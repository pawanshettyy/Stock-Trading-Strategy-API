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
    if not stock_data:
        return {
            "total_returns": 0,
            "win_rate": 0,
            "total_trades": 0,
            "profitable_trades": 0,
            "losing_trades": 0,
            "average_win": 0,
            "average_loss": 0,
            "max_drawdown": 0,
            "sharpe_ratio": None,
            "trades": [],
            "error": "Stock data is empty."
        }
    
    df = pd.DataFrame(stock_data)
    
    if 'datetime' not in df or 'close' not in df:
        return {
            "error": "Missing required columns ('datetime', 'close')."
        }
    
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    df = df.dropna(subset=['datetime', 'close'])
    
    if df.empty:
        return {
            "total_returns": 0,
            "win_rate": 0,
            "total_trades": 0,
            "profitable_trades": 0,
            "losing_trades": 0,
            "average_win": 0,
            "average_loss": 0,
            "max_drawdown": 0,
            "sharpe_ratio": None,
            "trades": [],
            "error": "No valid stock data available."
        }
    
    df = df.sort_values('datetime')
    
    df['short_ma'] = df['close'].rolling(window=short_window, min_periods=1).mean()
    df['long_ma'] = df['close'].rolling(window=long_window, min_periods=1).mean()
    
    df['signal'] = np.where(df['short_ma'] > df['long_ma'], 1, -1)
    df['position'] = df['signal'].diff()
    df['returns'] = df['close'].pct_change().fillna(0)
    df['strategy_returns'] = df['signal'].shift(1).fillna(0) * df['returns']
    df['cumulative_returns'] = (1 + df['strategy_returns']).cumprod()
    
    trades = []
    current_position = 0
    entry_price = 0
    entry_date = None
    
    for index, row in df.iterrows():
        if row['position'] == 1:
            entry_price = row['close']
            entry_date = row['datetime']
            current_position = 1
        elif row['position'] == -1 and current_position == 1:
            exit_price = row['close']
            exit_date = row['datetime']
            profit = (exit_price - entry_price) / entry_price * 100
            trades.append({
                'entry_date': entry_date.isoformat(),
                'exit_date': exit_date.isoformat(),
                'entry_price': float(entry_price),
                'exit_price': float(exit_price),
                'profit_pct': float(profit),
                'type': 'long'
            })
            current_position = 0
    
    profits = [t['profit_pct'] for t in trades]
    total_trades = len(trades)
    profitable_trades = sum(1 for p in profits if p > 0)
    losing_trades = total_trades - profitable_trades
    win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0
    avg_win = np.mean([p for p in profits if p > 0]) if profitable_trades > 0 else 0
    avg_loss = np.mean([p for p in profits if p <= 0]) if losing_trades > 0 else 0
    
    peak = df['cumulative_returns'].cummax()
    drawdown = (peak - df['cumulative_returns']) / peak
    max_drawdown = drawdown.max() * 100 if not drawdown.empty else 0
    
    strategy_std = df['strategy_returns'].std()
    sharpe_ratio = (df['strategy_returns'].mean() / strategy_std * np.sqrt(252)) if strategy_std > 0 else None
    
    total_return = (df['cumulative_returns'].iloc[-1] - 1) * 100 if not df.empty else 0
    
    return {
        'total_returns': float(total_return),
        'win_rate': float(win_rate),
        'total_trades': total_trades,
        'profitable_trades': profitable_trades,
        'losing_trades': losing_trades,
        'average_win': float(avg_win),
        'average_loss': float(avg_loss),
        'max_drawdown': float(max_drawdown),
        'sharpe_ratio': float(sharpe_ratio) if sharpe_ratio is not None else None,
        'trades': trades
    }
