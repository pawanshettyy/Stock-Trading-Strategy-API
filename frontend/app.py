import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Stock Trading Strategy Dashboard",
    page_icon="📈",
    layout="wide"
)

# App title
st.title("📊 Stock Trading Strategy Dashboard by Pawan Shetty")

# Sidebar
st.sidebar.header("Strategy Parameters")
short_window = st.sidebar.slider("Short-term MA Window", min_value=5, max_value=50, value=20)
long_window = st.sidebar.slider("Long-term MA Window", min_value=20, max_value=200, value=50)

# API URL
API_URL = "http://localhost:8000"  # Update with your API URL when deployed

# Function to fetch data from API
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_stock_data():
    try:
        response = requests.get(f"{API_URL}/data")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error fetching stock data: {e}")
        return []

# Function to fetch strategy performance
def fetch_strategy_performance(short_window, long_window):
    try:
        response = requests.get(
            f"{API_URL}/strategy/performance?short_window={short_window}&long_window={long_window}"
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error fetching strategy performance: {e}")
        return None

# Main content
tab1, tab2 = st.tabs(["📈 Strategy Performance", "🔍 Data Explorer"])

with tab1:
    st.subheader("Moving Average Crossover Strategy")
    
    with st.spinner("Calculating strategy performance..."):
        performance = fetch_strategy_performance(short_window, long_window)
    
    if performance:
        # Create performance metrics display
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Return", f"{performance['total_returns']:.2f}%")
        
        with col2:
            st.metric("Win Rate", f"{performance['win_rate']:.2f}%")
        
        with col3:
            st.metric("Total Trades", performance['total_trades'])
        
        with col4:
            st.metric("Max Drawdown", f"{performance['max_drawdown']:.2f}%")
        
        # Additional metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Profitable Trades", performance['profitable_trades'])
        
        with col2:
            st.metric("Losing Trades", performance['losing_trades'])
        
        with col3:
            st.metric("Avg Win", f"{performance['average_win']:.2f}%")
        
        with col4:
            st.metric("Avg Loss", f"{performance['average_loss']:.2f}%")
        
        # Stock data for visualization
        stock_data = fetch_stock_data()
        
        if stock_data:
            # Create DataFrame
            df = pd.DataFrame(stock_data)
            
            # Ensure 'datetime' column is parsed correctly
            df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')  # Coerce invalid datetime entries
            
            # Sort data by datetime
            df = df.sort_values('datetime')
            
            # Calculate moving averages
            df['short_ma'] = df['close'].rolling(window=short_window).mean()
            df['long_ma'] = df['close'].rolling(window=long_window).mean()
            
            # Create trading signals
            df['signal'] = 0
            df.loc[df['short_ma'] > df['long_ma'], 'signal'] = 1  # Buy signal
            df.loc[df['short_ma'] < df['long_ma'], 'signal'] = -1  # Sell signal
            
            # Create Plotly figure
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                               vertical_spacing=0.1, 
                               subplot_titles=('Price and Moving Averages', 'Volume'),
                               row_heights=[0.7, 0.3])
            
            # Price and MA lines
            fig.add_trace(
                go.Scatter(x=df['datetime'], y=df['close'], name='Close Price', line=dict(color='black')),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=df['datetime'], y=df['short_ma'], name=f'{short_window} MA', line=dict(color='blue')),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(x=df['datetime'], y=df['long_ma'], name=f'{long_window} MA', line=dict(color='red')),
                row=1, col=1
            )
            
            # Add buy/sell markers for trades
            buy_signals = []
            sell_signals = []
            
            for trade in performance['trades']:
                entry_date = pd.to_datetime(trade['entry_date'])
                exit_date = pd.to_datetime(trade['exit_date'])
                
                buy_signals.append((entry_date, trade['entry_price']))
                sell_signals.append((exit_date, trade['exit_price']))
            
            if buy_signals:
                buy_dates, buy_prices = zip(*buy_signals)
                fig.add_trace(
                    go.Scatter(x=buy_dates, y=buy_prices, mode='markers', 
                              marker=dict(symbol='triangle-up', size=12, color='green'),
                              name='Buy Signal'),
                    row=1, col=1
                )
            
            if sell_signals:
                sell_dates, sell_prices = zip(*sell_signals)
                fig.add_trace(
                    go.Scatter(x=sell_dates, y=sell_prices, mode='markers', 
                              marker=dict(symbol='triangle-down', size=12, color='red'),
                              name='Sell Signal'),
                    row=1, col=1
                )
            
            # Volume
            fig.add_trace(
                go.Bar(x=df['datetime'], y=df['volume'], name='Volume', marker=dict(color='lightblue')),
                row=2, col=1
            )
            
            # Update layout
            fig.update_layout(
                height=600,
                title_text=f"Moving Average Crossover Strategy ({short_window}/{long_window})",
                xaxis_title="Date",
                yaxis_title="Price",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Trades table
            if performance['trades']:
                st.subheader("Trade Details")
                
                trades_df = pd.DataFrame(performance['trades'])
                trades_df['entry_date'] = pd.to_datetime(trades_df['entry_date'])
                trades_df['exit_date'] = pd.to_datetime(trades_df['exit_date'])
                
                # Format the dataframe for display
                trades_df_display = trades_df.copy()
                trades_df_display['entry_date'] = trades_df_display['entry_date'].dt.strftime('%Y-%m-%d')
                trades_df_display['exit_date'] = trades_df_display['exit_date'].dt.strftime('%Y-%m-%d')
                trades_df_display['profit_pct'] = trades_df_display['profit_pct'].map('{:.2f}%'.format)
                
                st.dataframe(trades_df_display, use_container_width=True)
            else:
                st.info("No trades were executed with the current parameters")
        else:
            st.warning("No stock data available to visualize")
    else:
        st.warning("Could not calculate strategy performance")

with tab2:
    st.subheader("Stock Data Explorer")
    
    stock_data = fetch_stock_data()
    
    if stock_data:
        # Create DataFrame
        df = pd.DataFrame(stock_data)
        df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
        df = df.sort_values('datetime')
        
        # Basic stats
        st.write(f"Total records: {len(df)}")
        st.write(f"Date range: {df['datetime'].min().date()} to {df['datetime'].max().date()}")
        
        # OHLC chart
        fig = go.Figure(data=[go.Candlestick(
            x=df['datetime'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='OHLC'
        )])
        
        fig.update_layout(
            title='Stock Price (OHLC)',
            xaxis_title='Date',
            yaxis_title='Price',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Data table with filter
        st.subheader("Raw Data")
        
        # Create date range filter
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start date",
                df['datetime'].min().date()
            )
        with col2:
            end_date = st.date_input(
                "End date",
                df['datetime'].max().date()
            )
        
        # Filter data
        filtered_df = df[(df['datetime'].dt.date >= start_date) & 
                         (df['datetime'].dt.date <= end_date)]
        
        # Format datetime for display
        display_df = filtered_df.copy()
        display_df['datetime'] = display_df['datetime'].dt.strftime('%Y-%m-%d')
        
        st.dataframe(display_df, use_container_width=True)
        
        # Download option
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Download filtered data as CSV",
            csv,
            "stock_data.csv",
            "text/csv",
            key='download-csv'
        )
        
    else:
        st.warning("No stock data available")
