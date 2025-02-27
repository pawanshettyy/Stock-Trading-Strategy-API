from fastapi import APIRouter, Depends, HTTPException
from prisma import Prisma
from app.database import get_prisma
from app.schemas import StockDataCreate, StockData, MovingAverageParams
from app.strategy import calculate_ma_strategy
from typing import List
from datetime import datetime

router = APIRouter()

@router.get("/data", response_model=List[StockData])
async def get_stock_data(prisma: Prisma = Depends(get_prisma)):
    """Fetch all stock data records from the database."""
    try:
        stocks = await prisma.stockdata.find_many()
        return stocks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/data", response_model=StockData)
async def create_stock_data(data: StockDataCreate, prisma: Prisma = Depends(get_prisma)):
    """Add a new stock data record to the database."""
    try:
        # Check if record with this datetime already exists
        existing = await prisma.stockdata.find_unique(
            where={"datetime": data.datetime}
        )
        
        if existing:
            raise HTTPException(
                status_code=400, 
                detail=f"Record with datetime {data.datetime} already exists"
            )
        
        # Create new record
        new_record = await prisma.stockdata.create(
            data={
                "datetime": data.datetime,
                "open": float(data.open),
                "high": float(data.high),
                "low": float(data.low),
                "close": float(data.close),
                "volume": data.volume,
                "instrument": data.instrument
            }
        )
        return new_record
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/strategy/performance")
async def get_strategy_performance(
    params: MovingAverageParams = Depends(),
    prisma: Prisma = Depends(get_prisma)
):
    """
    Calculate and return the performance of the Moving Average Crossover Strategy.
    
    Query parameters:
    - short_window: Short-term moving average window (default: 20)
    - long_window: Long-term moving average window (default: 50)
    - instrument: Filter by instrument (optional)
    """
    try:
        # Query stock data
        where = {}
        if params.instrument:
            where["instrument"] = params.instrument
            
        stocks = await prisma.stockdata.find_many(
            where=where,
            order_by={"datetime": "asc"}
        )
        
        if not stocks:
            raise HTTPException(
                status_code=404,
                detail="No stock data found"
            )
        
        # Convert Prisma models to dictionaries for the strategy function
        stock_data = []
        for stock in stocks:
            stock_dict = dict(stock)
            # Convert decimal values to floats for JSON serialization
            for key in ['open', 'high', 'low', 'close']:
                stock_dict[key] = float(stock_dict[key])
            stock_data.append(stock_dict)
        
        # Calculate strategy performance
        performance = calculate_ma_strategy(
            stock_data, 
            short_window=params.short_window, 
            long_window=params.long_window
        )
        
        return performance
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating strategy: {str(e)}")