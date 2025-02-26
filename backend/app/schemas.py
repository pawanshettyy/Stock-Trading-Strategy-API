from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class StockDataBase(BaseModel):
    datetime: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    instrument: str

class StockDataCreate(StockDataBase):
    pass

class StockData(StockDataBase):
    id: int

    class Config:
        from_attributes = True

class StrategyPerformance(BaseModel):
    total_returns: float
    win_rate: float
    total_trades: int
    profitable_trades: int
    losing_trades: int
    average_win: float
    average_loss: float
    max_drawdown: float
    sharpe_ratio: Optional[float] = None
    trades: List[dict] = []

class MovingAverageParams(BaseModel):
    short_window: int = Field(default=20, gt=0)
    long_window: int = Field(default=50, gt=0)
    instrument: Optional[str] = None