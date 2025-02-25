from fastapi import FastAPI, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from app import models, schemas, crud, strategy
from app.database import engine, SessionLocal
from sqlalchemy import event

# Initialize FastAPI app
app = FastAPI(
    title="Stock Trading API",
    description="API for stock data analysis and trading strategies",
    version="1.0.0"
)

# Ensure database tables are created when the app starts
@event.listens_for(engine, "connect")
def startup(dbapi_connection, connection_record):
    models.Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Root route (Prevents 404 errors when visiting base URL)
@app.get("/", tags=["General"])
def root():
    """Root endpoint for API health check"""
    return {"message": "Welcome to the Stock Trading API!"}

# ------------------- Trade Endpoints -------------------

@app.post("/trades/", response_model=schemas.TradeResponse, tags=["Trades"])
def create_trade(trade: schemas.TradeCreate, db: Session = Depends(get_db)):
    """Create a new trade record"""
    return crud.create_trade(db, trade)

@app.get("/trades/", response_model=List[schemas.TradeResponse], tags=["Trades"])
def read_trades(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Fetch all trade records"""
    return crud.get_trades(db, skip, limit)

# ------------------- Ticker Data Endpoints -------------------

@app.post("/data/", response_model=schemas.TickerDataResponse, tags=["Ticker Data"])
def create_ticker_data(ticker_data: schemas.TickerDataCreate, db: Session = Depends(get_db)):
    """Add a new ticker data record to the database"""
    return crud.create_ticker_data(db, ticker_data)

@app.post("/data/bulk/", response_model=List[schemas.TickerDataResponse], tags=["Ticker Data"])
def create_ticker_data_bulk(ticker_data_list: List[schemas.TickerDataCreate], db: Session = Depends(get_db)):
    """Add multiple ticker data records to the database"""
    return crud.create_ticker_data_bulk(db, ticker_data_list)

@app.get("/data/", response_model=List[schemas.TickerDataResponse], tags=["Ticker Data"])
def get_ticker_data(
    skip: int = 0, 
    limit: int = 100, 
    ticker_symbol: Optional[str] = Query(None, description="Filter by ticker symbol"),
    db: Session = Depends(get_db)
):
    """Fetch ticker data with optional filtering by stock symbol"""
    return crud.get_ticker_data(db, skip, limit, ticker_symbol)

# ------------------- Strategy Endpoints -------------------

@app.get("/strategy/ma/{stock_symbol}", tags=["Strategies"])
def get_moving_average(stock_symbol: str, period: int = 5, db: Session = Depends(get_db)):
    """Calculate simple moving average for a given stock"""
    return strategy.calculate_moving_average(db, stock_symbol, period)

@app.get("/strategy/performance", response_model=dict, tags=["Strategies"])
def get_strategy_performance(
    ticker_symbol: str = Query(..., description="Stock ticker symbol"),
    short_window: int = Query(5, description="Short-term moving average window"),
    long_window: int = Query(20, description="Long-term moving average window"),
    db: Session = Depends(get_db)
):
    """
    Calculate the performance of a Moving Average Crossover Strategy.

    Returns:
    - Total trades
    - Winning/losing trades
    - Profit/loss
    - Buy/sell signals
    """
    return strategy.moving_average_crossover_strategy(db, ticker_symbol, short_window, long_window)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
