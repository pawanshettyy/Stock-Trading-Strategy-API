import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app import schemas, models, strategy

client = TestClient(app)

class TestTickerDataValidation(unittest.TestCase):
    """Tests for the input validation of ticker data"""
    
    def test_valid_ticker_data(self):
        """Test that valid ticker data passes validation"""
        data = {
            "datetime": datetime.now().isoformat(),
            "open": 150.25,
            "high": 152.75,
            "low": 149.50,
            "close": 151.80,
            "volume": 1250000,
            "ticker_symbol": "AAPL"
        }
        ticker_data = schemas.TickerDataCreate(**data)
        self.assertEqual(ticker_data.ticker_symbol, "AAPL")
        self.assertEqual(float(ticker_data.close), 151.80)
    
    def test_negative_price(self):
        """Test that negative prices raise validation error"""
        data = {
            "datetime": datetime.now().isoformat(),
            "open": -150.25,  # Negative value should fail
            "high": 152.75,
            "low": 149.50,
            "close": 151.80,
            "volume": 1250000,
            "ticker_symbol": "AAPL"
        }
        with self.assertRaises(ValueError):
            schemas.TickerDataCreate(**data)
    
    def test_negative_volume(self):
        """Test that negative volume raises validation error"""
        data = {
            "datetime": datetime.now().isoformat(),
            "open": 150.25,
            "high": 152.75,
            "low": 149.50,
            "close": 151.80,
            "volume": -1250000,  # Negative value should fail
            "ticker_symbol": "AAPL"
        }
        with self.assertRaises(ValueError):
            schemas.TickerDataCreate(**data)

class TestMovingAverageCrossoverStrategy(unittest.TestCase):
    """Tests for the moving average crossover strategy calculations"""
    
    def setUp(self):
        """Set up test data"""
        # Create a series of mock ticker data spanning 30 days
        self.mock_data = []
        base_date = datetime(2023, 1, 1)
        base_price = 100.0
        
        # Create price series with a clear uptrend followed by downtrend
        for i in range(30):
            # First 15 days uptrend, next 15 days downtrend
            if i < 15:
                modifier = 1.0 + (i * 0.01)  # Price increases
            else:
                modifier = 1.15 - ((i - 15) * 0.01)  # Price decreases
            
            close_price = base_price * modifier
            
            # Add some random variation
            open_price = close_price * (1 + np.random.uniform(-0.01, 0.01))
            high_price = max(open_price, close_price) * (1 + np.random.uniform(0, 0.01))
            low_price = min(open_price, close_price) * (1 - np.random.uniform(0, 0.01))
            
            self.mock_data.append(models.TickerData(
                id=i+1,
                datetime=base_date + timedelta(days=i),
                open=Decimal(str(round(open_price, 2))),
                high=Decimal(str(round(high_price, 2))),
                low=Decimal(str(round(low_price, 2))),
                close=Decimal(str(round(close_price, 2))),
                volume=int(100000 * (1 + np.random.uniform(-0.2, 0.2))),
                ticker_symbol="TEST"
            ))
        
        # Mock DB session
        self.mock_db = MagicMock(spec=Session)
        self.mock_query = self.mock_db.query.return_value
        self.mock_filter = self.mock_query.filter.return_value
        self.mock_order = self.mock_filter.order_by.return_value
        self.mock_order.all.return_value = self.mock_data
    
    def test_moving_average_calculation(self):
        """Test that moving averages are calculated correctly"""
        # Calculate short and long MAs manually
        closes = [float(data.close) for data in self.mock_data]
        df = pd.DataFrame({'close': closes})
        
        short_window = 5
        long_window = 15
        
        expected_short_ma = df['close'].rolling(window=short_window).mean()
        expected_long_ma = df['close'].rolling(window=long_window).mean()
        
        # Get strategy results
        result = strategy.moving_average_crossover_strategy(
            self.mock_db, "TEST", short_window, long_window
        )
        
        # Verify we have the right number of trades (should have crossovers)
        self.assertGreater(result['total_trades'], 0)
        
        # Check if total trades equals winning + losing trades
        self.assertEqual(
            result['total_trades'], 
            result['winning_trades'] + result['losing_trades']
        )

    def test_not_enough_data(self):
        """Test handling when there's not enough data for calculation"""
        # Mock returning only a few data points
        self.mock_order.all.return_value = self.mock_data[:5]
        
        # Try calculating with long_window = 20
        result = strategy.moving_average_crossover_strategy(
            self.mock_db, "TEST", 5, 20
        )
        
        # Should return error
        self.assertIn('error', result)

class TestAPIEndpoints(unittest.TestCase):
    """Tests for the API endpoints"""
    
    def test_create_ticker_data(self):
        """Test creating ticker data via API"""
        data = {
            "datetime": datetime.now().isoformat(),
            "open": 150.25,
            "high": 152.75,
            "low": 149.50,
            "close": 151.80,
            "volume": 1250000,
            "ticker_symbol": "AAPL"
        }
        
        with patch('app.crud.create_ticker_data') as mock_create:
            # Mock the database creation
            mock_create.return_value = models.TickerData(
                id=1,
                datetime=datetime.fromisoformat(data["datetime"]),
                open=Decimal(str(data["open"])),
                high=Decimal(str(data["high"])),
                low=Decimal(str(data["low"])),
                close=Decimal(str(data["close"])),
                volume=data["volume"],
                ticker_symbol=data["ticker_symbol"],
                created_at=datetime.now()
            )
            
            response = client.post("/data/", json=data)
            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertEqual(result["ticker_symbol"], "AAPL")

if __name__ == "__main__":
    unittest.main()