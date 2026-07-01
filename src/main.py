"""Main FastAPI application for Stock Analysis Agent"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging
import asyncio
from typing import List

from config import settings
from src.data_fetcher import get_fetcher
from src.technical_analysis import TechnicalAnalyzer
from src.alerts import get_alert_manager
from src.sentiment_analysis import get_news_service
from src.llm_agent import get_stock_analysis
from src.models import (
    StockData, TechnicalAnalysisResult, AlertRequest, AlertResponse,
    AnalysisResponse, MultiStockAnalysisRequest, HealthResponse
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Stock Analysis Intelligent Agent",
    description="AI-powered stock analysis with technical indicators and sentiment analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
fetcher = get_fetcher()
alert_manager = get_alert_manager()
news_service = get_news_service()


# ============== Health Check ==============
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )


# ============== Stock Data Endpoints ==============
@app.get("/api/v1/stock/{symbol}")
async def get_stock_data(symbol: str):
    """
    Get current stock data
    
    Args:
        symbol: Stock ticker symbol
    
    Returns:
        Current stock price and information
    """
    logger.info(f"Fetching stock data for {symbol}")
    data = fetcher.get_current_price(symbol.upper())
    
    if not data:
        raise HTTPException(status_code=404, detail=f"Stock {symbol} not found")
    
    return data


@app.get("/api/v1/stocks", response_model=dict)
async def get_multiple_stocks(symbols: str = "AAPL,MSFT,GOOGL"):
    """
    Get data for multiple stocks
    
    Args:
        symbols: Comma-separated stock symbols
    
    Returns:
        Dictionary with data for each symbol
    """
    symbol_list = [s.strip().upper() for s in symbols.split(",")]
    logger.info(f"Fetching data for stocks: {symbol_list}")
    
    return fetcher.get_multiple_stocks_data(symbol_list)


# ============== Technical Analysis Endpoints ==============
@app.get("/api/v1/analysis/{symbol}")
async def get_technical_analysis(symbol: str, period: str = "3mo"):
    """
    Get technical analysis for a stock
    
    Args:
        symbol: Stock ticker symbol
        period: Data period (1mo, 3mo, 6mo, 1y, etc.)
    
    Returns:
        Technical analysis with RSI, MACD, Bollinger Bands, trend
    """
    logger.info(f"Getting technical analysis for {symbol}")
    
    # Fetch historical data
    data = fetcher.get_historical_data(symbol.upper(), period=period)
    if data is None or data.empty:
        raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
    
    # Calculate technical indicators
    analysis = TechnicalAnalyzer.get_complete_analysis(data, symbol.upper())
    if not analysis:
        raise HTTPException(status_code=400, detail="Failed to calculate technical indicators")
    
    return analysis


# ============== AI-Powered Analysis Endpoints ==============
@app.get("/api/v1/recommendation/{symbol}")
async def get_ai_recommendation(symbol: str, period: str = "3mo"):
    """
    Get AI-powered buy/sell recommendation
    
    Args:
        symbol: Stock ticker symbol
        period: Data period for analysis
    
    Returns:
        AI recommendation with confidence score and analysis
    """
    logger.info(f"Getting AI recommendation for {symbol}")
    
    try:
        # Get stock data
        stock_data = fetcher.get_current_price(symbol.upper())
        if not stock_data:
            raise HTTPException(status_code=404, detail=f"Stock {symbol} not found")
        
        # Get historical data and technical analysis
        hist_data = fetcher.get_historical_data(symbol.upper(), period=period)
        if hist_data is None or hist_data.empty:
            raise HTTPException(status_code=404, detail=f"No historical data for {symbol}")
        
        technical_analysis = TechnicalAnalyzer.get_complete_analysis(hist_data, symbol.upper())
        if not technical_analysis:
            raise HTTPException(status_code=400, detail="Failed to calculate technical indicators")
        
        # Get news sentiment
        sentiment_data = await news_service.get_news_sentiment(symbol.upper())
        
        # Combine data for LLM analysis
        analysis_input = {
            **stock_data,
            'technical_analysis': technical_analysis,
            'sentiment': sentiment_data['sentiment']
        }
        
        # Get LLM recommendation
        recommendation = await get_stock_analysis(
            analysis_input,
            provider=settings.llm_provider,
            api_key=settings.openai_api_key
        )
        
        return recommendation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recommendation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/analyze-portfolio")
async def analyze_portfolio(request: MultiStockAnalysisRequest):
    """
    Analyze multiple stocks as a portfolio
    
    Args:
        request: MultiStockAnalysisRequest with symbols list
    
    Returns:
        Portfolio analysis with recommendations for each stock
    """
    logger.info(f"Analyzing portfolio: {request.symbols}")
    
    try:
        results = []
        for symbol in request.symbols:
            try:
                # Get stock data
                stock_data = fetcher.get_current_price(symbol.upper())
                if not stock_data:
                    continue
                
                # Get technical analysis
                hist_data = fetcher.get_historical_data(symbol.upper(), period="3mo")
                if hist_data is None or hist_data.empty:
                    continue
                
                technical_analysis = TechnicalAnalyzer.get_complete_analysis(hist_data, symbol.upper())
                if not technical_analysis:
                    continue
                
                # Get recommendation
                analysis_input = {
                    **stock_data,
                    'technical_analysis': technical_analysis
                }
                
                recommendation = await get_stock_analysis(
                    analysis_input,
                    provider=settings.llm_provider
                )
                
                results.append(recommendation)
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {str(e)}")
                continue
        
        return {
            'timestamp': datetime.now().isoformat(),
            'stocks': results,
            'total_stocks': len(request.symbols),
            'analyzed_stocks': len(results),
            'summary': {
                'buy_count': sum(1 for r in results if r.get('recommendation') == 'BUY'),
                'sell_count': sum(1 for r in results if r.get('recommendation') == 'SELL'),
                'hold_count': sum(1 for r in results if r.get('recommendation') == 'HOLD')
            }
        }
    except Exception as e:
        logger.error(f"Error analyzing portfolio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============== Alert Management Endpoints ==============
@app.post("/api/v1/alerts", response_model=AlertResponse)
async def create_alert(request: AlertRequest):
    """
    Create a price alert
    
    Args:
        request: AlertRequest with symbol, alert type, and target price
    
    Returns:
        Created alert information
    """
    logger.info(f"Creating alert for {request.symbol}")
    
    alert = alert_manager.create_alert(
        request.symbol.upper(),
        request.alert_type,
        request.target_price
    )
    
    return AlertResponse(
        alert_id=alert.alert_id,
        symbol=alert.symbol,
        alert_type=alert.alert_type,
        target_price=alert.target_price,
        created_at=alert.created_at.isoformat(),
        triggered=alert.triggered
    )


@app.get("/api/v1/alerts")
async def get_alerts(symbol: str = None):
    """
    Get all active alerts
    
    Args:
        symbol: Optional symbol to filter alerts
    
    Returns:
        List of active alerts
    """
    return alert_manager.get_alerts(symbol)


@app.delete("/api/v1/alerts/{alert_id}")
async def delete_alert(alert_id: str):
    """
    Delete an alert
    
    Args:
        alert_id: ID of the alert to delete
    
    Returns:
        Success message
    """
    success = alert_manager.delete_alert(alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"message": "Alert deleted successfully"}


# ============== Sentiment Analysis Endpoints ==============
@app.get("/api/v1/sentiment/{symbol}")
async def get_sentiment(symbol: str):
    """
    Get news sentiment analysis for a stock
    
    Args:
        symbol: Stock ticker symbol
    
    Returns:
        Sentiment analysis with articles and scores
    """
    logger.info(f"Getting sentiment for {symbol}")
    
    return await news_service.get_news_sentiment(symbol.upper())


# ============== Background Tasks ==============
async def check_alerts_task():
    """
    Background task to check alerts periodically
    """
    while True:
        try:
            # Check alerts for default stocks
            stocks = settings.get_stock_list()
            for symbol in stocks:
                data = fetcher.get_current_price(symbol)
                if data:
                    alert_manager.check_alerts(symbol, data['current_price'])
            
            await asyncio.sleep(settings.price_alert_check_interval)
        except Exception as e:
            logger.error(f"Error in alert check task: {str(e)}")
            await asyncio.sleep(60)


@app.on_event("startup")
async def startup_event():
    """Start background tasks on app startup"""
    logger.info("Starting background tasks")
    asyncio.create_task(check_alerts_task())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level="info"
    )
