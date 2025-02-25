import pandas as pd
from sqlalchemy.orm import Session
from .models import Trade

def calculate_moving_average(db: Session, stock_symbol: str, period: int = 5):
    """ Calculates the moving average for a given stock symbol """
    trades = db.query(Trade).filter(Trade.stock_symbol == stock_symbol).order_by(Trade.timestamp).all()

    if len(trades) < period:
        return {"error": "Not enough data to calculate moving average"}

    df = pd.DataFrame([{"price": trade.price, "timestamp": trade.timestamp} for trade in trades])
    df["moving_avg"] = df["price"].rolling(window=period).mean()

    return df.to_dict(orient="records")
