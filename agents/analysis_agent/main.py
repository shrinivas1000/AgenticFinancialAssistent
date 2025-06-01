from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
from collections import defaultdict
import re

app = FastAPI(title="Dynamic Analysis Agent")

class AnalysisRequest(BaseModel):
    stocks: List[Dict[str, Any]]
    news: List[Dict[str, Any]]

class AnalysisAgent:
    def __init__(self):
        self.positive_indicators = ['beat', 'surge', 'rise', 'gain', 'up', 'strong', 'growth', 'profit', 'revenue increase', 'bullish', 'positive']
        self.negative_indicators = ['miss', 'fall', 'drop', 'down', 'weak', 'loss', 'decline', 'concern', 'risk', 'bearish', 'negative']
        self.earnings_keywords = ['earnings', 'results', 'quarterly', 'revenue', 'profit', 'eps', 'estimate', 'guidance', 'outlook']
    
    def calculate_sector_allocation(self, stocks):
        sector_data = {}
        portfolio_total = 0
        
        for stock in stocks:
            if isinstance(stock.get('price'), (int, float)) and stock['price'] > 0:
                sector = stock.get('sector', 'Unclassified')
                price = stock['price']
                ticker = stock['ticker']
                
                if sector not in sector_data:
                    sector_data[sector] = {'stock_count': 0, 'total_value': 0, 'tickers': []}
                
                sector_data[sector]['stock_count'] += 1
                sector_data[sector]['total_value'] += price
                sector_data[sector]['tickers'].append(ticker)
                portfolio_total += price
        
        sector_breakdown = {}
        for sector in sector_data:
            data = sector_data[sector]
            if portfolio_total > 0:
                percentage = (data['total_value'] / portfolio_total * 100)
            else:
                percentage = 0
            
            sector_breakdown[sector] = {
                'allocation_percentage': round(percentage, 1),
                'number_of_holdings': data['stock_count'],
                'holdings': data['tickers'],
                'value': round(data['total_value'], 2)
            }
        
        return sector_breakdown, round(portfolio_total, 2)
    
    def analyze_market_sentiment(self, news):
        earnings_updates = []
        sentiment_analysis = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for article in news:
            title = article.get('title', '').lower()
            summary = article.get('summary', '').lower()
            content = f"{title} {summary}"
            
            has_earnings_content = any(keyword in content for keyword in self.earnings_keywords)
            
            positive_signals = sum(1 for indicator in self.positive_indicators if indicator in content)
            negative_signals = sum(1 for indicator in self.negative_indicators if indicator in content)
            
            if positive_signals > negative_signals:
                sentiment = 'positive'
                sentiment_analysis['positive'] += 1
            elif negative_signals > positive_signals:
                sentiment = 'negative'
                sentiment_analysis['negative'] += 1
            else:
                sentiment = 'neutral'
                sentiment_analysis['neutral'] += 1
            
            if has_earnings_content:
                earnings_updates.append({
                    'ticker': article.get('ticker'),
                    'title': article.get('title'),
                    'summary': article.get('summary'),
                    'sentiment': sentiment
                })
        
        return earnings_updates, sentiment_analysis
    
    def assess_concentration_risk(self, sector_breakdown):
        if not sector_breakdown:
            return {'risk_level': 'LOW', 'dominant_sector': None}
        
        highest_percentage = 0
        dominant_sector = None
        
        for sector in sector_breakdown:
            current_percentage = sector_breakdown[sector]['allocation_percentage']
            if current_percentage > highest_percentage:
                highest_percentage = current_percentage
                dominant_sector = sector
        
        if highest_percentage > 40:
            risk = 'HIGH'
        elif highest_percentage > 25:
            risk = 'MEDIUM'
        else:
            risk = 'LOW'
        
        return {
            'risk_level': risk,
            'dominant_sector': dominant_sector,
            'concentration_percentage': highest_percentage
        }
    
    def generate_key_insights(self, sector_breakdown, earnings_updates, sentiment_analysis, risk_assessment):
        insights = []
        
        if risk_assessment['dominant_sector'] and risk_assessment['dominant_sector'] != 'Unclassified':
            insights.append(f"Portfolio shows {risk_assessment['concentration_percentage']}% concentration in {risk_assessment['dominant_sector']} sector")
        
        if earnings_updates:
            active_tickers = []
            for update in earnings_updates:
                active_tickers.append(update['ticker'])
            unique_tickers = list(set(active_tickers))
            insights.append(f"Earnings activity detected for: {', '.join(unique_tickers)}")
        
        total_sentiment = sum(sentiment_analysis.values())
        if total_sentiment > 0:
            positive_ratio = sentiment_analysis['positive'] / total_sentiment
            if positive_ratio > 0.6:
                insights.append("Market sentiment trending positive")
            elif positive_ratio < 0.3:
                insights.append("Market sentiment showing caution")
        
        return insights
    
    def analyze(self, stocks, news):
        sector_breakdown, portfolio_value = self.calculate_sector_allocation(stocks)
        earnings_updates, sentiment_analysis = self.analyze_market_sentiment(news)
        risk_assessment = self.assess_concentration_risk(sector_breakdown)
        key_insights = self.generate_key_insights(sector_breakdown, earnings_updates, sentiment_analysis, risk_assessment)
        
        valid_stocks = []
        for s in stocks:
            if isinstance(s.get('price'), (int, float)):
                valid_stocks.append(s)
        
        
        stock_prices = {}
        for stock in stocks:
            if isinstance(stock.get('price'), (int, float)):
                stock_prices[stock['ticker']] = {
                    'price': stock['price'],
                    'currency': stock.get('currency', 'USD'),
                    'name': stock.get('longName', stock['ticker'])
                }

        return {
            "portfolio_overview": {
                "total_value": portfolio_value,
                "total_holdings": len(valid_stocks),
                "sector_allocation": sector_breakdown,
                "individual_stocks": stock_prices  
            },
            "risk_assessment": risk_assessment,
            "market_intelligence": {
                "earnings_updates": earnings_updates,
                "sentiment_breakdown": sentiment_analysis,
                "news_coverage": len(news)
            },
            "key_insights": key_insights
        }


agent = AnalysisAgent()

@app.post("/analyze")
def analyze_portfolio(request: AnalysisRequest):
    try:
        result = agent.analyze(request.stocks, request.news)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"message": "Portfolio Analysis Service"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)