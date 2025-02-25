from sqlalchemy.orm import Session
from . import models, schemas

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
