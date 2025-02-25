from sqlalchemy import Column, Integer, String, Float, DateTime, DECIMAL, Enum
from sqlalchemy.sql import func
from .database import Base

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    stock_symbol = Column(String, index=True, nullable=False)
    trade_type = Column(Enum("BUY", "SELL", name="trade_type_enum"), nullable=False)  # Enforcing allowed values
    price = Column(DECIMAL(10, 2), nullable=False)  # Using DECIMAL for financial consistency
    quantity = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=func.now(), nullable=False)  # Auto timestamp

class TickerData(Base):
    __tablename__ = "ticker_data"

    id = Column(Integer, primary_key=True, index=True)
    recorded_at = Column(DateTime, index=True, nullable=False)  # Fixed column name
    open = Column(DECIMAL(10, 2), nullable=False)  # Fixed naming to match DB schema
    high = Column(DECIMAL(10, 2), nullable=False)
    low = Column(DECIMAL(10, 2), nullable=False)
    close = Column(DECIMAL(10, 2), nullable=False)
    volume = Column(Integer, nullable=False)
    ticker_symbol = Column(String, index=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)  # Timestamp for record creation
