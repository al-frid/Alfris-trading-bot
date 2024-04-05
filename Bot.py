from pyrogram import Client,filters  
from unittest import result         
from pyrogram.types import ChatPermissions
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup , ReplyKeyboardMarkup
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import time
import sqlite3


# Initialize the Pyrogram client
bot = Client(
    "Alfris Bot",
    api_id=27980026,
    api_hash="70d4e95314dbde5348c86042dc9f271d",
    bot_token="6727072066:AAHVm45ozarWaSYrz2WRkq8K-w6MV8LDZwE"
)



# # Connect to SQLite database
# conn = sqlite3.connect('user_history.db')
# cursor = conn.cursor()

# # Create table to store user history if not exists
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS user_history (
#         user_id INTEGER,
#         message TEXT,
#         timestamp TEXT
#     )
# ''')
# conn.commit()

# # Function to save user history to the database
# def save_user_history(user_id, message, timestamp):
#     # Connect to SQLite database
#     conn = sqlite3.connect('user_history.db')
#     cursor = conn.cursor()
    
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS user_history (
#             user_id INTEGER,
#             message TEXT,
#             timestamp TEXT
#         )
#     ''')
#     cursor.execute('''
#         INSERT INTO user_history (user_id, message, timestamp)
#         VALUES (?, ?, ?)
#     ''', (user_id, message, timestamp))
#     conn.commit()
#     conn.close()


# Inline Keyboard
START_MESSAGE = "Please select an action"
START_MESSAGE_BUTTONS = [
    [InlineKeyboardButton("AutoTrade", callback_data="autotrade"),
     InlineKeyboardButton("Generate Signal", callback_data="generatesignal")],
    [InlineKeyboardButton("Candlestick chart", url='http://192.168.8.116:8080')]
]

REPLY_MESSAGE = "Choose your currency pair"
Currency_Pair_Buttons = [
    ["EURUSD", "USDJPY", "GBPUSD", "AUDUSD", "NZDUSD"],
    ["USDCAD", "USDCHF", "EURGBP", "EURJPY", "EURCHF"]
]

# Alfris action when the user interacts
@bot.on_message(filters.command('start') & filters.private)
def start_command_handler(client, message):
    text = START_MESSAGE
    reply_markup = InlineKeyboardMarkup(START_MESSAGE_BUTTONS)
    client.send_message(message.chat.id, text=text, reply_markup=reply_markup, disable_web_page_preview=True)

# # Command to handle echo and save user history
# @bot.on_message(filters.command('start') & filters.private)
# def echo_and_save(client, message):
#     save_user_history(message.from_user.id, message.text, message.date)
#     message.reply_text("Your message has been saved.")

# Function to get exposure
def get_exposure(symbol):
    position = mt5.positions_get(symbol=symbol)
    if position:
        pos_df = pd.DataFrame(position, columns=position[0]._asdict().keys())
        exposure = pos_df['volume'].sum()
        return exposure

# Function to look for trading signals
def signal(symbol, timeframe, sma_period):
    bars = mt5.copy_rates_from_pos(symbol, timeframe, 1, sma_period)
    bars_df = pd.DataFrame(bars)

    last_close = bars_df.iloc[-1].close
    sma = bars_df.close.mean()

    direction = 'flat'
    if last_close > sma:
        direction = 'buy'
    elif last_close < sma:
        direction = 'sell'

    return last_close, sma, direction

mt5.initialize()

# Alfris action when the user selects "Generate Signal"
@bot.on_callback_query(filters.regex("generatesignal"))
def generatesignal_callback_handler(client, callback_query):
    chat_id = callback_query.message.chat.id

    text = REPLY_MESSAGE
    reply_markup = ReplyKeyboardMarkup(Currency_Pair_Buttons, one_time_keyboard=True, resize_keyboard=True)
    client.send_message(chat_id, text=text, reply_markup=reply_markup)

    # Nested handler for currency pair selection
    @client.on_message(filters.text & filters.private)
    def handle_currency_pair(client, message):
        global SYMBOL
        
        # Assign the selected currency pair to SYMBOL
        SYMBOL = message.text.upper()  # Convert to uppercase to ensure consistency
        
        # Notify the user about the selected currency pair
        client.send_message(chat_id, f"Selected currency pair: {SYMBOL}")

        # Proceed with generating the signal using the selected currency pair
        VOLUME = 1.0
        TIMEFRAME = mt5.TIMEFRAME_M1
        SMA_PERIOD = 10
        DEVIATION = 20

        # Calculate exposure, signal, and other necessary data using the selected currency pair (SYMBOL)
        exposure = get_exposure(SYMBOL)
        last_close, sma, direction = signal(SYMBOL, TIMEFRAME, SMA_PERIOD)

        # Format the message with each piece of information on a new line
        message_text = f"Time: {datetime.now()}\n" \
                       f"Current Trades: {exposure}\n" \
                       f"Last Close: {last_close}\n" \
                       f"Simple Moving Average: {sma}\n" \
                       f"Signal: {direction}"

        # Send the message to the user
        client.send_message(chat_id, message_text)


# Alfris action when the user selects "AutoTrade"
@bot.on_callback_query(filters.regex("autotrade"))
def autotrade_callback_handler(client, callback_query):
    
    
    chat_id = callback_query.message.chat.id
    text = "AutoTrade started. Press /close to stop."
    buttons = [
        [InlineKeyboardButton("Generate Signal", callback_data="generatesignal"),
         InlineKeyboardButton("Candlestick chart", url='http://192.168.8.116:8080')]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    client.send_message(chat_id, text=text, reply_markup=reply_markup)

    class Alfris:
        def __init__(self):
            mt5.initialize()
            # self.login = 
            # self.password = ''
            # self.server = ''
            # mt5.login(self.login, self.password, self.server)
            self.SYMBOL = 'CADJPY'
            self.Atr_Perc_tp = 1.5 
            self.Atr_Perc_sl = 2.2 
            self.TIMEFRAME_15M = mt5.TIMEFRAME_M15
            self.TIMEFRAME_5M = mt5.TIMEFRAME_M5
            self.TIMEFRAME_1H = mt5.TIMEFRAME_H1
            self.VOLUME = 0.01
            self.MAGIC = 2022
            self.Comment = 'Alfris'
            self.sec_to_shift = 14400 # depend of the local time, check the timestamp of mt5 and in your machine to match.
            self.symbol_list = ['AUDUSD', 'CHFJPY', 'EURUSD', 'GBPUSD', 'USDCAD', 'USDCHF',
                                'USDJPY', 'EURCAD', 'GBPJPY', 'AUDCHF', 'AUDCAD', 'AUDJPY',
                                'EURGBP', 'EURAUD', 'EURJPY', 'EURCHF', 'EURNZD', 'AUDNZD',
                                'GBPCHF', 'USDSGD', 'CADCHF', 'CADJPY', 'GBPAUD', 'GBPCAD',
                                'GBPNZD', 'NZDCAD', 'NZDCHF', 'NZDUSD', 'NZDJPY'] # 29


        ''' H I S T O R I C A L   D A T A '''

        # GET DATA (on)
        def Historical(self):
            # Get data from now to back by the numbers of candles
            number_of_candles = 400
            looknow = int(datetime.utcnow().timestamp())
            lookback = (looknow - (number_of_candles * 5)*60) # in sec
            df = pd.DataFrame(mt5.copy_rates_range(self.SYMBOL,self.TIMEFRAME_5M, lookback + self.sec_to_shift, looknow + self.sec_to_shift))

            # Create dataframe
            df = df.drop(['spread','real_volume'],axis=1) 
            df = df[['time','open','high','low','close','tick_volume']]
            df['time']=pd.to_datetime(df['time'], unit='s')
            df.reset_index()
            df = df.dropna()

            # pd.set_option('display.max_columns', None)
            # print(df.tail(30))
            return df


        ''' C A N D L E   P A T T E R N '''

        # BULLISH ENGULFING (off)
        def Bull_Eng(self, SYMBOL):
            self.SYMBOL = SYMBOL
            df = self.Historical()
            Bullish_Engulfing = df['close'].iloc[-2] > df['open'].iloc[-3] and df['open'].iloc[-2] <= df['close'].iloc[-3] and (0.8 * 0.9) > 0.8 and \
                                df['close'].iloc[-3] < df['open'].iloc[-3] and df['close'].iloc[-2] > df['open'].iloc[-2] and df['high'].iloc[-2] > df['high'].iloc[-3]
            
            return Bullish_Engulfing
        
        # BEARISH ENGULFING (off)
        def Bear_Eng(self, SYMBOL):
            self.SYMBOL = SYMBOL
            df = self.Historical()
            Bearish_Engulfing = df['close'].iloc[-2] < df['open'].iloc[-3] and df['open'].iloc[-2] >= df['close'].iloc[-3] and (0.8 * 0.9) < 0.8 and \
                                df['close'].iloc[-3] > df['open'].iloc[-3] and df['close'].iloc[-2] < df['open'].iloc[-2] and df['low'].iloc[-2] < df['low'].iloc[-3]       

            return Bearish_Engulfing


        ''' I N D I C A T O R S '''

        # Avarage True Range (on)
        def ATR(self):
            df = self.Historical()
            # ATR
            prev_close = df.close.shift(1)
            true_range_1 = df.high - df.low
            true_range_2 = abs(df.high - prev_close)
            true_range_3 = abs(prev_close - df.low)
            tr = pd.DataFrame({'Tr_1':true_range_1, 'Tr_2':true_range_2, 'Tr_3':true_range_3}).max(axis=1)
            df['ATR'] = tr.rolling(window=6).mean()

            # Take Profit and Stop Loss for Long position
            SL_buy = df['close'].iloc[-2] - (df['ATR'].iloc[-2] * self.Atr_Perc_sl)
            TP_buy = df['close'].iloc[-2] + (df['ATR'].iloc[-2] * self.Atr_Perc_tp)

            # Take Profit and Stop Loss for Short position
            TP_sell = df['close'].iloc[-2] - (df['ATR'].iloc[-2] * self.Atr_Perc_tp)
            SL_sell = df['close'].iloc[-2] + (df['ATR'].iloc[-2] * self.Atr_Perc_sl)

            return ([TP_buy, SL_buy, TP_sell, SL_sell])

        # Relatve Strenght Index (on)
        def RSI(self, SYMBOL):
            self.SYMBOL = SYMBOL
            df = self.Historical()
            # CALCULATE RSI
            alpha = 1.0 / 14
            gains = df.close.diff()
            wins = pd.Series([x if x >= 0 else 0.0 for x in gains], name='wins')
            losses = pd.Series([x * -1 if x < 0 else 0.0 for x in gains], name='losses')
            wins_rma = wins.ewm(min_periods=14, alpha=alpha).mean()
            losses_rma = losses.ewm(min_periods=14, alpha=alpha).mean()
            rs = wins_rma / losses_rma
            rs = wins_rma / losses_rma
            df['RSI'] = 100.0 - (100.0 / (1.0 + rs))

            # Return what needed
            RSI_mean_1 = df['RSI'].iloc[-2:-1].mean()
            RSI_mean_2 = df['RSI'].iloc[-3:-2].mean()
            RSI_mean_3 = df['RSI'].iloc[-4:-2].mean()

            return ([RSI_mean_1, RSI_mean_2, RSI_mean_3])
        
        # SUPPLY & DEMAND using VOLUME (off)
        def Supply_Demand_by_volume(self, SYMBOL):
            self.SYMBOL = SYMBOL
            df = self.Historical()
            # Create a new column 'range' by subtracting the 'low' column from the 'high' column.
            df["range"] = df["high"] - df["low"]
            # Create a new column 'vwap' by taking the cumulative sum of the product of the 'close' and 'tick_volume' columns divided by the cumulative sum of the 'tick_volume' column.
            df["vwap"] = (df["close"] * df["tick_volume"]).cumsum() / df["tick_volume"].cumsum()
            
            # Roll them in other to understand the footprints left by the traders and so the supply and demand zones.
            df['RollRange'] = df["range"].rolling(window=50).mean()
            df["RollVwap"] = df["vwap"].rolling(window=50).mean()

            # is supply if last closed candle:
            Supply = df['range'].iloc[-2] < df['RollRange'].iloc[-2] and df['vwap'].iloc[-2] > df['RollVwap'].iloc[-2]
            # is demand if last closed candle:
            Demand = df['range'].iloc[-2] < df['RollRange'].iloc[-2] and df['vwap'].iloc[-2] < df['RollVwap'].iloc[-2]

            # check supply and demand zones not by only the last candle but by zones
            supply_len_50 = df[(df["range"] < df["range"].rolling(window=50).mean()) & (df["vwap"] > df["vwap"].rolling(window=50).mean())]
            demand_len_50 = df[(df["range"] < df["range"].rolling(window=50).mean()) & (df["vwap"] < df["vwap"].rolling(window=50).mean())]

            # return the length of the zones, of one is grater than teh other, is that zone.
            # ex: 
            # 'Buy' if len(supply_len_50) > len(demand_len_50) else 'Sell' if len(demand_len_50) > len(supply_len_50)
            return len(supply_len_50), len(demand_len_50)

        # SUPPLY & DEMAND using HIGHS and LOWS (on)
        def Supply_Demand_by_candles(self, SYMBOL, Window):
            self.SYMBOL = SYMBOL
            df = self.Historical()
            # Get the Higher High and the Lower Low 
            df["high_rolling_max"] = df["high"].rolling(window=Window).max()
            df["low_rolling_min"] = df["low"].rolling(window=Window).min()
            # Create a column to store the supply and demand zones
            df["supply_demand"] = None
            
            # Loop and define wheather is a Supply or Demand zone
            for i, row in df.iterrows():
                if row["high"] >= row["high_rolling_max"]:
                    df.loc[i, "supply_demand"] = "Supply"
                elif row["low"] <= row["low_rolling_min"]:
                    df.loc[i, "supply_demand"] = "Demand"
            
            return df

        # LIQUIDITY POOL (on)
        def Liquidity_pool(self):
            df = self.Historical()

            df['Liquidity'] = (df['close'] * df['tick_volume']) / df['tick_volume'].rolling(window=30).sum()
            # Get teh liquidity of teh last closed candle
            Liquidity_last = df['Liquidity'].iloc[-2]
            # Get the max liquidity of the last 26 cnandles
            Liquidity_max_26_period = df['Liquidity'].iloc[-26:].max()
            # Get the max liquidity of the last 50 cnandles
            Liquidity_max_50_period = df['Liquidity'].iloc[-50:].max()
            # Get the max liquidity of the last 80 cnandles
            Liquidity_max_80_period = df['Liquidity'].iloc[-80:].max()
            # Get the full row of the df where the liquidity is max
            max_liquidity_row = df.loc[df['Liquidity'].iloc[-20:].idxmax()]
            # Get the close and then the open of the above line
            Liquidity_Row = max_liquidity_row['close']
            Liquidity_Row_open = max_liquidity_row['open']

            # Check if where the candle with large liquidity is a bull or bear
            Liquidity_direction_bull = Liquidity_Row > Liquidity_Row_open
            Liquidity_direction_bear = Liquidity_Row < Liquidity_Row_open

            # Return just what needed for this strategy
            return Liquidity_Row


        ''' P O S I T I O N   M A N A G E R '''

        # OPEN MARKET POSITION (on)
        def open_market_position(self, s_l, Volume):
            # sell 1 == ask
            # buy 0 == bid

            TP_Buy = self.ATR()[0] #.astype(float)
            SL_Buy = self.ATR()[1] #.astype(float)
            TP_Sell = self.ATR()[2] #.astype(float)
            SL_Sell = self.ATR()[3] #.astype(float)

            if (s_l == 1):
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": self.SYMBOL,
                    "volume": Volume, # FLOAT
                    "type": mt5.ORDER_TYPE_BUY,
                    "price": mt5.symbol_info_tick(self.SYMBOL).bid,
                    "sl": SL_Buy, # FLOAT
                    "tp": TP_Buy, # FLOAT
                    "deviation": 20, # INTERGER
                    "magic": self.MAGIC,
                    "comment": self.Comment,
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,}

                response = mt5.order_send(request)
                return response

            if (s_l == -1):
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": self.SYMBOL,
                    "volume": Volume, # FLOAT
                    "type": mt5.ORDER_TYPE_SELL,
                    "price": mt5.symbol_info_tick(self.SYMBOL).ask,
                    "sl": SL_Sell, # FLOAT
                    "tp": TP_Sell, # FLOAT
                    "deviation": 20, # INTERGER
                    "magic": self.MAGIC,
                    "comment": self.Comment,
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,}

                response = mt5.order_send(request)
                return response

        # OPEN LIMIT POSITION (off)
        def open_limit_position(self, s_l):
            # sell 1 == ask
            # buy 0 == bid

            TP_Buy = self.MINUTE()[8] #.astype(float)
            SL_Buy = self.MINUTE()[9] #.astype(float)
            TP_Sell = self.MINUTE()[10] #.astype(float)
            SL_Sell = self.MINUTE()[11] #.astype(float)

            if (s_l == 1):
                request = {
                    "action": mt5.TRADE_ACTION_PENDING,
                    "symbol": self.SYMBOL,
                    "volume": self.VOLUME, # FLOAT
                    "type": mt5.ORDER_TYPE_BUY_LIMIT,
                    "price": mt5.symbol_info_tick(self.SYMBOL).ask - 10 * point,
                    "sl": SL_Buy, # FLOAT
                    "tp": TP_Buy, # FLOAT
                    "deviation": 20, # INTERGER
                    "magic": self.MAGIC, # INTERGER
                    "comment": self.Comment,
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_RETURN}

                response = mt5.order_send(request)
                return response

            if (s_l == -1):
                request = {
                    "action": mt5.TRADE_ACTION_PENDING,
                    "symbol": self.SYMBOL,
                    "volume": self.VOLUME, # FLOAT
                    "type": mt5.ORDER_TYPE_SELL_LIMIT,
                    "price": mt5.symbol_info_tick(self.SYMBOL).bid + 10 * point,
                    "sl": SL_Sell, # FLOAT
                    "tp": TP_Sell, # FLOAT
                    "deviation": 20, # INTERGER
                    "magic": self.MAGIC, # INTERGER
                    "comment": self.Comment,
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_RETURN}

                response = mt5.order_send(request)
                return response

        # CLOSE MARKET POSITION (on)
        def close_position(self, s_l):
            # mt5.positions_get()[0][0]
            
            if (s_l == 1):
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": self.SYMBOL,
                    "volume": self.VOLUME, # FLOAT
                    "type": mt5.ORDER_TYPE_BUY,
                    "position": mt5.positions_get(symbol=self.SYMBOL)[0][0],
                    "price": mt5.symbol_info_tick(self.SYMBOL).bid,
                    "sl": 0.0, # FLOAT
                    "tp": 0.0, # FLOAT
                    "deviation": 20, # INTERGER
                    "magic": self.MAGIC,
                    "comment": self.Comment,
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,}

                response = mt5.order_send(request)
                return response

            if (s_l == -1):
                request = {
                    "action": mt5.TRADE_ACTION_DEAL,
                    "symbol": self.SYMBOL,
                    "volume": self.VOLUME, # FLOAT
                    "type": mt5.ORDER_TYPE_SELL,
                    "position": mt5.positions_get(symbol=self.SYMBOL)[0][0],
                    "price": mt5.symbol_info_tick(self.SYMBOL).ask,
                    "sl": 0.0, # FLOAT
                    "tp": 0.0, # FLOAT
                    "deviation": 20, # INTERGER
                    "magic": self.MAGIC,
                    "comment": self.Comment,
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC,}

                response = mt5.order_send(request)
                # print(response)
                return response

        # CLOSE ALL POSITIONS (on)
        def close_all_positions(self, SYMBOL, pos):
            self.SYMBOL = SYMBOL
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "position": pos.ticket,
                "symbol": self.SYMBOL,
                "volume": pos.volume, # FLOAT
                "type": mt5.ORDER_TYPE_BUY if pos.type == 1 else mt5.ORDER_TYPE_SELL,
                "price": mt5.symbol_info_tick(self.SYMBOL).ask if pos.type == 1 else mt5.symbol_info_tick(self.SYMBOL).bid,
                "deviation": 20, # INTERGER
                "magic": self.MAGIC, # INTERGER
                "comment": self.Comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,}
            
            # To close all positions for all symbols, run the following outside this function:
            # for SYMBOL in self.symbol_list:
            #     Opened = mt5.positions_get(symbol = SYMBOL)
            #     for pos in Opened:
            #         self.close_all_positions(SYMBOL, pos)

            response = mt5.order_send(request)
            return response

        # CLOSE ALL LIMIT POSITON PENDING (off)
        def close_all_pendings(self, pos):
            request = {
                "action": mt5.TRADE_ACTION_REMOVE,
                "order": pos.ticket if pos != () else None,
                "symbol": self.SYMBOL,
                "type_filling": mt5.ORDER_FILLING_IOC,}
            
            # To close all pending positions for all symbols, run the following outside this function:
            # for SYMBOL in self.symbol_list:
            #     Pending = Pending = mt5.orders_get(symbol= SYMBOL)
            #     for pos in Pending:
            #         self.close_all_positions(SYMBOL, pos)

            response = mt5.order_send(request)
            return response
        
        # GET POSITION CURRENTLY OPEN (on)
        def get_opened_positions(self, SYMBOL):
            self.SYMBOL = SYMBOL

            if len(mt5.positions_get(symbol = self.SYMBOL)) == 0:
                return ''

            # 0 == buy, 1 == sell
            elif len(mt5.positions_get(symbol = self.SYMBOL)) > 0:
                positions = pd.DataFrame(mt5.positions_get(symbol = self.SYMBOL)[0])
                side = positions[0][5] # type, buy or sell, 0 or 1
                entryprice = positions[0][10]
                profit = positions[0][15]
                ticket_ID = positions[0][0] # ID positon
                    
                if side == 0:
                    pos = 1
                    return [pos,profit,entryprice, ticket_ID]

                elif side == 1:
                    pos = -1

                    return ([pos, side, profit, entryprice, ticket_ID])
                
                else:
                    return 'NONE'
            else:
                return 'NONE'

        # GET BID AND ASK LAST CANDLE (off)
        def get_SYMBOL_price_last(self):
            prices = mt5.symbol_info_tick(self.SYMBOL)._asdict()
            df = pd.DataFrame([prices], index=[0])
            bid = df.at[0,'bid']
            ask = df.at[0,'ask']
            return [bid, ask]


        ''' C H E C K   S I G N A L S '''

        # CHECK SIGNAL TO OPEN POSITION (on)
        def check_signal(self, SYMBOL):
            self.SYMBOL = SYMBOL
            SIGNAL = 0
            
            df = self.Historical()

            Supply_Demand_20 = self.Supply_Demand_by_candles(SYMBOL, 20)
            Supply_Demand_50 = self.Supply_Demand_by_candles(SYMBOL, 50)
            Liquidity = self.Liquidity_pool()

            Close = df['close'] # any
            Open = df['open'] # any

            # Define th edirection of the last closed candle
            BULL_2 = Close.iloc[-2] > Open.iloc[-2]
            BEAR_2 = Close.iloc[-2] < Open.iloc[-2]

            # It opnes the position a little bit far from where the signal has bee cathed
            point = mt5.symbol_info(self.SYMBOL).point 
            margin_buy = Close.iloc[-2] - 10 * point
            margin_sell =  Close.iloc[-2] + 10 * point

            # L O N G 
            if Supply_Demand_50['supply_demand'].iloc[-3] == 'Demand' and Supply_Demand_20['supply_demand'].iloc[-3] == 'Demand':
                if BULL_2 == True and Supply_Demand_20['supply_demand'].iloc[-2] != 'Demand' and Liquidity == Close.iloc[-3]:
                    SIGNAL = 1

            # S H O R T
            elif Supply_Demand_50['supply_demand'].iloc[-3] == 'Supply' and Supply_Demand_20['supply_demand'].iloc[-3] == 'Supply':
                if BEAR_2 == True and Supply_Demand_20['supply_demand'].iloc[-2] != 'Supply' and Liquidity == Close.iloc[-3]:
                    SIGNAL = -1

            return SIGNAL

        # CHECK A PARTIAL SIGNAL AND CLOSE THE POSITION IF True (on)
        def check_reverse_signal(self, SYMBOL):
            self.SYMBOL = SYMBOL
            SIGNAL = 0

            Supply_Demand_50 = self.Supply_Demand_by_candles(SYMBOL, 50)
            Supply_Demand_20 = self.Supply_Demand_by_candles(SYMBOL, 20)

            # L O N G 
            if Supply_Demand_50['supply_demand'].iloc[-2] == 'Demand' and Supply_Demand_20['supply_demand'].iloc[-2] == 'Demand':
                # print(f'BUY reverse {SYMBOL}')
                SIGNAL = 1

            # S H O R T
            elif Supply_Demand_50['supply_demand'].iloc[-2] == 'Supply' and Supply_Demand_20['supply_demand'].iloc[-2] == 'Supply':
                # print(f'SELL reverse {SYMBOL}')
                SIGNAL = -1

            return SIGNAL


        ''' P R O F I T   &   S T O P   L O S S E S '''

        # CHECK THE CURRENT PROFIT (off)
        def Profit_F(self, SYMBOL):
            self.SYMBOL = SYMBOL
            Openedd = mt5.positions_get(symbol = self.SYMBOL)
            tot_profit = 0
            Positions_Opened = [ pos for pos in Openedd ]
            for pos in Positions_Opened:
                tot_profit += pos.profit
            return round(tot_profit, 2)

        # REMOVE ALL STOP LOSS (on)
        def remove_sl(self, SYMBOL, pos):
            self.SYMBOL = SYMBOL
            Openedd = mt5.positions_get(symbol = SYMBOL)
            Positions_Opened = [ pos for pos in Openedd ]
            for pos in Openedd:
                # print(pos.ticket)
                request = {
                    "action": mt5.TRADE_ACTION_SLTP,
                    "symbol": self.SYMBOL,
                    "position": pos.ticket,
                    "sl": 0.0 if pos.sl > 0.0 or pos.sl != "" else None,
                    "tp": pos.tp}

                response = mt5.order_send(request)
                return response

        # ADD ALL STOP LOSS (on)
        def add_sl(self, SYMBOL, pos):
            SL_Buy = self.ATR()[1] #.astype(float)
            SL_Sell = self.ATR()[3] #.astype(float)
            self.SYMBOL = SYMBOL
            Openedd = mt5.positions_get(symbol = SYMBOL)
            Positions_Opened = [ pos for pos in Openedd ]
            for pos in Openedd:
                # print(pos.ticket)
                request = {
                    "action": mt5.TRADE_ACTION_SLTP,
                    "symbol": self.SYMBOL,
                    "position": pos.ticket,
                    "sl": SL_Sell if pos.type == 1 else SL_Buy,
                    "tp": pos.tp}

                response = mt5.order_send(request)
                return response


        ''' E X E C U T I O N '''

        # BUY or SELL (on)
        def main(self, step):

            for SYMBOL in self.symbol_list:
                # ------- close all ------- #
                CLOSE_ALL = False # switch to True for execute
                if CLOSE_ALL == True:
                    Opened = mt5.positions_get(symbol = SYMBOL)
                    for pos in Opened:
                        self.close_all_positions(SYMBOL, pos)
                # ------- close all ------- #

                POSITIONS = self.get_opened_positions(SYMBOL)
                Openedd = mt5.positions_get(symbol = SYMBOL)
                Pendingg = mt5.orders_get(symbol= SYMBOL)

                Tot_Profit = self.Profit_F(SYMBOL)
                Tot_Len = len(Pendingg) + len(Openedd)
                signal_reverse = self.check_reverse_signal(SYMBOL)
                signal = self.check_signal(SYMBOL)

                if CLOSE_ALL == False:
                    # LOOKING FOR PATTERN
                    if POSITIONS == '' and len(Openedd) < 1:
                        try:
                            if signal == 1:
                                self.open_market_position(1, self.VOLUME)
                                client.send_message(chat_id, f'1L1 - Long Opened {SYMBOL}')
                                print(f'1L1 - Long Opened {SYMBOL}')
                            
                            elif signal == -1:
                                self.open_market_position(-1, self.VOLUME)
                                client.send_message(chat_id, f'1S1 - Short Opened {SYMBOL}')
                                print(f'1S1 - Short Opened {SYMBOL}')
                        except:
                            client.send_message(chat_id, f'Could not open nuew pos')
                            print('Could not open nuew pos')
                        
        # CLOSE POSITION (on)
        def main_close(self):
            for SYMBOL in self.symbol_list:
                POSITIONS = self.get_opened_positions(SYMBOL)
                signal_reverse = self.check_reverse_signal(SYMBOL)

                if POSITIONS != '':
                    try:
                        
                        if POSITIONS[0] == 1: # if side is Buy
                            if signal_reverse == -1:
                                self.close_position(-1)
                                client.send_message(chat_id, f'3L2 - Close Long {SYMBOL} due reverse Signal') 
                                print(f'3L2 - Close Long {SYMBOL} due reverse Signal')
                        
                        elif POSITIONS[0] == -1: # if side id Sell
                            if signal_reverse == 1:
                                self.close_position(1) 
                                #Bot Reply
                                client.send_message(chat_id, f'3L2 - Close Short {SYMBOL} due reverse Signal')
                                print(f'3L2 - Close Short {SYMBOL} due reverse Signal')

                    except:
                        #Bot reply
                        client.send_message(chat_id, f'Could not close a poaition {SYMBOL}')
                        print(f'Could not close a poaition {SYMBOL}')

        # EXECUTE MAIN - BUY or SELL (on)
        def execution_main(self):
            import datetime

            # The broker cause massive spread during the closing and open time of the market and
            # this more often burn all the stop losses of the position if using timeframe of 10min or less.
            # To avoid this, just before the market close, stop searching for signals and remove all the stop losses.
            # After about 1 hour from the open when the spread came to normal re-add the stop losses and start searching for signal.

            current_time = datetime.datetime.now().time()

            # remove all stop loss 
            if current_time > datetime.time(21, 35) and current_time <= datetime.time(22, 0):
                for S in self.symbol_list:
                    for pos in S:
                        self.remove_sl(S, pos)

            # add all stop loss
            elif current_time > datetime.time(23, 11) and current_time <= datetime.time(23, 5):
                for S in self.symbol_list:
                    for pos in S:
                        self.add_sl(S, pos)

            # execute
            else:
                counterr = 1
                # Bot Reply
                client.send_message(chat_id, f'Looking for pattern in {self.symbol_list}...')
                print(f'Looking for pattern in {self.symbol_list}...')
                while True:
                    # stop executing until:
                    if current_time > datetime.time(21, 40) or current_time <= datetime.time(23, 12):
                        try:
                            self.main(counterr), self.main_close()
                            counterr = counterr + 1
                            if counterr > 5:
                                counterr = 1
                            time.sleep(28)
                            
                        except KeyboardInterrupt:
                            client.send_message(chat_id, f"KeyboardInterrupt. Stopping.")
                            print('\n\KeyboardInterrupt. Stopping.')
                            exit()
                    else:
                        client.send_message(chat_id, f'Starting again at 23:35')
                        print('Starting again at 23:35')
                        time.sleep(180)
                        continue



    if __name__ == '__main__':
        Trade = Alfris()
        Trade.execution_main()


