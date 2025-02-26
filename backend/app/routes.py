from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import StockData

router = APIRouter()

@router.get("/stocks/")
def get_stock_data(db: Session = Depends(get_db)):
    stocks = db.query(StockData).all()
    return {"data": stocks}
