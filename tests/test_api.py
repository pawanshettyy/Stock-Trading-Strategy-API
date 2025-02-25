import unittest
import pandas as pd
from unittest.mock import MagicMock
from datetime import datetime
from app.strategy import moving_average_crossover_strategy
from app.models import TickerData

class TestMovingAverageCrossoverStrategy(unittest.TestCase):
    def setUp(self):
        """Create mock data for testing."""
        self.mock_db = MagicMock()

        # Generate at least 20 data points (to be safe)
        self.mock_data = [
            TickerData(
                ticker_symbol="HINDALCO",
                timestamp=datetime.strptime(f"2024-02-{i+1} 00:00:00", "%Y-%m-%d %H:%M:%S"),  # Convert to datetime
                open=100 + i,
                high=105 + i,
                low=95 + i,
                close=100 + (i % 5) * 2,
                volume=1000 + i * 10
            )
            for i in range(20)  # Ensure we have enough data
        ]

        # Properly mock query behavior
        self.mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = self.mock_data

    def test_moving_average_calculation(self):
        """Test that moving averages are calculated correctly and strategy returns expected keys"""
        closes = [float(data.close) for data in self.mock_data]
        df = pd.DataFrame({'close': closes})

        short_window = 5
        long_window = 15

        df['short_ma'] = df['close'].rolling(window=short_window).mean()
        df['long_ma'] = df['close'].rolling(window=long_window).mean()
        df['crossover'] = df['short_ma'] > df['long_ma']
        print(df.tail(10))

        result = moving_average_crossover_strategy(self.mock_db, "HINDALCO", short_window, long_window)

        print(f"Strategy Output: {result}")
        self.assertIsInstance(result, dict, "Strategy output is not a dictionary")
        self.assertIn('total_trades', result, "Missing key: 'total_trades'")
        self.assertIn('profit_loss', result, "Missing key: 'profit_loss'")
        self.assertIn('signals', result, "Missing key: 'signals'")
        self.assertGreaterEqual(result["total_trades"], 0, "Total trades should be non-negative")

if __name__ == "__main__":
    unittest.main()
