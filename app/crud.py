from sqlalchemy.orm import Session
from . import models, schemas
from typing import List, Optional
from sqlalchemy import desc

def create_trade(db: Session, trade: schemas.TradeCreate):
    """ Inserts a new trade record into the database """
    db_trade = models.Trade(
        stock_symbol=trade.stock_symbol,
        trade_type=trade.trade_type,
        price=trade.price,
        quantity=trade.quantity
    )
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    return db_trade

def get_trades(db: Session, skip: int = 0, limit: int = 10):
    """ Fetches a list of trades with optional pagination """
    return db.query(models.Trade).offset(skip).limit(limit).all()

def create_ticker_data(db: Session, ticker_data: schemas.TickerDataCreate):
    """ Inserts a new ticker data record into the database """
    db_ticker_data = models.TickerData(
        datetime=ticker_data.datetime,
        open=ticker_data.open,
        high=ticker_data.high,
        low=ticker_data.low,
        close=ticker_data.close,
        volume=ticker_data.volume,
        ticker_symbol=ticker_data.ticker_symbol
    )
    db.add(db_ticker_data)
    db.commit()
    db.refresh(db_ticker_data)
    return db_ticker_data

def create_ticker_data_bulk(db: Session, ticker_data_list: List[schemas.TickerDataCreate]):
    """ Inserts multiple ticker data records into the database """
    db_ticker_data_list = [
        models.TickerData(
            datetime=item.datetime,
            open=item.open,
            high=item.high,
            low=item.low,
            close=item.close,
            volume=item.volume,
            ticker_symbol=item.ticker_symbol
        ) for item in ticker_data_list
    ]
    
    db.add_all(db_ticker_data_list)
    db.commit()
    
    return db_ticker_data_list

def get_ticker_data(db: Session, skip: int = 0, limit: int = 100, ticker_symbol: Optional[str] = None):
    """ Fetches a list of ticker data with optional filtering and pagination """
    query = db.query(models.TickerData)
    
    if ticker_symbol:
        query = query.filter(models.TickerData.ticker_symbol == ticker_symbol)
    
    return query.order_by(models.TickerData.datetime).offset(skip).limit(limit).all()

def get_ticker_data_for_strategy(db: Session, ticker_symbol: str):
    """ Fetches all ticker data for a specific symbol for strategy calculation """
    return db.query(models.TickerData).filter(
        models.TickerData.ticker_symbol == ticker_symbol
    ).order_by(models.TickerData.datetime).all()