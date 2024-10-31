# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 16:10:44 2024

@author: Iaina
"""

import yfinance as yf
import pandas as pd

def fetch_stock_data(ticker, period='1y', interval='1d'):
    """
    Fetch historical stock price data using yfinance.
    
    :param ticker: str - Stock ticker symbol (e.g., 'AAPL' for Apple)
    :param period: str - Time period for data ('1d', '1mo', '1y', etc.)
    :param interval: str - Interval between data points ('1d', '1wk', '1mo', etc.)
    :return: DataFrame - Stock data with open, close, high, low, adjusted close, and volume
    """
    stock = yf.Ticker(ticker)
    data = stock.history(period=period, interval=interval)
    return data

def calculate_moving_averages(data, short_window=50, long_window=200):
    """
    Calculate 50-day and 200-day moving averages for the stock data.
    
    :param data: DataFrame - Stock price data
    :param short_window: int - Short window for moving average (default 50)
    :param long_window: int - Long window for moving average (default 200)
    :return: DataFrame - Original data with added moving averages
    """
    data['MA50'] = data['Close'].rolling(window=short_window).mean()
    data['MA200'] = data['Close'].rolling(window=long_window).mean()
    return data

def calculate_price_change(data):
    """
    Calculate the percentage change in stock price over time.
    
    :param data: DataFrame - Stock price data
    :return: DataFrame - Data with added price change percentage
    """
    data['Price Change (%)'] = data['Close'].pct_change() * 100
    return data

def calculate_volatility(data):
    """
    Calculate stock price volatility based on the percentage change in stock price.
    
    :param data: DataFrame - Stock price data
    :return: float - Volatility (standard deviation of the price change percentage)
    """
    return data['Price Change (%)'].std()

def calculate_rsi(data, period=14):
    """
    Calculate the Relative Strength Index (RSI) for the stock data.
    
    :param data: DataFrame - Stock price data
    :param period: int - The number of days to calculate RSI (default: 14 days)
    :return: DataFrame - Data with added RSI column
    """
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    data['RSI'] = rsi
    return data

def process_stock_data(ticker):
    """
    Fetch stock data and calculate key metrics (moving averages, price change, RSI, volatility).
    
    :param ticker: str - Stock ticker symbol
    :return: DataFrame - Stock data with calculated metrics
    """
    # Step 1: Fetch stock data
    stock_data = fetch_stock_data(ticker)
    
    # Step 2: Calculate 50-day and 200-day moving averages
    stock_data = calculate_moving_averages(stock_data)
    
    # Step 3: Calculate price change percentage
    stock_data = calculate_price_change(stock_data)
    
    # Step 4: Calculate RSI (Relative Strength Index)
    stock_data = calculate_rsi(stock_data)
    
    # Step 5: Calculate volatility (standard deviation of price change)
    volatility = calculate_volatility(stock_data)
    
    # Display volatility
    print(f"Volatility for {ticker}: {volatility:.2f}%")
    
    return stock_data

if __name__ == "__main__":
    # Example usage: Fetch and process stock data for IBM
    ticker = 'IBM'
    stock_data = process_stock_data(ticker)
    
    # Show the first few rows of processed stock data
    print(stock_data[['Open', 'Close', 'MA50', 'MA200', 'Price Change (%)', 'RSI']].tail())

import yfinance as yf
import pandas as pd
import dash
from dash import dcc, html
import plotly.graph_objs as go
from dash.dependencies import Input, Output

# Fetch stock data
def fetch_stock_data(ticker, period='1y', interval='1d'):
    stock = yf.Ticker(ticker)
    data = stock.history(period=period, interval=interval)
    data['Price Change (%)'] = data['Close'].pct_change() * 100
    return data

# Calculate RSI
def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    data['RSI'] = rsi
    return data

# Moving averages
def calculate_moving_averages(data, short_window=50, long_window=200):
    data['MA50'] = data['Close'].rolling(window=short_window).mean()
    data['MA200'] = data['Close'].rolling(window=long_window).mean()
    return data

# Dashboard App Layout
app = dash.Dash(__name__)

app.layout = html.Div(style={'backgroundColor': '#003B73', 'padding': '20px'}, children=[
    html.H1('Stock Performance Dashboard', style={'textAlign': 'center', 'color': '#F0F8FF'}),

    dcc.Dropdown(
        id='stock-dropdown',
        options=[
            {'label': 'IBM', 'value': 'IBM'},
            {'label': 'Oracle', 'value': 'ORCL'},
            {'label': 'Microsoft', 'value': 'MSFT'},
            {'label': 'Google (Alphabet)', 'value': 'GOOGL'},
            {'label': 'Amazon', 'value': 'AMZN'}
        ],
        value='IBM',
        style={'color': '#000000'}
    ),
    
    dcc.Graph(id='stock-graph', style={'height': '600px'}),

    dcc.Graph(id='rsi-graph', style={'height': '300px'}),

    dcc.Graph(id='volatility-graph', style={'height': '300px'})
])

# Callbacks for updating graphs
@app.callback(
    [Output('stock-graph', 'figure'),
     Output('rsi-graph', 'figure'),
     Output('volatility-graph', 'figure')],
    [Input('stock-dropdown', 'value')]
)
def update_graphs(selected_ticker):
    df = fetch_stock_data(selected_ticker)
    df = calculate_rsi(df)
    df = calculate_moving_averages(df)

    # Stock Price Graph
    stock_trace = go.Scatter(
        x=df.index,
        y=df['Close'],
        mode='lines',
        name=f'{selected_ticker} Close Price',
        line=dict(color='#48A9A6')
    )

    ma50_trace = go.Scatter(
        x=df.index,
        y=df['MA50'],
        mode='lines',
        name='50-day MA',
        line=dict(color='#96C5F7')
    )

    ma200_trace = go.Scatter(
        x=df.index,
        y=df['MA200'],
        mode='lines',
        name='200-day MA',
        line=dict(color='#1B4F72')
    )

    stock_fig = go.Figure([stock_trace, ma50_trace, ma200_trace])
    stock_fig.update_layout(
        title=f'{selected_ticker} Stock Performance',
        xaxis_title='Date',
        yaxis_title='Price',
        plot_bgcolor='#011F4B',
        paper_bgcolor='#011F4B',
        font=dict(color='#F0F8FF')
    )

    # RSI Graph
    rsi_trace = go.Scatter(
        x=df.index,
        y=df['RSI'],
        mode='lines',
        name='RSI',
        line=dict(color='#1B98E0')
    )

    rsi_fig = go.Figure([rsi_trace])
    rsi_fig.update_layout(
        title=f'{selected_ticker} RSI (Relative Strength Index)',
        xaxis_title='Date',
        yaxis_title='RSI',
        plot_bgcolor='#03396C',
        paper_bgcolor='#03396C',
        font=dict(color='#F0F8FF')
    )

    # Volatility Graph
    volatility = df['Price Change (%)'].std()
    volatility_trace = go.Indicator(
        mode="gauge+number",
        value=volatility,
        title={'text': f'Volatility for {selected_ticker}'},
        gauge={'axis': {'range': [0, 10]}, 'bar': {'color': '#A2D5F2'}}
    )

    volatility_fig = go.Figure([volatility_trace])
    volatility_fig.update_layout(
        plot_bgcolor='#005B96',
        paper_bgcolor='#005B96',
        font=dict(color='#F0F8FF')
    )

    return stock_fig, rsi_fig, volatility_fig

if __name__ == '__main__':
    app.run_server(debug=True)

import dash
from dash import dcc, html
import plotly.graph_objs as go
import pandas as pd

# Sample Data (Replace this with your fetched data)
df = pd.read_csv("path_to_your_data.csv")  # Replace with actual file path or dataframe

# Initialize Dash app
app = dash.Dash(__name__)

# Define the layout of the dashboard
app.layout = html.Div(
    style={'background-color': '#E0F7FA', 'font-family': 'Arial, sans-serif'},
    children=[
        html.H1(
            'Nautical-Themed Stock Dashboard',
            style={'text-align': 'center', 'color': '#004D61'}
        ),
        dcc.Dropdown(
            id='stock-dropdown',
            options=[
                {'label': 'IBM', 'value': 'IBM'},
                {'label': 'Oracle', 'value': 'ORCL'},
                {'label': 'Microsoft', 'value': 'MSFT'},
                {'label': 'Google', 'value': 'GOOGL'},
                {'label': 'Amazon', 'value': 'AMZN'}
            ],
            value='IBM',
            style={'width': '50%', 'margin': 'auto', 'padding': '10px'}
        ),
        dcc.Graph(id='stock-graph', style={'height': '600px'}),
        dcc.Interval(
            id='interval-component',
            interval=60*1000,  # Update every minute
            n_intervals=0
        )
    ]
)

# Define callback to update graph based on selected stock
@app.callback(
    dash.dependencies.Output('stock-graph', 'figure'),
    [dash.dependencies.Input('stock-dropdown', 'value')]
)
def update_graph(selected_stock):
    # Filter data for the selected stock
    filtered_df = df[df['Stock'] == selected_stock]

    # Create traces for Close Price and RSI
    trace_close = go.Scatter(
        x=filtered_df['Date'],
        y=filtered_df['Close'],
        mode='lines',
        name='Closing Price',
        line=dict(color='#006064')
    )

    trace_rsi = go.Scatter(
        x=filtered_df['Date'],
        y=filtered_df['RSI'],
        mode='lines',
        name='RSI (Relative Strength Index)',
        yaxis='y2',
        line=dict(color='#FF6F00', dash='dash')
    )

    # Create layout with nautical theme
    layout = go.Layout(
        title=f'Stock Performance for {selected_stock}',
        xaxis={'title': 'Date'},
        yaxis={'title': 'Price (USD)'},
        yaxis2={
            'title': 'RSI',
            'overlaying': 'y',
            'side': 'right',
            'range': [0, 100]
        },
        plot_bgcolor='#B3E5FC',
        paper_bgcolor='#E0F7FA',
        font=dict(color='#004D61'),
        legend=dict(x=0, y=1.1),
    )

    # Create the figure with both price and RSI
    fig = go.Figure(data=[trace_close, trace_rsi], layout=layout)

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
