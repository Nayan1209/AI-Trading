from fastapi import FastAPI
from .market_data.providers import MockMarketDataProvider
from .market_data.service import MarketDataService

app = FastAPI(title='AI Trading System', version='0.1.0')
market_data = MarketDataService(MockMarketDataProvider())

@app.get('/api/v1/health')
def health():
    return {'status':'ok','environment':'development'}

@app.get('/api/v1/market-data/latest')
def latest_market_data(symbol: str, exchange: str='NSE', timeframe: str='15m'):
    return market_data.latest(symbol, exchange, timeframe).model_dump(mode='json')
