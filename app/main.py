from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import database, models, schemas, crud, strategy

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/trades/", response_model=schemas.TradeResponse)
def create_trade(trade: schemas.TradeCreate, db: Session = Depends(get_db)):
    return crud.create_trade(db, trade)

@app.get("/trades/", response_model=list[schemas.TradeResponse])
def read_trades(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_trades(db, skip, limit)

@app.get("/strategy/{stock_symbol}")
def get_moving_average(stock_symbol: str, period: int = 5, db: Session = Depends(get_db)):
    return strategy.calculate_moving_average(db, stock_symbol, period)
