import logging
from sqlalchemy.orm import Session
from . import models
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def moving_average_crossover_strategy(db: Session, ticker_symbol: str, short_window: int, long_window: int):
    logger.info(f"Fetching historical data for {ticker_symbol}...")

    # Fetch historical data from the database
    ticker_data = (
        db.query(models.TickerData)
        .filter(models.TickerData.ticker_symbol == ticker_symbol)
        .order_by(models.TickerData.recorded_at)
        .all()
    )

    if not ticker_data:
        logger.error("No data found for the given ticker symbol.")
        return {"error": "No data found for the given ticker symbol."}

    logger.info(f"Fetched {len(ticker_data)} records for {ticker_symbol}")

    # Convert data to DataFrame
    df = pd.DataFrame(
        [(d.recorded_at, d.close) for d in ticker_data], columns=["recorded_at", "close"]
    )
    df.set_index("recorded_at", inplace=True)

    # Ensure sufficient data for moving averages
    if len(df) < max(short_window, long_window):
        logger.error("Not enough data for the given moving average windows.")
        return {"error": "Not enough data for the given moving average windows."}

    logger.info(f"Calculating {short_window}-day and {long_window}-day moving averages...")

    # Calculate moving averages
    df["short_ma"] = df["close"].rolling(window=short_window).mean()
    df["long_ma"] = df["close"].rolling(window=long_window).mean()

    # Debug: Print last few rows of moving averages
    logger.info(f"Latest moving average values:\n{df[['close', 'short_ma', 'long_ma']].tail(5)}")

    # Generate buy/sell signals
    logger.info("Generating buy/sell signals...")
    df["signal"] = 0  # Default: No signal
    df.loc[df["short_ma"] > df["long_ma"], "signal"] = 1  # Buy signal
    df.loc[df["short_ma"] < df["long_ma"], "signal"] = -1  # Sell signal

    # Debug: Log last 5 signal changes
    logger.info(f"Recent signal values:\n{df[['short_ma', 'long_ma', 'signal']].tail(5)}")

    # Calculate trade statistics
    df["trade"] = df["signal"].diff().fillna(0)  # Detect changes in signal
    total_trades = df["trade"].abs().sum()
    winning_trades = (df["trade"] == 1).sum()
    losing_trades = (df["trade"] == -1).sum()

    # Simplified profit/loss calculation
    profit_loss = (df["close"].iloc[-1] - df["close"].iloc[0]) * total_trades  

    logger.info(f"Strategy execution completed for {ticker_symbol}")
    logger.info(f"Total trades: {total_trades}, Winning trades: {winning_trades}, Losing trades: {losing_trades}")
    logger.info(f"Estimated profit/loss: {profit_loss}")

    return {
        "ticker_symbol": ticker_symbol,
        "total_trades": int(total_trades),
        "winning_trades": int(winning_trades),
        "losing_trades": int(losing_trades),
        "profit_loss": float(profit_loss),
        "signals": df[["close", "short_ma", "long_ma", "signal"]].reset_index().to_dict(orient="records")
    }
