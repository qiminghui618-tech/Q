"""Stock data fetching module using Yahoo Finance"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class StockDataFetcher:
    """Fetch stock data from Yahoo Finance"""
    
    def __init__(self):
        self.cache = {}
        self.cache_timestamp = {}
        self.cache_ttl = 300  # 5 minutes cache TTL
    
    def get_historical_data(
        self, 
        symbol: str, 
        period: str = "3mo",
        interval: str = "1d"
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical stock data
        
        Args:
            symbol: Stock ticker symbol
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 5m, 15m, 30m, 60m, 1d, 1wk, 1mo)
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            logger.info(f"Fetching historical data for {symbol} ({period}, {interval})")
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                logger.warning(f"No data found for {symbol}")
                return None
            
            logger.info(f"Successfully fetched {len(data)} records for {symbol}")
            return data
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[Dict]:
        """
        Get current stock price and info
        
        Args:
            symbol: Stock ticker symbol
        
        Returns:
            Dictionary with current price info
        """
        try:
            # Check cache first
            cache_key = f"current_{symbol}"
            if self._is_cache_valid(cache_key):
                return self.cache[cache_key]
            
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")
            info = ticker.info
            
            if data.empty:
                return None
            
            current_price = data['Close'].iloc[-1]
            previous_close = info.get('previousClose', current_price)
            change = current_price - previous_close
            change_percent = (change / previous_close * 100) if previous_close != 0 else 0
            
            result = {
                'symbol': symbol,
                'current_price': float(current_price),
                'previous_close': float(previous_close),
                'change': float(change),
                'change_percent': float(change_percent),
                'high_52week': float(info.get('fiftyTwoWeekHigh', 0)),
                'low_52week': float(info.get('fiftyTwoWeekLow', 0)),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'timestamp': datetime.now().isoformat()
            }
            
            # Cache the result
            self.cache[cache_key] = result
            self.cache_timestamp[cache_key] = datetime.now()
            
            logger.info(f"Current price for {symbol}: ${current_price:.2f}")
            return result
        except Exception as e:
            logger.error(f"Error fetching current price for {symbol}: {str(e)}")
            return None
    
    def get_multiple_stocks_data(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        Get current data for multiple stocks
        
        Args:
            symbols: List of stock symbols
        
        Returns:
            Dictionary with data for each symbol
        """
        results = {}
        for symbol in symbols:
            results[symbol] = self.get_current_price(symbol)
        return results
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid"""
        if cache_key not in self.cache_timestamp:
            return False
        
        age = (datetime.now() - self.cache_timestamp[cache_key]).total_seconds()
        return age < self.cache_ttl
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
        self.cache_timestamp.clear()
        logger.info("Cache cleared")


# Singleton instance
_fetcher = StockDataFetcher()


def get_fetcher() -> StockDataFetcher:
    """Get singleton fetcher instance"""
    return _fetcher
