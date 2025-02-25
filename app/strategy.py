import pandas as pd
from sqlalchemy.orm import Session
from .models import TickerData

def moving_average_crossover_strategy(db: Session, ticker_symbol: str, short_window: int = 5, long_window: int = 20):
    """
    Implements a Moving Average Crossover Strategy.
    """
    # Fetch stock data
    ticker_data = db.query(TickerData).filter(
        TickerData.ticker_symbol == ticker_symbol
    ).order_by(TickerData.timestamp).all()

    if len(ticker_data) < long_window:
        return {"error": f"Not enough data. Need at least {long_window} data points."}

    # Convert data to DataFrame
    df = pd.DataFrame([{
        "timestamp": data.timestamp,
        "close": float(data.close)
    } for data in ticker_data])

    if df.empty or df['close'].isnull().all():
        return {"error": "No valid price data available"}

    # Calculate moving averages
    df["short_ma"] = df["close"].rolling(window=short_window, min_periods=1).mean()
    df["long_ma"] = df["close"].rolling(window=long_window, min_periods=1).mean()

    # Generate signals
    df["signal"] = 0
    df.loc[df["short_ma"] > df["long_ma"], "signal"] = 1  # Buy
    df.loc[df["short_ma"] < df["long_ma"], "signal"] = -1  # Sell
    df["position"] = df["signal"].diff()

    # Debugging: Print last 10 rows
    print(df.tail(10))

    # Ensure there are signals
    if df["position"].dropna().empty:
        return {"error": "Not enough signal data for trading"}

    # Generate trade list
    trades = []
    for idx, row in df.iterrows():
        if row["position"] == 1:  # Buy signal
            trades.append({
                "timestamp": row["timestamp"].isoformat(),
                "type": "BUY",
                "price": row["close"],
                "signal": "Short MA crossed above Long MA"
            })
        elif row["position"] == -1:  # Sell signal
            trades.append({
                "timestamp": row["timestamp"].isoformat(),
                "type": "SELL",
                "price": row["close"],
                "signal": "Short MA crossed below Long MA"
            })

    # Calculate profit/loss & winning trades
    pnl = 0
    winning_trades = 0
    for i in range(0, len(trades) - 1, 2):  # Buy-Sell pairs
        trade_profit = trades[i + 1]["price"] - trades[i]["price"]
        pnl += trade_profit
        if trade_profit > 0:
            winning_trades += 1

    # Prepare result
    result = {
        "ticker_symbol": ticker_symbol,
        "start_date": df["timestamp"].iloc[0].isoformat() if not df.empty else None,
        "end_date": df["timestamp"].iloc[-1].isoformat() if not df.empty else None,
        "short_window": short_window,
        "long_window": long_window,
        "total_trades": len(trades) // 2,
        "winning_trades": winning_trades,  # ✅ Added winning trades count
        "profit_loss": round(pnl, 2),
        "signals": trades
    }

    return result
