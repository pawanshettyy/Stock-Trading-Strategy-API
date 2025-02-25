from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import List
from decimal import Decimal

class TradeBase(BaseModel):
    stock_symbol: str
    trade_type: str  # BUY or SELL
    price: float
    quantity: int

    @field_validator("price", mode="before")
    @classmethod
    def validate_price(cls, v):
        if isinstance(v, str):
            v = float(v)  # Ensure numeric conversion
        if v <= 0:
            raise ValueError("Price must be positive")
        return v

    @field_validator("quantity", mode="before")
    @classmethod
    def validate_quantity(cls, v):
        if isinstance(v, str):
            v = int(v)  # Ensure numeric conversion
        if v <= 0:
            raise ValueError("Quantity must be positive")
        return v

class TradeCreate(TradeBase):
    pass  # Used for creating trades

class TradeResponse(TradeBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True  # ORM compatibility

class TickerDataBase(BaseModel):
    recorded_at: datetime  # ✅ Fixed: Renamed from `timestamp` to match `models.py`
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: int
    ticker_symbol: str

    @field_validator("open_price", "high_price", "low_price", "close_price", mode="before")
    @classmethod
    def validate_prices(cls, v):
        if isinstance(v, str):
            v = float(v)  # Ensure numeric conversion
        if v <= 0:
            raise ValueError("Price must be positive")
        return v

    @field_validator("volume", mode="before")
    @classmethod
    def validate_volume(cls, v):
        if isinstance(v, str):
            v = int(v)  # Ensure numeric conversion
        if v < 0:
            raise ValueError("Volume cannot be negative")
        return v

class TickerDataCreate(TickerDataBase):
    pass

class TickerDataResponse(TickerDataBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # ORM compatibility

class StrategyPerformance(BaseModel):
    ticker_symbol: str
    start_date: datetime
    end_date: datetime
    total_trades: int
    winning_trades: int
    losing_trades: int
    profit_loss: float
    signals: List[dict]
