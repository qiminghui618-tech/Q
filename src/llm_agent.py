"""LLM-based analysis agent"""
import json
from typing import Dict, Optional
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def analyze_stock(self, stock_data: Dict) -> Dict:
        """Analyze stock data and provide recommendation"""
        pass


class MockLLM(LLMProvider):
    """Mock LLM for development and testing"""
    
    async def analyze_stock(self, stock_data: Dict) -> Dict:
        """
        Generate mock analysis based on technical indicators
        
        Args:
            stock_data: Dictionary with stock and technical analysis data
        
        Returns:
            Dictionary with analysis and recommendation
        """
        try:
            symbol = stock_data.get('symbol', 'UNKNOWN')
            current_price = stock_data.get('current_price', 0)
            technical = stock_data.get('technical_analysis', {})
            
            # Extract signals
            rsi = technical.get('rsi', 50)
            rsi_signal = technical.get('rsi_signal', 'NEUTRAL')
            trend = technical.get('trend', {}).get('trend', 'NEUTRAL')
            macd = technical.get('macd', {})
            bb = technical.get('bollinger_bands', {})
            
            # Generate recommendation based on signals
            signals = self._count_signals(rsi_signal, trend, macd, bb)
            recommendation = self._generate_recommendation(signals)
            confidence = self._calculate_confidence(signals)
            
            return {
                'symbol': symbol,
                'timestamp': stock_data.get('timestamp', ''),
                'current_price': current_price,
                'recommendation': recommendation,
                'confidence': confidence,
                'analysis': {
                    'summary': self._generate_summary(symbol, recommendation, rsi_signal, trend),
                    'signals': {
                        'rsi': {
                            'value': rsi,
                            'signal': rsi_signal,
                            'interpretation': self._interpret_rsi_extended(rsi)
                        },
                        'trend': {
                            'current_trend': trend,
                            'interpretation': self._interpret_trend(trend)
                        },
                        'macd': {
                            'value': macd.get('histogram', 0),
                            'interpretation': self._interpret_macd(macd)
                        }
                    }
                },
                'risk_level': self._assess_risk(rsi_signal, trend),
                'target_price': self._estimate_target(current_price, trend),
                'stop_loss': self._estimate_stop_loss(current_price, trend)
            }
        except Exception as e:
            logger.error(f"Error in mock LLM analysis: {str(e)}")
            return {
                'error': str(e),
                'recommendation': 'HOLD',
                'confidence': 0
            }
    
    @staticmethod
    def _count_signals(rsi_signal: str, trend: str, macd: Dict, bb: Dict) -> int:
        """Count bullish signals"""
        signals = 0
        
        if rsi_signal == "OVERSOLD":
            signals += 1
        elif rsi_signal == "OVERBOUGHT":
            signals -= 1
        
        if "UP" in trend.upper():
            signals += 1
        elif "DOWN" in trend.upper():
            signals -= 1
        
        if macd.get('histogram', 0) > 0:
            signals += 1
        elif macd.get('histogram', 0) < 0:
            signals -= 1
        
        return signals
    
    @staticmethod
    def _generate_recommendation(signals: int) -> str:
        """Generate recommendation based on signals"""
        if signals >= 2:
            return "BUY"
        elif signals <= -2:
            return "SELL"
        else:
            return "HOLD"
    
    @staticmethod
    def _calculate_confidence(signals: int) -> float:
        """Calculate confidence score (0-1)"""
        return min(abs(signals) / 3.0, 1.0)
    
    @staticmethod
    def _generate_summary(symbol: str, recommendation: str, rsi_signal: str, trend: str) -> str:
        """Generate analysis summary"""
        return f"{symbol} is currently in a {trend} with {rsi_signal} RSI conditions. Based on technical indicators, the recommendation is to {recommendation}."
    
    @staticmethod
    def _interpret_rsi_extended(rsi: float) -> str:
        """Extended RSI interpretation"""
        if rsi > 80:
            return "Extremely overbought - Strong sell signal"
        elif rsi > 70:
            return "Overbought - Consider selling"
        elif rsi > 60:
            return "Moderately strong uptrend"
        elif rsi > 40:
            return "Neutral - Balanced momentum"
        elif rsi > 30:
            return "Moderately weak downtrend"
        elif rsi > 20:
            return "Oversold - Consider buying"
        else:
            return "Extremely oversold - Strong buy signal"
    
    @staticmethod
    def _interpret_trend(trend: str) -> str:
        """Interpret trend"""
        trend_upper = trend.upper()
        if "STRONG UP" in trend_upper:
            return "Very bullish - Strong upward momentum"
        elif "UP" in trend_upper:
            return "Bullish - Upward momentum"
        elif "STRONG DOWN" in trend_upper:
            return "Very bearish - Strong downward momentum"
        elif "DOWN" in trend_upper:
            return "Bearish - Downward momentum"
        else:
            return "Neutral - No clear direction"
    
    @staticmethod
    def _interpret_macd(macd: Dict) -> str:
        """Interpret MACD signal"""
        histogram = macd.get('histogram', 0)
        if histogram > 0:
            return "MACD line above signal line - Bullish signal"
        elif histogram < 0:
            return "MACD line below signal line - Bearish signal"
        else:
            return "MACD lines crossed - Potential signal reversal"
    
    @staticmethod
    def _assess_risk(rsi_signal: str, trend: str) -> str:
        """Assess risk level"""
        trend_upper = trend.upper()
        
        if rsi_signal == "OVERBOUGHT" and "DOWN" in trend_upper:
            return "HIGH"
        elif rsi_signal == "OVERSOLD" and "UP" in trend_upper:
            return "MEDIUM"
        elif "STRONG" in trend_upper:
            return "LOW"
        else:
            return "MEDIUM"
    
    @staticmethod
    def _estimate_target(current_price: float, trend: str) -> float:
        """Estimate target price"""
        trend_upper = trend.upper()
        
        if "UP" in trend_upper:
            return current_price * 1.05  # 5% upside
        elif "DOWN" in trend_upper:
            return current_price * 0.95  # 5% downside
        else:
            return current_price
    
    @staticmethod
    def _estimate_stop_loss(current_price: float, trend: str) -> float:
        """Estimate stop loss level"""
        trend_upper = trend.upper()
        
        if "UP" in trend_upper:
            return current_price * 0.97  # 3% below current
        elif "DOWN" in trend_upper:
            return current_price * 1.03  # 3% above current
        else:
            return current_price * 0.98


