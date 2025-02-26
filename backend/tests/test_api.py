import pytest
from fastapi.testclient import TestClient
from app.main import app
from datetime import datetime

client = TestClient(app)

def test_read_data():
    """Test GET /data endpoint"""
    response = client.get("/data")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_create_data_valid():
    """Test POST /data endpoint with valid data"""
    test_data = {
        "datetime": datetime.now().isoformat(),
        "open": 100.0,
        "high": 105.0,
        "low": 95.0,
        "close": 102.0,
        "volume": 10000,
        "instrument": "TEST"
    }
    
    response = client.post("/data", json=test_data)
    
    # Note: In a real test, we would use a test database
    # Here we check if the API validates the data correctly
    # The actual DB operation might fail if the record exists
    assert response.status_code in [200, 400]
    
    if response.status_code == 400:
        # If it fails, it should be because of duplicate
        assert "already exists" in response.json()["detail"]

def test_create_data_invalid():
    """Test POST /data endpoint with invalid data"""
    # Missing required fields
    test_data = {
        "datetime": datetime.now().isoformat(),
        "open": 100.0,
        # Missing high, low, close
        "volume": 10000,
        "instrument": "TEST"
    }
    
    response = client.post("/data", json=test_data)
    assert response.status_code == 422  # Validation error

def test_strategy_performance():
    """Test GET /strategy/performance endpoint"""
    response = client.get("/strategy/performance?short_window=10&long_window=30")
    
    # The response might be 200 or 404 depending on if data exists
    if response.status_code == 200:
        data = response.json()
        assert "total_returns" in data
        assert "win_rate" in data
        assert "total_trades" in data
        assert "trades" in data
    else:
        assert response.status_code == 404
        assert "No stock data found" in response.json()["detail"]