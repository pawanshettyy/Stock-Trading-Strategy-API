from sqlalchemy import Column, Integer, String, Float, DateTime
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
