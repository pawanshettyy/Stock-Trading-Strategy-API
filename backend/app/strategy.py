import numpy as np
import pandas as pd
from typing import List, Dict, Any

def calculate_ma_strategy(
    stock_data: List[Dict[str, Any]], 
    short_window: int = 20, 
    long_window: int = 50
) -> Dict[str, Any]:
    """
    Calculate Moving Average Crossover Strategy performance
    
    Args:
        stock_data: List of stock data records
        short_window: Short-term moving average window (default: 20)
        long_window: Long-term moving average window (default: 50)
        
    Returns:
        Dictionary with strategy performance metrics
    """
    # Convert to pandas DataFrame for easier manipulation
    df = pd.DataFrame(stock_data)
    
    # Convert datetime strings to datetime objects if needed
    if isinstance(df['datetime'].iloc[0], str):
        df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Sort by datetime
    df = df.sort_values('datetime')
    
    # Calculate moving averages
    df['short_ma'] = df['close'].rolling(window=short_window).mean()
    df['long_ma'] = df['close'].rolling(window=long_window).mean()
    
    # Generate signals
    df['signal'] = 0
    df.loc[df['short_ma'] > df['long_ma'], 'signal'] = 1  # Buy signal
    df.loc[df['short_ma'] < df['long_ma'], 'signal'] = -1  # Sell signal
    
    # Generate trading orders (1 for buy, -1 for sell, 0 for hold)
    df['position'] = df['signal'].diff()
    
    # Calculate returns
    df['returns'] = df['close'].pct_change()
    
    # Calculate strategy returns (position at time t, return at time t+1)
    df['strategy_returns'] = df['signal'].shift(1) * df['returns']
    
    # Calculate cumulative returns
    df['cumulative_returns'] = (1 + df['strategy_returns']).cumprod()
    
    # Remove NaN values
    df = df.dropna()
    
    # Generate list of trades
    trades = []
    current_position = 0
    entry_price = 0
    entry_date = None
    
    for index, row in df.iterrows():
        if row['position'] == 1:  # Buy signal
            entry_price = row['close']
            entry_date = row['datetime']
            current_position = 1
        elif row['position'] == -1 and current_position == 1:  # Sell signal after holding
            exit_price = row['close']
            exit_date = row['datetime']
            profit = (exit_price - entry_price) / entry_price * 100
            trades.append({
                'entry_date': entry_date.isoformat() if hasattr(entry_date, 'isoformat') else str(entry_date),
                'exit_date': exit_date.isoformat() if hasattr(exit_date, 'isoformat') else str(exit_date),
                'entry_price': float(entry_price),
                'exit_price': float(exit_price),
                'profit_pct': float(profit),
                'type': 'long'
            })
            current_position = 0
    
    # Calculate performance metrics
    if trades:
        profits = [t['profit_pct'] for t in trades]
        profitable_trades = sum(1 for p in profits if p > 0)
        losing_trades = sum(1 for p in profits if p <= 0)
        total_trades = len(trades)
        win_rate = profitable_trades / total_trades if total_trades > 0 else 0
        
        avg_win = sum(p for p in profits if p > 0) / profitable_trades if profitable_trades > 0 else 0
        avg_loss = sum(p for p in profits if p <= 0) / losing_trades if losing_trades > 0 else 0
        
        # Calculate max drawdown
        cumulative_return = df['cumulative_returns'].values
        max_drawdown = 0
        if len(cumulative_return) > 0:
            peak = cumulative_return[0]
            for value in cumulative_return:
                if value > peak:
                    peak = value
                drawdown = (peak - value) / peak
                max_drawdown = max(max_drawdown, drawdown)
        
        # Calculate Sharpe ratio (annual)
        if df['strategy_returns'].std() > 0:
            sharpe = df['strategy_returns'].mean() / df['strategy_returns'].std() * np.sqrt(252)
        else:
            sharpe = None
        
        # Calculate total return
        total_return = df['cumulative_returns'].iloc[-1] - 1 if len(df) > 0 else 0
        
        performance = {
            'total_returns': float(total_return * 100),  # Convert to percentage
            'win_rate': float(win_rate * 100),  # Convert to percentage
            'total_trades': total_trades,
            'profitable_trades': profitable_trades,
            'losing_trades': losing_trades,
            'average_win': float(avg_win),
            'average_loss': float(avg_loss),
            'max_drawdown': float(max_drawdown * 100),  # Convert to percentage
            'sharpe_ratio': float(sharpe) if sharpe is not None else None,
            'trades': trades
        }
    else:
        performance = {
            'total_returns': 0.0,
            'win_rate': 0.0,
            'total_trades': 0,
            'profitable_trades': 0,
            'losing_trades': 0,
            'average_win': 0.0,
            'average_loss': 0.0,
            'max_drawdown': 0.0,
            'sharpe_ratio': None,
            'trades': []
        }
    
    return performance