class OpenAILLM(LLMProvider):
    """OpenAI GPT-based LLM provider"""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model
    
    async def analyze_stock(self, stock_data: Dict) -> Dict:
        """Analyze stock using OpenAI (to be implemented)"""
        # TODO: Implement actual OpenAI integration
        logger.warning("OpenAI LLM not yet implemented, falling back to mock")
        mock_llm = MockLLM()
        return await mock_llm.analyze_stock(stock_data)


class LLMAgentFactory:
    """Factory for creating LLM agents"""
    
    @staticmethod
    def create(provider: str, **kwargs) -> LLMProvider:
        """
        Create LLM provider instance
        
        Args:
            provider: Provider type (mock, openai, claude)
            **kwargs: Additional arguments for the provider
        
        Returns:
            LLMProvider instance
        """
        if provider.lower() == "mock":
            return MockLLM()
        elif provider.lower() == "openai":
            api_key = kwargs.get('api_key')
            model = kwargs.get('model', 'gpt-4')
            return OpenAILLM(api_key, model)
        else:
            logger.warning(f"Unknown provider {provider}, using mock")
            return MockLLM()


async def get_stock_analysis(
    stock_data: Dict,
    provider: str = "mock",
    api_key: Optional[str] = None
) -> Dict:
    """
    Get LLM-based stock analysis
    
    Args:
        stock_data: Stock and technical data dictionary
        provider: LLM provider (mock, openai, claude)
        api_key: API key for the provider
    
    Returns:
        Analysis and recommendation from LLM
    """
    llm = LLMAgentFactory.create(
        provider,
        api_key=api_key
    )
    return await llm.analyze_stock(stock_data)
