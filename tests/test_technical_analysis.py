"""Tests for technical analysis module"""
import pytest
import pandas as pd
import numpy as np
from src.technical_analysis import TechnicalAnalyzer


@pytest.fixture
def sample_data():
    """Create sample stock data for testing"""
    dates = pd.date_range('2024-01-01', periods=100)
    data = {
        'Open': np.random.uniform(90, 110, 100),
        'High': np.random.uniform(100, 120, 100),
        'Low': np.random.uniform(80, 100, 100),
        'Close': np.random.uniform(90, 110, 100),
        'Volume': np.random.uniform(1000000, 10000000, 100)
    }
    return pd.DataFrame(data, index=dates)


def test_calculate_sma(sample_data):
    """Test SMA calculation"""
    sma = TechnicalAnalyzer.calculate_sma(sample_data, period=20)
    assert len(sma) == len(sample_data)
    assert sma.isna().sum() == 19  # First 19 values should be NaN


def test_calculate_rsi(sample_data):
    """Test RSI calculation"""
    rsi = TechnicalAnalyzer.calculate_rsi(sample_data, period=14)
    assert len(rsi) == len(sample_data)
    # RSI should be between 0-100
    valid_rsi = rsi.dropna()
    assert (valid_rsi >= 0).all() and (valid_rsi <= 100).all()


def test_calculate_macd(sample_data):
    """Test MACD calculation"""
    macd, signal, histogram = TechnicalAnalyzer.calculate_macd(sample_data)
    assert len(macd) == len(sample_data)
    assert len(signal) == len(sample_data)
    assert len(histogram) == len(sample_data)


def test_calculate_bollinger_bands(sample_data):
    """Test Bollinger Bands calculation"""
    bb = TechnicalAnalyzer.calculate_bollinger_bands(sample_data, period=20)
    assert 'upper' in bb
    assert 'middle' in bb
    assert 'lower' in bb
    # Upper should be above lower
    assert (bb['upper'] > bb['lower']).sum() > 0


def test_analyze_trend(sample_data):
    """Test trend analysis"""
    trend = TechnicalAnalyzer.analyze_trend(sample_data)
    assert 'trend' in trend
    assert 'current_price' in trend
    assert trend['trend'] in ["NEUTRAL", "UPTREND", "DOWNTREND", "STRONG UPTREND", "STRONG DOWNTREND"]