def shutdown_mt5():
    # Check if MT5 is initialized
    if mt5.initialize():
        # Log out from the account
        mt5.shutdown()
        print("Logged out from MetaTrader 5 account.")

    # Deinitialize the MT5 library
    mt5.shutdown()
    print("MetaTrader 5 library deinitialized.")

# Command handler for /close command
@bot.on_message(filters.command(["close"]) & filters.private)
def close_command_handler(client, message):
    # Check if the MT5 connection is initialized
    if mt5.initialize():
        # Shutdown the MT5 connection
        shutdown_mt5()
        # Send a message to the user indicating successful shutdown
        client.send_message(message.chat.id, "MetaTrader 5 connection has been closed.")
    else:
        # Send a message to the user indicating that MT5 is not initialized
        client.send_message(message.chat.id, "MetaTrader 5 connection is not initialized.")


#~~~~~~~ FEEDBACK ~~~~~~~~~~
# Connect to SQLite database
conn = sqlite3.connect('feedback.db')
c = conn.cursor()

# Create feedback table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS feedback (
             id INTEGER PRIMARY KEY,
             user_id INTEGER,
             text TEXT,
             timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
conn.commit()

import aiosqlite

# Define a coroutine to save feedback to the database
async def save_feedback(user_id, feedback_text):
    async with aiosqlite.connect('feedback.db') as conn:
        await conn.execute("INSERT INTO feedback (user_id, text) VALUES (?, ?)", (user_id, feedback_text))
        await conn.commit()

# Handle feedback command
@bot.on_message(filters.command("feedback"))
async def feedback_command(client, message):
    # Open the database connection
    async with aiosqlite.connect('feedback.db') as conn:
        user_id = message.from_user.id
        feedback_text = " ".join(message.command[1:])  # Extract the feedback text from the command

        # Save feedback to the database
        await save_feedback(user_id, feedback_text)
        
    # Reply to the user
    await message.reply_text("Thank you for your feedback!")



@bot.on_message(filters.command(["showfeedback"]) & filters.private)
async def showfeedback_command_handler(client, message):
    # Connect to SQLite database
    conn = sqlite3.connect('feedback.db')
    c = conn.cursor()

    # Fetch all feedback from the database
    c.execute("SELECT * FROM feedback")
    feedback_rows = c.fetchall()

    # Display the feedback
    for row in feedback_rows:
        await client.send_message(message.chat.id, f"Text: {row[2]}, Timestamp: {row[3]}") 

        print(f"ID: {row[0]}, User ID: {row[1]}, Text: {row[2]}, Timestamp: {row[3]}")

    # Close the database connection
    conn.close()

# ~~~~~~~ Indicates that Alfris is live ~~~~~~~~
print("Alfris Running")
bot.run()
