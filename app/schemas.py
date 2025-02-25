
from pydantic import BaseModel
from datetime import datetime

class TradeBase(BaseModel):
    stock_symbol: str
    trade_type: str  # BUY or SELL
    price: float
    quantity: int

class TradeCreate(TradeBase):
    pass  # Used for creating trades

class TradeResponse(TradeBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True  # Used for ORM compatibility
