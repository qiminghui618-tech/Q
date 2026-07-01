"""Pydantic models for API requests and responses"""
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from datetime import datetime


class StockData(BaseModel):
    """Stock data model"""
    symbol: str
    current_price: float
    change: float
    change_percent: float
    high_52week: float
    low_52week: float
    pe_ratio: float
    market_cap: int


class TechnicalAnalysisResult(BaseModel):
    """Technical analysis result model"""
    symbol: str
    current_price: float
    rsi: Optional[float] = None
    rsi_signal: str
    macd: Dict[str, Optional[float]]
    bollinger_bands: Dict[str, Optional[float]]
    trend: Dict[str, Any]


class AlertRequest(BaseModel):
    """Create price alert request"""
    symbol: str
    alert_type: str  # above, below
    target_price: float


class AlertResponse(BaseModel):
    """Price alert response"""
    alert_id: str
    symbol: str
    alert_type: str
    target_price: float
    created_at: str
    triggered: bool


class AnalysisResponse(BaseModel):
    """Stock analysis response"""
    symbol: str
    timestamp: str
    current_price: float
    recommendation: str  # BUY, SELL, HOLD
    confidence: float
    analysis: Dict[str, Any]
    risk_level: str
    target_price: float
    stop_loss: float


class MultiStockAnalysisRequest(BaseModel):
    """Request for analyzing multiple stocks"""
    symbols: List[str]
    include_sentiment: bool = True


class MultiStockAnalysisResponse(BaseModel):
    """Response for multiple stocks analysis"""
    timestamp: str
    stocks: List[Dict[str, Any]]
    summary: Dict[str, Any]


class PortfolioRequest(BaseModel):
    """Portfolio analysis request"""
    stocks: List[str]
    weights: Optional[List[float]] = None


class PortfolioAnalysis(BaseModel):
    """Portfolio analysis response"""
    stocks: List[Dict[str, Any]]
    total_value: float
    portfolio_recommendation: str
    diversification_score: float
    risk_score: float


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str
