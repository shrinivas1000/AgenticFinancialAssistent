import yfinance as yf

def get_stock_data(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "ticker": ticker,
            "price": info.get("currentPrice") or info.get("regularMarketPrice") or "Unable to get price",
            "currency": info.get("currency", "Unknown Currency"),
            "longName": info.get("longName", "Unknown stock name"),
            "sector": info.get("sector", "Unable to get sector"),
        }
    except Exception as e:
        return {"error": str(e)}

def get_ticker_news(tickers, limit=3):
    all_news = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            news = stock.news
            company_info = stock.info
            company_name = company_info.get('longName', '').split()[0] if company_info.get('longName') else ''
            
            filtered_news = []
            for item in news[:limit*2]:  
                content = item.get('content', {})
                title = content.get('title', 'No title')
                summary = content.get('summary', content.get('description', 'No summary'))
                
                
                if (company_name and company_name.lower() in title.lower()) or ticker in title.upper() or ticker.lower() in title.lower():
                    filtered_news.append({
                        'ticker': ticker,
                        'title': title,
                        'summary': summary
                    })
            
           
            if not filtered_news:
                for item in news[:limit]:
                    content = item.get('content', {})
                    filtered_news.append({
                        'ticker': ticker,
                        'title': content.get('title', 'No title'),
                        'summary': content.get('summary', content.get('description', 'No summary'))
                    })
            
            all_news.extend(filtered_news[:limit])
        except:
            continue
    return all_news
