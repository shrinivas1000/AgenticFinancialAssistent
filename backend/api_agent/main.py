import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from utils import get_stock_data, get_ticker_news
import uvicorn

app = FastAPI(
    title="Stock Data API",
    description="API for fetching stock data and news",
    version="1.0.0"
)

    
class TickerRequest(BaseModel):
    tickers: List[str]


def get_multi_data(tickers: List[str]):
    results = []
    for ticker in tickers:
        results.append(get_stock_data(ticker))
    return results

def get_multi_data_with_news(tickers: List[str], news_limit: int = 2):
    stock_data = get_multi_data(tickers)
    news_data = get_ticker_news(tickers, limit=news_limit)
    
    return {
        'stocks': stock_data,
        'news': news_data
    }


@app.get("/")
async def root():
    return {"message": "Stock Data API", "docs": "/docs"}

@app.post("/stocks")
async def get_stocks(request: TickerRequest):
    """Get stock data for multiple tickers"""
    if not request.tickers:
        raise HTTPException(status_code=400, detail="At least one ticker required")
    
    try:
        return {"stocks": get_multi_data(request.tickers)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stocks/{ticker}")
async def get_single_stock(ticker: str):
    """Get stock data for a single ticker"""
    try:
        stock_data = get_stock_data(ticker.upper())
        if "error" in stock_data:
            raise HTTPException(status_code=404, detail=f"Stock not found: {ticker}")
        return stock_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/combined")
async def get_combined_data(request: TickerRequest, news_limit: int = 2):
    """Get combined stock data and news"""
    if not request.tickers:
        raise HTTPException(status_code=400, detail="At least one ticker required")
    
    try:
        return get_multi_data_with_news(request.tickers, news_limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/quick")
async def quick_stocks(tickers: str):
    """Quick endpoint: /quick?tickers=AAPL,TSM,INFY"""
    ticker_list = [t.strip().upper() for t in tickers.split(",") if t.strip()]
    if not ticker_list:
        raise HTTPException(status_code=400, detail="Provide comma-separated tickers")
    
    try:
        return {"stocks": get_multi_data(ticker_list)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)