"""News sentiment analysis module"""
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Analyze news sentiment for stocks"""
    
    @staticmethod
    def analyze_news(news_data: List[Dict]) -> Dict:
        """
        Analyze sentiment from news articles
        
        Args:
            news_data: List of news articles with text
        
        Returns:
            Dictionary with sentiment analysis results
        """
        if not news_data:
            return {
                'sentiment': 'NEUTRAL',
                'score': 0.0,
                'article_count': 0,
                'articles': []
            }
        
        total_sentiment = 0
        articles_analyzed = []
        
        for article in news_data:
            article_sentiment = SentimentAnalyzer._analyze_article(article)
            total_sentiment += article_sentiment['score']
            articles_analyzed.append(article_sentiment)
        
        avg_sentiment = total_sentiment / len(articles_analyzed) if articles_analyzed else 0
        
        # Normalize to -1 to 1
        normalized_sentiment = max(-1, min(1, avg_sentiment))
        
        return {
            'sentiment': SentimentAnalyzer._classify_sentiment(normalized_sentiment),
            'score': normalized_sentiment,
            'article_count': len(articles_analyzed),
            'articles': articles_analyzed[:5]  # Return top 5
        }
    
    @staticmethod
    def _analyze_article(article: Dict) -> Dict:
        """
        Analyze sentiment of a single article
        
        Args:
            article: Article data with title and description
        
        Returns:
            Dictionary with article and sentiment
        """
        text = f"{article.get('title', '')} {article.get('description', '')}".lower()
        
        # Simple keyword-based sentiment analysis
        sentiment_score = SentimentAnalyzer._keyword_sentiment(text)
        
        return {
            'title': article.get('title', ''),
            'source': article.get('source', ''),
            'url': article.get('url', ''),
            'published_at': article.get('published_at', ''),
            'sentiment': SentimentAnalyzer._classify_sentiment(sentiment_score),
            'score': sentiment_score
        }
    
    @staticmethod
    def _keyword_sentiment(text: str) -> float:
        """
        Simple keyword-based sentiment analysis
        
        Args:
            text: Text to analyze
        
        Returns:
            Sentiment score (-1 to 1)
        """
        # Positive keywords
        positive_keywords = [
            'gain', 'bull', 'surge', 'soar', 'rally', 'strong', 'growth',
            'profit', 'positive', 'win', 'success', 'up', 'bullish',
            'record', 'breakthrough', 'outperform', 'beat', 'upgrade'
        ]
        
        # Negative keywords
        negative_keywords = [
            'loss', 'bear', 'plunge', 'crash', 'decline', 'weak', 'fall',
            'loss', 'negative', 'fail', 'risk', 'down', 'bearish',
            'downgrade', 'miss', 'underperform', 'cut', 'warning'
        ]
        
        score = 0
        
        for word in positive_keywords:
            if word in text:
                score += 0.2
        
        for word in negative_keywords:
            if word in text:
                score -= 0.2
        
        # Normalize
        return max(-1, min(1, score))
    
    @staticmethod
    def _classify_sentiment(score: float) -> str:
        """Classify sentiment based on score"""
        if score > 0.3:
            return "POSITIVE"
        elif score < -0.3:
            return "NEGATIVE"
        else:
            return "NEUTRAL"


class NewsService:
    """Service for fetching and analyzing news"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour
    
    async def get_news_sentiment(self, symbol: str) -> Dict:
        """
        Get news sentiment for a stock
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Dictionary with sentiment analysis
        """
        # For mock implementation, return placeholder data
        logger.info(f"Fetching news sentiment for {symbol}")
        
        mock_news = [
            {
                'title': f'{symbol} stock surges on strong earnings',
                'description': 'The company reported better-than-expected quarterly earnings',
                'source': 'Financial Times',
                'url': 'https://example.com/news1',
                'published_at': '2024-07-01T10:00:00Z'
            },
            {
                'title': f'{symbol} announces new partnership',
                'description': 'Strategic partnership with leading tech company',
                'source': 'Bloomberg',
                'url': 'https://example.com/news2',
                'published_at': '2024-07-01T09:30:00Z'
            }
        ]
        
        sentiment = SentimentAnalyzer.analyze_news(mock_news)
        
        return {
            'symbol': symbol,
            'sentiment': sentiment,
            'news_items': mock_news
        }


# Singleton instance
_news_service = NewsService()


def get_news_service() -> NewsService:
    """Get singleton news service"""
    return _news_service
