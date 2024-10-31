# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 21:13:24 2024

@author: Iaina
"""

import yfinance as yf
import pandas as pd
import dash
from dash import dcc, html
import plotly.graph_objs as go
import plotly.express as px
import numpy as np
from dash.dependencies import Input, Output

# Initialize Dash app
app = dash.Dash(__name__)

# Dropdown options for selecting stocks
stock_options = [
    {'label': 'IBM', 'value': 'IBM'},
    {'label': 'Oracle', 'value': 'ORCL'},
    {'label': 'Microsoft', 'value': 'MSFT'},
    {'label': 'Google', 'value': 'GOOGL'},
    {'label': 'Amazon', 'value': 'AMZN'}
]

# ======== Data Processing Functions ========

# Fetch historical stock data
def fetch_stock_data(ticker, period='1y', interval='1d'):
    if ticker is None:
        return pd.DataFrame()
    stock = yf.Ticker(ticker)
    data = stock.history(period=period, interval=interval)
    return data

# Calculate moving averages
def calculate_moving_averages(data, short_window=50, long_window=200):
    data['MA50'] = data['Close'].rolling(window=short_window).mean()
    data['MA200'] = data['Close'].rolling(window=long_window).mean()
    return data

# Calculate percentage change in stock price
def calculate_price_change(data):
    data['Price Change (%)'] = data['Close'].pct_change() * 100
    return data

# Calculate volatility as standard deviation of price changes over a rolling window
def calculate_volatility(data, window=14):
    data['Volatility'] = data['Price Change (%)'].rolling(window=window).std()
    return data

# Calculate Relative Strength Index (RSI)
def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    return data

# Generate sample sentiment data
def fetch_sentiment_data(ticker):
    sentiment_data = pd.DataFrame({
        'Date': pd.date_range(start='2023-01-01', periods=30, freq='D'),
        'Positive': np.random.randint(10, 40, size=30),
        'Neutral': np.random.randint(20, 50, size=30),
        'Negative': np.random.randint(5, 30, size=30),
        'Volume': np.random.randint(100000, 1000000, size=30),
        'Volatility': np.random.uniform(1, 3, size=30)
    })
    # Calculate sentiment index as a simple weighted score
    sentiment_data['Sentiment Index'] = sentiment_data['Positive'] - sentiment_data['Negative']
    return sentiment_data

# ======== Visualization Functions ========

# Stock performance line and RSI graph
def create_stock_graph(data, selected_stock):
    trace_close = go.Scatter(
        x=data.index,
        y=data['Close'],
        mode='lines',
        name='Closing Price',
        line=dict(color='#006064')
    )
    trace_rsi = go.Scatter(
        x=data.index,
        y=data['RSI'],
        mode='lines',
        name='RSI',
        yaxis='y2',
        line=dict(color='#FF6F00', dash='dash')
    )
    layout = go.Layout(
        title=f'Stock Performance for {selected_stock}',
        xaxis={'title': 'Date'},
        yaxis={'title': 'Price (USD)'},
        yaxis2={'title': 'RSI', 'overlaying': 'y', 'side': 'right', 'range': [0, 100]},
        plot_bgcolor='#B3E5FC',
        paper_bgcolor='#E0F7FA',
        font=dict(color='#004D61'),
    )
    return go.Figure(data=[trace_close, trace_rsi], layout=layout)

# Volatility over time graph
def create_volatility_graph(data):
    fig = go.Figure(go.Scatter(
        x=data.index, y=data['Volatility'],
        mode='lines', name='Volatility',
        line=dict(color='#FFA500')
    ))
    fig.update_layout(
        title="Volatility Over Time",
        xaxis_title="Date",
        yaxis_title="Volatility",
        plot_bgcolor='#E0F7FA',
        paper_bgcolor='#E0F7FA',
        font=dict(color='#004D61'),
        title_x=0.5  # Center title
    )
    return fig

# Investor Sentiment Index graph
def create_sentiment_index_graph(data):
    fig = go.Figure(go.Scatter(
        x=data['Date'], y=data['Sentiment Index'],
        mode='lines', name='Sentiment Index',
        line=dict(color='#42A5F5')
    ))
    fig.update_layout(
        title="Investor Sentiment Index Over Time",
        xaxis_title="Date",
        yaxis_title="Sentiment Index",
        plot_bgcolor='#E0F7FA',
        paper_bgcolor='#E0F7FA',
        font=dict(color='#004D61'),
        title_x=0.5  # Center title
    )
    return fig

# Bubble chart for sentiment vs. volatility
def create_bubble_chart(data):
    fig = px.scatter(
        data, x="Volatility", y="Positive", size="Volume", color="Negative",
        hover_name="Date", title="Investor Sentiment vs Volatility",
        labels={"Positive": "Positive Sentiment", "Volatility": "Volatility (VIX)"}
    )
    fig.update_layout(transition_duration=500, template="plotly_white", height=400, title_x=0.5)  # Center title
    return fig

# Bar chart for sentiment distribution
def create_sentiment_bar_chart(data):
    fig = px.bar(
        data, x="Date", y=["Positive", "Neutral", "Negative"],
        title="Sentiment Distribution Over Time",
        labels={"value": "Sentiment Score", "variable": "Sentiment Type"},
        barmode="group"
    )
    fig.update_layout(transition_duration=500, template="plotly_white", height=400, title_x=0.5)  # Center title
    return fig

# Gauge chart for market volatility
def create_volatility_gauge(data):
    latest_volatility = data['Volatility'].iloc[-1] if not data.empty else 0
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=latest_volatility,
        title={'text': "Market Volatility"},
        gauge={'axis': {'range': [0, 3]},
               'bar': {'color': "#FFA500"},
               'steps': [
                   {'range': [0, 1], 'color': "#00cc99"},
                   {'range': [1, 2], 'color': "#ffcc00"},
                   {'range': [2, 3], 'color': "#ff3300"}]
               }
    ))
    fig.update_layout(paper_bgcolor="#E0F7FA")
    return fig

# ======== Dashboard Layout with Tabs ========

app.layout = html.Div(
    style={'background-color': '#E0F7FA', 'font-family': 'Arial, sans-serif'},
    children=[
        html.H1(
            'Stock Savvy: A Dashboard for Market Mavens',
            style={'text-align': 'center', 'color': '#004D61', 'padding': '20px'}
        ),
        html.Div([
            html.Label("Select a Company:", style={'font-weight': 'bold', 'font-size': '20px', 'margin-right': '15px'}),
            dcc.Dropdown(
                id='stock-dropdown',
                options=stock_options,
                value='IBM',
                style={'width': '250px', 'display': 'inline-block', 'font-size': '18px'}
            )
        ], style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'padding': '20px', 'background-color': '#BBDEFB'}),
        
        # Tabs for organizing components
        dcc.Tabs([
            dcc.Tab(label='Overview', children=[dcc.Graph(id='stock-graph', style={'height': '600px'})],
                    style={'font-weight': 'bold', 'font-size': '18px', 'color': '#ffffff', 'background-color': '#1565C0'}),
            dcc.Tab(label='Sentiment Analysis', children=[
                html.Div([
                    dcc.Graph(id='bubble-chart', style={'display': 'inline-block', 'width': '48%', 'padding': '20px'}),
                    dcc.Graph(id='sentiment-bar-chart', style={'display': 'inline-block', 'width': '48%', 'padding': '20px'}),
                ], style={'textAlign': 'center', 'padding': '20px'})
            ], style={'font-weight': 'bold', 'font-size': '18px', 'color': '#ffffff', 'background-color': '#1565C0'}),
            dcc.Tab(label='Volatility Trends', children=[dcc.Graph(id='volatility-graph', style={'height': '600px'})],
                    style={'font-weight': 'bold', 'font-size': '18px', 'color': '#ffffff', 'background-color': '#1565C0'}),
            dcc.Tab(label='Investor Insights', children=[
                html.Div([
                    dcc.Graph(id='sentiment-index-graph', style={'display': 'inline-block', 'width': '48%', 'padding': '20px'}),
                    dcc.Graph(id='volatility-gauge', style={'display': 'inline-block', 'width': '48%', 'padding': '20px'}),
                ], style={'textAlign': 'center', 'padding': '20px'})
            ], style={'font-weight': 'bold', 'font-size': '18px', 'color': '#ffffff', 'background-color': '#1565C0'}),
        ])
    ]
)

# ======== Callbacks ========

# Update stock graph based on dropdown selection
@app.callback(Output('stock-graph', 'figure'), [Input('stock-dropdown', 'value')])
def update_stock_graph(selected_stock):
    data = fetch_stock_data(selected_stock)
    if data.empty:
        return go.Figure()
    data = calculate_moving_averages(data)
    data = calculate_price_change(data)
    data = calculate_rsi(data)
    return create_stock_graph(data, selected_stock)

# Update sentiment charts based on dropdown selection
@app.callback(
    [Output('bubble-chart', 'figure'), Output('sentiment-bar-chart', 'figure')],
    [Input('stock-dropdown', 'value')]
)
def update_sentiment_graphs(selected_stock):
    data = fetch_sentiment_data(selected_stock)
    bubble_chart = create_bubble_chart(data)
    sentiment_bar_chart = create_sentiment_bar_chart(data)
    return bubble_chart, sentiment_bar_chart

# Update volatility graph based on dropdown selection
@app.callback(Output('volatility-graph', 'figure'), [Input('stock-dropdown', 'value')])
def update_volatility_graph(selected_stock):
    data = fetch_stock_data(selected_stock)
    if data.empty:
        return go.Figure()
    data = calculate_price_change(data)
    data = calculate_volatility(data)
    return create_volatility_graph(data)

# Update investor sentiment index graph and volatility gauge based on dropdown selection
@app.callback(
    [Output('sentiment-index-graph', 'figure'), Output('volatility-gauge', 'figure')],
    [Input('stock-dropdown', 'value')]
)
def update_investor_insights(selected_stock):
    data = fetch_sentiment_data(selected_stock)
    sentiment_index_graph = create_sentiment_index_graph(data)
    volatility_gauge = create_volatility_gauge(data)
    return sentiment_index_graph, volatility_gauge

# ======== Run the App ========
if __name__ == '__main__':
    app.run_server(debug=True)
