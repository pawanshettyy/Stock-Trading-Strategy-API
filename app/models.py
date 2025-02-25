from sqlalchemy import Column, Integer, String, Float, DateTime, DECIMAL
from .database import Base
import datetime

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    stock_symbol = Column(String, index=True)
    trade_type = Column(String)  # "BUY" or "SELL"
    price = Column(Float)
    quantity = Column(Integer)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class TickerData(Base):
    __tablename__ = "ticker_data"

    id = Column(Integer, primary_key=True, index=True)
    datetime = Column(DateTime, index=True)
    open = Column(DECIMAL(10, 2), nullable=False)
    high = Column(DECIMAL(10, 2), nullable=False)
    low = Column(DECIMAL(10, 2), nullable=False)
    close = Column(DECIMAL(10, 2), nullable=False)
    volume = Column(Integer, nullable=False)
    ticker_symbol = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)