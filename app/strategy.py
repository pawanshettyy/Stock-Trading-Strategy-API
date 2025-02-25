import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from typing import Dict, List, Tuple
from .models import Trade, TickerData

def calculate_moving_average(db: Session, stock_symbol: str, period: int = 5):
    """ Calculates the moving average for a given stock symbol """
    trades = db.query(Trade).filter(Trade.stock_symbol == stock_symbol).order_by(Trade.timestamp).all()

    if len(trades) < period:
        return {"error": "Not enough data to calculate moving average"}

    df = pd.DataFrame([{"price": trade.price, "timestamp": trade.timestamp} for trade in trades])
    df["moving_avg"] = df["price"].rolling(window=period).mean()

    return df.to_dict(orient="records")

def moving_average_crossover_strategy(db: Session, ticker_symbol: str, short_window: int = 5, long_window: int = 20):
    """
    Implements a Moving Average Crossover Strategy
    
    Args:
        db: Database session
        ticker_symbol: The stock ticker symbol
        short_window: Short-term moving average window (default: 5)
        long_window: Long-term moving average window (default: 20)
        
    Returns:
        Dictionary containing strategy performance metrics and signals
    """
    # Get data from database
    ticker_data = db.query(TickerData).filter(
        TickerData.ticker_symbol == ticker_symbol
    ).order_by(TickerData.datetime).all()
    
    if len(ticker_data) < long_window:
        return {"error": f"Not enough data. Need at least {long_window} data points."}
    
    # Convert to DataFrame
    df = pd.DataFrame([{
        "datetime": data.datetime,
        "open": float(data.open),
        "high": float(data.high),
        "low": float(data.low),
        "close": float(data.close),
        "volume": data.volume
    } for data in ticker_data])
    
    # Calculate moving averages
    df['short_ma'] = df['close'].rolling(window=short_window).mean()
    df['long_ma'] = df['close'].rolling(window=long_window).mean()
    
    # Generate signals
    df['signal'] = 0
    df.loc[df['short_ma'] > df['long_ma'], 'signal'] = 1  # Buy signal
    df.loc[df['short_ma'] < df['long_ma'], 'signal'] = -1  # Sell signal
    
    # Generate trading orders
    df['position'] = df['signal'].diff()
    
    # Calculate returns
    df['returns'] = df['close'].pct_change()
    df['strategy_returns'] = df['returns'] * df['signal'].shift(1)
    
    # Generate trade list
    trades = []
    current_position = 0
    
    for idx, row in df.iterrows():
        if pd.notna(row['position']) and row['position'] != 0:
            if row['position'] > 0:  # Buy signal
                trades.append({
                    'datetime': row['datetime'].isoformat(),
                    'type': 'BUY',
                    'price': row['close'],
                    'signal': 'Short MA crossed above Long MA'
                })
                current_position = 1
            elif row['position'] < 0 and current_position > 0:  # Sell signal
                trades.append({
                    'datetime': row['datetime'].isoformat(),
                    'type': 'SELL',
                    'price': row['close'],
                    'signal': 'Short MA crossed below Long MA'
                })
                current_position = 0
    
    # Calculate performance metrics
    winning_trades = len([t for t in range(1, len(trades), 2) if trades[t]['price'] > trades[t-1]['price']])
    total_trades = len(trades) // 2  # Each round trip is one trade
    
    # Calculate profit/loss
    pnl = 0
    for i in range(0, len(trades), 2):
        if i + 1 < len(trades):
            buy_price = trades[i]['price']
            sell_price = trades[i+1]['price']
            pnl += (sell_price - buy_price)
    
    # Prepare result
    result = {
        "ticker_symbol": ticker_symbol,
        "start_date": df['datetime'].iloc[0].isoformat() if not df.empty else None,
        "end_date": df['datetime'].iloc[-1].isoformat() if not df.empty else None,
        "short_window": short_window,
        "long_window": long_window,
        "total_trades": total_trades,
        "winning_trades": winning_trades,
        "losing_trades": total_trades - winning_trades,
        "win_rate": (winning_trades / total_trades) if total_trades > 0 else 0,
        "profit_loss": round(pnl, 2),
        "cumulative_return": round(df['strategy_returns'].cumsum().iloc[-1] * 100, 2) if not df.empty else 0,
        "signals": trades
    }
    
    return result