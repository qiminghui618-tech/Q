"""Technical analysis indicators module"""
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class TechnicalAnalyzer:
    """Calculate technical analysis indicators"""
    
    @staticmethod
    def calculate_sma(data: pd.DataFrame, period: int = 20) -> pd.Series:
        """
        Calculate Simple Moving Average
        
        Args:
            data: DataFrame with 'Close' column
            period: Period for SMA calculation
        
        Returns:
            Series with SMA values
        """
        return data['Close'].rolling(window=period).mean()
    
    @staticmethod
    def calculate_ema(data: pd.DataFrame, period: int = 20) -> pd.Series:
        """
        Calculate Exponential Moving Average
        
        Args:
            data: DataFrame with 'Close' column
            period: Period for EMA calculation
        
        Returns:
            Series with EMA values
        """
        return data['Close'].ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def calculate_rsi(data: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI)
        
        Args:
            data: DataFrame with 'Close' column
            period: Period for RSI calculation (default 14)
        
        Returns:
            Series with RSI values (0-100)
        """
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def calculate_macd(data: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            data: DataFrame with 'Close' column
            fast: Fast EMA period (default 12)
            slow: Slow EMA period (default 26)
            signal: Signal line period (default 9)
        
        Returns:
            Tuple of (MACD line, Signal line, Histogram)
        """
        ema_fast = data['Close'].ewm(span=fast, adjust=False).mean()
        ema_slow = data['Close'].ewm(span=slow, adjust=False).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def calculate_bollinger_bands(data: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> Dict[str, pd.Series]:
        """
        Calculate Bollinger Bands
        
        Args:
            data: DataFrame with 'Close' column
            period: Period for SMA (default 20)
            std_dev: Number of standard deviations (default 2)
        
        Returns:
            Dictionary with upper, middle, lower bands
        """
        sma = data['Close'].rolling(window=period).mean()
        std = data['Close'].rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return {
            'upper': upper_band,
            'middle': sma,
            'lower': lower_band
        }
    
    @staticmethod
    def analyze_trend(data: pd.DataFrame, short_period: int = 20, long_period: int = 50) -> Dict[str, any]:
        """
        Analyze trend using moving averages
        
        Args:
            data: DataFrame with OHLCV data
            short_period: Short MA period
            long_period: Long MA period
        
        Returns:
            Dictionary with trend analysis
        """
        sma_short = TechnicalAnalyzer.calculate_sma(data, short_period)
        sma_long = TechnicalAnalyzer.calculate_sma(data, long_period)
        
        current_price = data['Close'].iloc[-1]
        current_sma_short = sma_short.iloc[-1]
        current_sma_long = sma_long.iloc[-1]
        
        trend = "NEUTRAL"
        if current_sma_short > current_sma_long:
            if current_price > current_sma_short:
                trend = "STRONG UPTREND"
            else:
                trend = "UPTREND"
        elif current_sma_short < current_sma_long:
            if current_price < current_sma_short:
                trend = "STRONG DOWNTREND"
            else:
                trend = "DOWNTREND"
        
        return {
            'trend': trend,
            'current_price': float(current_price),
            'sma_short': float(current_sma_short),
            'sma_long': float(current_sma_long),
            'short_above_long': bool(current_sma_short > current_sma_long),
            'price_above_short_ma': bool(current_price > current_sma_short)
        }
    
    @staticmethod
    def get_complete_analysis(data: pd.DataFrame, symbol: str) -> Dict:
        """
        Get complete technical analysis for a stock
        
        Args:
            data: DataFrame with OHLCV data
            symbol: Stock symbol
        
        Returns:
            Dictionary with all technical indicators
        """
        try:
            if data.empty or len(data) < 50:
                return None
            
            # Calculate indicators
            rsi = TechnicalAnalyzer.calculate_rsi(data)
            macd_line, signal_line, histogram = TechnicalAnalyzer.calculate_macd(data)
            bb = TechnicalAnalyzer.calculate_bollinger_bands(data)
            trend_analysis = TechnicalAnalyzer.analyze_trend(data)
            
            current_price = data['Close'].iloc[-1]
            
            return {
                'symbol': symbol,
                'current_price': float(current_price),
                'rsi': float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None,
                'rsi_signal': TechnicalAnalyzer._interpret_rsi(rsi.iloc[-1]),
                'macd': {
                    'line': float(macd_line.iloc[-1]) if not pd.isna(macd_line.iloc[-1]) else None,
                    'signal': float(signal_line.iloc[-1]) if not pd.isna(signal_line.iloc[-1]) else None,
                    'histogram': float(histogram.iloc[-1]) if not pd.isna(histogram.iloc[-1]) else None,
                },
                'bollinger_bands': {
                    'upper': float(bb['upper'].iloc[-1]) if not pd.isna(bb['upper'].iloc[-1]) else None,
                    'middle': float(bb['middle'].iloc[-1]) if not pd.isna(bb['middle'].iloc[-1]) else None,
                    'lower': float(bb['lower'].iloc[-1]) if not pd.isna(bb['lower'].iloc[-1]) else None,
                },
                'trend': trend_analysis
            }
        except Exception as e:
            logger.error(f"Error in complete analysis for {symbol}: {str(e)}")
            return None
    
    @staticmethod
    def _interpret_rsi(rsi_value: float) -> str:
        """Interpret RSI value"""
        if pd.isna(rsi_value):
            return "UNKNOWN"
        if rsi_value > 70:
            return "OVERBOUGHT"
        elif rsi_value < 30:
            return "OVERSOLD"
        else:
            return "NEUTRAL"
