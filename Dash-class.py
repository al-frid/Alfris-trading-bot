from dash import Dash, html, dcc, Output, Input, State
import dash_bootstrap_components as dbc 
import pandas as pd 
import plotly.graph_objects as go
import MetaTrader5 as mt5 
# from mt5_funcs import get_symbol_names, TIMEFRAMES, TIMEFRAME_DICT

TIMEFRAMES = ['M1', 'M5', 'M15', 'M30', "H1", 'H4', 'D1', 'W1','MN1']
TIMEFRAME_DICT = {
    'M1': mt5.TIMEFRAME_M1,
    'M5': mt5.TIMEFRAME_M5,
    'M15': mt5.TIMEFRAME_M15,
    'M30': mt5.TIMEFRAME_M30,
    'H1': mt5.TIMEFRAME_H1,
    'H4': mt5.TIMEFRAME_H4,
    'D1': mt5.TIMEFRAME_D1,
    'W1': mt5.TIMEFRAME_W1,
    'MN1': mt5.TIMEFRAME_MN1,
}

def get_symbol_names():
    mt5.initialize()

    symbols = mt5.symbols_get()
    symbols_df = pd.DataFrame(symbols, columns=symbols[0]._asdict().keys())

    symbol_names = symbols_df['name'].tolist()
    return symbol_names

class RealTimeChartsApp:
    def __init__(self):
        self.app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        self.setup_layout()
        self.register_callbacks()

    def setup_layout(self):
        self.symbol_dropdown = html.Div([
            html.P('Symbol:'),
            dcc.Dropdown(
                id='symbol-dropdown',
                options=[{'label': symbol, 'value': symbol} for symbol in get_symbol_names()],
                value='EURUSD'
            )
        ])

        self.timeframe_dropdown = html.Div([
            html.P('Timeframe:'),
            dcc.Dropdown(
                id='timeframe-dropdown',
                options=[{'label': timeframe, 'value': timeframe} for timeframe in TIMEFRAMES],
                value='D1'
            )
        ])

        self.num_bars_input = html.Div([
            html.P('Number of Candles'),
            dbc.Input(id='num-bar-input', type='number', value='20')
        ])

        self.app.layout = html.Div([
            html.H1('Real Time Charts'),

            dbc.Row([
                dbc.Col(self.symbol_dropdown),
                dbc.Col(self.timeframe_dropdown),
                dbc.Col(self.num_bars_input)
            ]),

            html.Hr(),

            dcc.Interval(id='update', interval=200),

            html.Div(id='page-content')

        ], style={'margin-left': '5%', 'margin-right': '5%', 'margin-top': '20px'})

    def register_callbacks(self):
        @self.app.callback(
            Output('page-content', 'children'),
            Input('update', 'n_intervals'),
            State('symbol-dropdown', 'value'),
            State('timeframe-dropdown', 'value'),
            State('num-bar-input', 'value')
        )
        def update_ohlc_chart(interval, symbol, timeframe, num_bars):
            timeframe_str = timeframe
            timeframe = TIMEFRAME_DICT[timeframe]
            num_bars = int(num_bars)

            print(symbol, timeframe, num_bars)

            bars = mt5.copy_rates_from_pos(symbol, timeframe, 0, num_bars)
            df = pd.DataFrame(bars)
            df['time'] = pd.to_datetime(df['time'], unit='s')

            fig = go.Figure(data=go.Candlestick(x=df['time'],
                                                open=df['open'],
                                                high=df['high'],
                                                low=df['low'],
                                                close=df['close']))
            
            fig.update(layout_xaxis_rangeslider_visible=False)
            fig.update_layout(yaxis={'side':'right'})
            fig.layout.xaxis.fixedrange = True
            fig.layout.yaxis.fixedrange = True

            return [
                html.H2(id='chart-details', children=f'{symbol} - {timeframe_str}'),
                dcc.Graph(figure=fig, config={'displayModeBar': False})
            ]

    def run(self, host='127.0.0.1', port=8080):
        self.app.run_server(host=host, port=port)

if __name__ == '__main__':
    app = RealTimeChartsApp()
    app.run(host='0.0.0.0')  # Use 0.0.0.0 to listen on all available network interfaces

