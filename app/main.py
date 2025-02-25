from fastapi import FastAPI, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from . import database, models, schemas, crud, strategy

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Stock Trading API", description="API for stock data analysis and trading strategies")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Trade endpoints
@app.post("/trades/", response_model=schemas.TradeResponse)
def create_trade(trade: schemas.TradeCreate, db: Session = Depends(get_db)):
    return crud.create_trade(db, trade)

@app.get("/trades/", response_model=List[schemas.TradeResponse])
def read_trades(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_trades(db, skip, limit)

# Ticker Data endpoints
@app.post("/data/", response_model=schemas.TickerDataResponse)
def create_ticker_data(ticker_data: schemas.TickerDataCreate, db: Session = Depends(get_db)):
    """Add a new ticker data record to the database"""
    return crud.create_ticker_data(db, ticker_data)

@app.post("/data/bulk/", response_model=List[schemas.TickerDataResponse])
def create_ticker_data_bulk(ticker_data_list: List[schemas.TickerDataCreate], db: Session = Depends(get_db)):
    """Add multiple ticker data records to the database"""
    return crud.create_ticker_data_bulk(db, ticker_data_list)

@app.get("/data/", response_model=List[schemas.TickerDataResponse])
def get_ticker_data(
    skip: int = 0, 
    limit: int = 100, 
    ticker_symbol: Optional[str] = Query(None, description="Filter by ticker symbol"),
    db: Session = Depends(get_db)
):
    """Fetch ticker data with optional filtering"""
    return crud.get_ticker_data(db, skip, limit, ticker_symbol)

# Strategy endpoints
@app.get("/strategy/ma/{stock_symbol}")
def get_moving_average(stock_symbol: str, period: int = 5, db: Session = Depends(get_db)):
    """Calculate simple moving average for a stock"""
    return strategy.calculate_moving_average(db, stock_symbol, period)

@app.get("/strategy/performance", response_model=dict)
def get_strategy_performance(
    ticker_symbol: str = Query(..., description="Stock ticker symbol"),
    short_window: int = Query(5, description="Short-term moving average window"),
    long_window: int = Query(20, description="Long-term moving average window"),
    db: Session = Depends(get_db)
):
    """
    Calculate performance of a Moving Average Crossover Strategy
    
    Returns performance metrics including:
    - Total trades
    - Winning/losing trades
    - Profit/loss
    - Buy/sell signals
    """
    return strategy.moving_average_crossover_strategy(db, ticker_symbol, short_window, long_window)