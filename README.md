# Q - Stock Analysis Intelligent Agent

An intelligent stock analysis agent powered by FastAPI and LLM, providing AI-driven investment recommendations with technical analysis and sentiment analysis.

## Features

✨ **Core Capabilities:**
- 📊 **Real-time Stock Data**: Fetch current stock prices and historical data from Yahoo Finance
- 📈 **Technical Analysis**: Calculate RSI, MACD, Bollinger Bands, and trend analysis
- 🤖 **AI-Powered Recommendations**: Get buy/sell/hold recommendations with confidence scores
- 🔔 **Price Alerts**: Set price alerts above/below target prices
- 📰 **Sentiment Analysis**: Analyze news sentiment for informed decision-making
- 💼 **Portfolio Analysis**: Analyze multiple stocks as a portfolio
- 🌐 **RESTful API**: Easy-to-use REST API for integration

## Tech Stack

- **Backend**: FastAPI, Python 3.9+
- **Data Source**: Yahoo Finance (via yfinance)
- **LLM**: Mock LLM (easily extensible to OpenAI, Claude, etc.)
- **Technical Analysis**: pandas, numpy, ta-lib
- **Async**: asyncio, aiohttp

## Project Structure

```
Q/
├── config.py                    # Configuration management
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── .env.example                 # Environment variables example
├── src/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application
│   ├── data_fetcher.py          # Stock data fetching (Yahoo Finance)
│   ├── technical_analysis.py    # Technical indicators (RSI, MACD, BB)
│   ├── llm_agent.py             # LLM-based analysis (Mock implementation)
│   ├── sentiment_analysis.py    # News sentiment analysis
│   ├── alerts.py                # Price alert management
│   └── models.py                # Pydantic models
└── tests/
    └── (tests to be added)
```

## Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/qiminghui618-tech/Q.git
   cd Q
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

## Running the Application

### Development

```bash
python -m src.main
```

The API will be available at `http://localhost:8000`

### API Documentation

Access interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check
```bash
GET /health
```

### Stock Data
```bash
# Get current stock data
GET /api/v1/stock/{symbol}

# Get multiple stocks
GET /api/v1/stocks?symbols=AAPL,MSFT,GOOGL
```

### Technical Analysis
```bash
# Get technical indicators
GET /api/v1/analysis/{symbol}?period=3mo
```

### AI Recommendations
```bash
# Get AI-powered recommendation
GET /api/v1/recommendation/{symbol}?period=3mo

# Analyze portfolio
POST /api/v1/analyze-portfolio
Content-Type: application/json
{
  "symbols": ["AAPL", "MSFT", "GOOGL"],
  "include_sentiment": true
}
```

### Price Alerts
```bash
# Create alert
POST /api/v1/alerts
Content-Type: application/json
{
  "symbol": "AAPL",
  "alert_type": "above",
  "target_price": 150.00
}

# Get alerts
GET /api/v1/alerts
GET /api/v1/alerts?symbol=AAPL

# Delete alert
DELETE /api/v1/alerts/{alert_id}
```

### Sentiment Analysis
```bash
# Get news sentiment
GET /api/v1/sentiment/{symbol}
```

## Usage Examples

### Python

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Get stock data
response = requests.get(f"{BASE_URL}/stock/AAPL")
stock_data = response.json()
print(f"AAPL: ${stock_data['current_price']}")

# Get AI recommendation
response = requests.get(f"{BASE_URL}/recommendation/AAPL")
recommendation = response.json()
print(f"Recommendation: {recommendation['recommendation']}")
print(f"Confidence: {recommendation['confidence']}")

# Create price alert
response = requests.post(
    f"{BASE_URL}/alerts",
    json={
        "symbol": "AAPL",
        "alert_type": "above",
        "target_price": 150.00
    }
)
alert = response.json()
print(f"Alert created: {alert['alert_id']}")
```

### cURL

```bash
# Get stock data
curl http://localhost:8000/api/v1/stock/AAPL

# Get AI recommendation
curl http://localhost:8000/api/v1/recommendation/AAPL

# Create alert
curl -X POST http://localhost:8000/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "alert_type": "above", "target_price": 150.0}'
```

## Configuration

Edit `.env` file to customize:

```env
# LLM Configuration
LLM_PROVIDER=mock  # mock, openai, claude
LLM_MODEL=gpt-4
OPENAI_API_KEY=your_key_here

# Stock Analysis
DEFAULT_STOCKS=AAPL,MSFT,GOOGL,TSLA
ANALYSIS_INTERVAL=3600

# Alerts
PRICE_ALERT_CHECK_INTERVAL=300

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

## Understanding the Analysis

### Technical Indicators

- **RSI (Relative Strength Index)**: Measures momentum (0-100)
  - > 70: Overbought
  - < 30: Oversold
  - 30-70: Neutral

- **MACD (Moving Average Convergence Divergence)**: Trend and momentum
  - Positive histogram: Bullish
  - Negative histogram: Bearish

- **Bollinger Bands**: Volatility and price levels
  - Price near upper band: Possibly overbought
  - Price near lower band: Possibly oversold

- **Trend Analysis**: Based on moving averages
  - Strong Uptrend: Price > Short MA > Long MA
  - Uptrend: Short MA > Long MA
  - Strong Downtrend: Price < Short MA < Long MA
  - Downtrend: Short MA < Long MA

### AI Recommendation Signals

The AI agent considers:
- RSI levels
- Trend direction
- MACD signals
- Bollinger Bands positions
- News sentiment

**Recommendation Types:**
- **BUY**: Strong buy signals detected
- **SELL**: Strong sell signals detected
- **HOLD**: Mixed or neutral signals

## Extending to Real LLM

To integrate OpenAI or Claude:

1. Install the provider's SDK:
   ```bash
   pip install openai  # For OpenAI
   # or
   pip install anthropic  # For Claude
   ```

2. Add API key to `.env`:
   ```env
   OPENAI_API_KEY=your_key
   LLM_PROVIDER=openai
   ```

3. Implement the provider class in `src/llm_agent.py`

## Testing

```bash
# Run tests
pytest tests/

# With coverage
pytest --cov=src tests/
```

## Performance Tips

- Cache historical data locally
- Adjust `ANALYSIS_INTERVAL` based on your needs
- Use batch requests for multiple stocks
- Monitor API rate limits from Yahoo Finance

## Troubleshooting

### No data for stock symbol
- Verify the ticker symbol is correct
- Check internet connection
- Yahoo Finance may be rate limiting

### Missing technical indicators
- Ensure sufficient historical data (minimum 50 days)
- Check data quality

### Alerts not triggering
- Verify alert is created (GET /api/v1/alerts)
- Check background tasks are running
- Verify price thresholds are reasonable

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Roadmap

- [ ] Database integration (PostgreSQL)
- [ ] User authentication
- [ ] Email/SMS notifications
- [ ] Advanced portfolio optimization
- [ ] Machine learning models
- [ ] Real-time WebSocket updates
- [ ] Mobile app
- [ ] More LLM integrations

## License

MIT License - see LICENSE file for details

## Disclaimer

⚠️ **This is for educational purposes only. Not financial advice.**

Stock trading involves risk. Always:
- Do your own research
- Consult a financial advisor
- Never invest more than you can afford to lose
- Use this tool as a supplementary analysis tool, not the sole basis for decisions

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review API examples

## Acknowledgments

- yfinance: Yahoo Finance data
- FastAPI: Web framework
- pandas: Data analysis
- LLM providers: AI analysis capabilities
