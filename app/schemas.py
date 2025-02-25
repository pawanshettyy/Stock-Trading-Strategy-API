from pydantic import BaseModel, validator
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

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

class TickerDataBase(BaseModel):
    datetime: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    ticker_symbol: str

    @validator('open', 'high', 'low', 'close')
    def validate_prices(cls, v):
        if v <= 0:
            raise ValueError("Price must be positive")
        return v
    
    @validator('volume')
    def validate_volume(cls, v):
        if v < 0:
            raise ValueError("Volume cannot be negative")
        return v

class TickerDataCreate(TickerDataBase):
    pass

class TickerDataResponse(TickerDataBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class StrategyPerformance(BaseModel):
    ticker_symbol: str
    start_date: datetime
    end_date: datetime
    total_trades: int
    winning_trades: int
    losing_trades: int
    profit_loss: float
    signals: List[dict]