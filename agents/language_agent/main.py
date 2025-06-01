from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn

app = FastAPI(title="Language Agent Service")

class LanguageRequest(BaseModel):
    analysis_data: Dict[str, Any]
    retrieved_docs: List[Dict[str, Any]]
    user_query: str

class LanguageAgent:
    def __init__(self):
        self.templates = {
            "portfolio_summary": "Your portfolio has {total_holdings} holdings worth ${total_value:,.2f}",
            "sector_allocation": "{sector} sector represents {percentage}% of your portfolio",
            "risk_level": "Portfolio concentration risk is {risk_level}",
            "earnings_update": "{ticker} has earnings activity with {sentiment} sentiment",
            "market_sentiment": "Overall market sentiment is {sentiment} based on recent news"
        }
    
    def format_portfolio_overview(self, portfolio_data):
        overview = portfolio_data.get('portfolio_overview', {})
        total_value = overview.get('total_value', 0)
        total_holdings = overview.get('total_holdings', 0)
        
        summary = self.templates["portfolio_summary"].format(
            total_holdings=total_holdings,
            total_value=total_value
        )
        

        sectors = overview.get('sector_allocation', {})
        sector_text = []
        for sector, data in sectors.items():
            if data['allocation_percentage'] > 5: 
                sector_text.append(
                    self.templates["sector_allocation"].format(
                        sector=sector,
                        percentage=data['allocation_percentage']
                    )
                )
        
        if sector_text:
            summary += ". " + ". ".join(sector_text)
        
        return summary
    
    def format_risk_assessment(self, risk_data):
        risk_level = risk_data.get('risk_level', 'LOW')
        dominant_sector = risk_data.get('dominant_sector')
        concentration = risk_data.get('concentration_percentage', 0)
        
        risk_text = self.templates["risk_level"].format(risk_level=risk_level)
        
        if dominant_sector and concentration > 25:
            risk_text += f" due to {concentration}% concentration in {dominant_sector}"
        
        return risk_text
    
    def format_earnings_updates(self, market_data):
        earnings = market_data.get('earnings_updates', [])
        if not earnings:
            return "No significant earnings updates today"
        
        updates = []
        for earning in earnings[:3]: 
            ticker = earning.get('ticker', 'N/A')
            sentiment = earning.get('sentiment', 'neutral')
            title = earning.get('title', '')
            
            if 'beat' in title.lower():
                performance = "beat estimates"
            elif 'miss' in title.lower():
                performance = "missed estimates"
            else:
                performance = "reported results"
            
            updates.append(f"{ticker} {performance}")
        
        return "Earnings highlights: " + ", ".join(updates)
    
    def format_market_sentiment(self, market_data):
        sentiment_data = market_data.get('sentiment_breakdown', {})
        
       
        if not sentiment_data:
            return "Market sentiment analysis in progress"
        
        total = sum(sentiment_data.values())
        
        if total == 0:
            return "Market sentiment analysis in progress"
        
        positive_ratio = sentiment_data.get('positive', 0) / total
        negative_ratio = sentiment_data.get('negative', 0) / total
        
        if positive_ratio > 0.6:
            sentiment = "positive with bullish indicators"
        elif negative_ratio > 0.6:
            sentiment = "cautious with bearish signals"
        else:
            sentiment = "mixed with balanced outlook"
        
        return f"Market sentiment is {sentiment} based on {total} news articles analyzed"
    
    def format_price_info(self, analysis_data):
        portfolio_data = analysis_data.get('portfolio_overview', {})
        individual_stocks = portfolio_data.get('individual_stocks', {})
        
        if not individual_stocks:
            return "Price information is currently unavailable"
        
        price_info = []
        for ticker, stock_data in individual_stocks.items():
            price = stock_data.get('price', 0)
            currency = stock_data.get('currency', 'USD')
            name = stock_data.get('name', ticker)
            
            if currency == 'INR':
                price_text = f"{ticker} ({name}) is trading at ₹{price:,.2f}"
            else:
                price_text = f"{ticker} ({name}) is trading at ${price:,.2f}"
            
            price_info.append(price_text)
        
        return "Current prices: " + "; ".join(price_info)


    
    def include_retrieved_context(self, retrieved_docs, main_response):
        if not retrieved_docs:
            return main_response
        
       
        news_items = []
        seen_titles = set()
        
        for doc in retrieved_docs[:4]: 
            ticker = doc.get('ticker', '')
            title = doc.get('title', '')
            summary = doc.get('summary', '')
            
            if title in seen_titles or not title:
                continue
                
            seen_titles.add(title)
            
            if ticker and title:
               
                news_item = f"**{ticker}**: {title}"
                if summary and len(summary) > 20:
                    
                    short_summary = summary[:150] + "..." if len(summary) > 150 else summary
                    news_item += f" - {short_summary}"
                news_items.append(news_item)
        
        if news_items:
            news_section = "\n\n**Latest News Updates:**\n" + "\n\n".join(news_items)
            return main_response + news_section
        
        return main_response



    
    def detect_query_focus(self, query):
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['price', 'current price', 'cost', 'value', 'trading at', 'worth']):
            return 'price'
        elif any(word in query_lower for word in ['risk', 'exposure', 'concentration']):
            return 'risk'
        elif any(word in query_lower for word in ['earnings', 'results', 'surprise']):
            return 'earnings'
        elif any(word in query_lower for word in ['sector', 'allocation', 'breakdown']):
            return 'sectors'
        elif any(word in query_lower for word in ['sentiment', 'market', 'news']):
            return 'sentiment'
        else:
            return 'overview'

    
    def generate_response(self, analysis_data, retrieved_docs, user_query):
        query_focus = self.detect_query_focus(user_query)
        
        
        response_parts = []
        if query_focus == 'price':
            price_text = self.format_price_info(analysis_data)
            response_parts.append(price_text)
        
        elif query_focus == 'risk':
            risk_text = self.format_risk_assessment(analysis_data.get('risk_assessment', {}))
            response_parts.append(risk_text)
            
        elif query_focus == 'earnings':
            earnings_text = self.format_earnings_updates(analysis_data.get('market_intelligence', {}))
            response_parts.append(earnings_text)
            
        elif query_focus == 'sectors':
            portfolio_text = self.format_portfolio_overview(analysis_data)
            response_parts.append(portfolio_text)
            
        elif query_focus == 'sentiment':
            sentiment_text = self.format_market_sentiment(analysis_data.get('market_intelligence', {}))
            response_parts.append(sentiment_text)
            
        else: 
            portfolio_text = self.format_portfolio_overview(analysis_data)
            earnings_text = self.format_earnings_updates(analysis_data.get('market_intelligence', {}))
            sentiment_text = self.format_market_sentiment(analysis_data.get('market_intelligence', {}))
            
        
            response_parts.extend([portfolio_text, earnings_text, sentiment_text])

        
        
        main_response = ". ".join(response_parts)
        
        
        final_response = self.include_retrieved_context(retrieved_docs, main_response)
        
        return final_response

language_agent = LanguageAgent()

@app.post("/generate")
def generate_response(request: LanguageRequest):
    try:
        response = language_agent.generate_response(
            analysis_data=request.analysis_data,
            retrieved_docs=request.retrieved_docs,
            user_query=request.user_query
        )
        return {
            "response": response,
            "query_focus": language_agent.detect_query_focus(request.user_query)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"message": "Language Agent Service"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)