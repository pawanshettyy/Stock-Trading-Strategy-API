from sqlalchemy import Column, Integer, Float, String, DateTime
from app.database import Base

class StockData(Base):
    __tablename__ = "hindalco_stock"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
