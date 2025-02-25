from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)

def test_create_trade():
    response = client.post(
        "/trades/",
        json={"stock_symbol": "AAPL", "trade_type": "BUY", "price": 150.5, "quantity": 10}
    )
    assert response.status_code == 200
    assert response.json()["stock_symbol"] == "AAPL"

def test_read_trades():
    response = client.get("/trades/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
