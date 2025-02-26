import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from app.strategy import calculate_ma_strategy

def generate_test_data(days=100):
    """Generate synthetic stock data for testing"""
    data = []
    start_date = datetime(2023, 1, 1)
    
    # Generate random price series
    np.random.seed(42)  # For reproducibility
    price = 100.0
    for i in range(days):
        current_date = start_date + timedelta(days=i)
        # Random daily change (-2% to +2%)
        daily_change = np.random.normal(0, 0.01)
        price *= (1 + daily_change)
        
        high = price * (1 + abs(np.random.normal(0, 0.005)))
        low = price * (1 - abs(np.random.normal(0, 0.005)))
        open_price = price * (1 + np.random.normal(0, 0.003))
        
        data.append({
            "id": i + 1,
            "datetime": current_date,
            "open": float(open_price),
            "high": float(high),
            "low": float(low),
            "close": float(price),
            "volume": int(np.random.normal(100000, 20000)),
            "instrument": "TEST"
        })
    
    return data

def test_calculate_ma_strategy():
    """Test the moving average crossover strategy calculation"""
    # Generate test data
    test_data = generate_test_data(days=100)
    
    # Calculate strategy
    result = calculate_ma_strategy(test_data, short_window=10, long_window=30)
    
    # Check that the result contains expected keys
    assert "total_returns" in result
    assert "win_rate" in result
    assert "total_trades" in result
    assert "profitable_trades" in result
    assert "losing_trades" in result
    assert "average_win" in result
    assert "average_loss" in result
    assert "max_drawdown" in result
    assert "sharpe_ratio" in result
    assert "trades" in result
    
    # Check that the values are of the correct type
    assert isinstance(result["total_returns"], float)
    assert isinstance(result["win_rate"], float)
    assert isinstance(result["total_trades"], int)
    assert isinstance(result["trades"], list)
    
    # Check consistency
    assert result["profitable_trades"] + result["losing_trades"] == result["total_trades"]
    
    # Check trades format
    if result["trades"]:
        trade = result["trades"][0]
        assert "entry_date" in trade
        assert "exit_date" in trade
        assert "entry_price" in trade
        assert "exit_price" in trade
        assert "profit_pct" in trade
        assert "type" in trade

def test_edge_cases():
    """Test edge cases for the strategy calculation"""
    # Test with empty data
    empty_result = calculate_ma_strategy([], short_window=10, long_window=30)
    assert empty_result["total_trades"] == 0
    assert empty_result["total_returns"] == 0.0
    
    # Test with too few data points
    short_data = generate_test_data(days=5)  # Not enough for MA calculation
    short_result = calculate_ma_strategy(short_data, short_window=10, long_window=30)
    assert short_result["total_trades"] == 0  # Should have no trades
    
    # Test with equal MA windows
    equal_window_result = calculate_ma_strategy(
        generate_test_data(days=100), 
        short_window=20, 
        long_window=20
    )
    # Equal windows should still produce a valid result
    assert isinstance(equal_window_result["total_returns"], float)