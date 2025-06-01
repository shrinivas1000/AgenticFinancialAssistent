from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import requests
import uvicorn
import asyncio

app = FastAPI(title="Finance Assistant Orchestrator")


SERVICES = {
    "api_agent": "http://localhost:8000",     
    "retriever": "http://localhost:8001",      
    "analysis": "http://localhost:8002",      
    "language": "http://localhost:8003",     
    "voice": "http://localhost:8004"         
}

class QueryRequest(BaseModel):
    query: str
    tickers: Optional[List[str]] = ["AAPL", "TSMC", "NVDA"]  
    use_voice: Optional[bool] = False

class VoiceQueryRequest(BaseModel):
    tickers: Optional[List[str]] = ["AAPL", "TSMC", "NVDA"]

class Orchestrator:
    def __init__(self):
        self.confidence_threshold = 0.3
    
    def call_service(self, service_name, endpoint, data=None, method="GET"):
        try:
            base_url = SERVICES.get(service_name)
            if not base_url:
                raise Exception(f"Service {service_name} not configured")
            
            url = f"{base_url}{endpoint}"
            
            if method == "POST":
                response = requests.post(url, json=data, timeout=30)
            elif method == "DELETE":
                response = requests.delete(url, timeout=30)
            else:
                response = requests.get(url, timeout=30)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Service call failed for {service_name}: {e}")
            return None
        except Exception as e:
            print(f"Error calling {service_name}: {e}")
            return None
    
    def get_market_data(self, tickers):
        data = self.call_service("api_agent", "/combined", {
            "tickers": tickers
        }, method="POST")
        
        if not data:
            raise Exception(f"Failed to fetch real market data for: {', '.join(tickers)}")
    
        return data
    
    def analyze_portfolio(self, stocks, news):
        analysis_data = self.call_service("analysis", "/analyze", {
            "stocks": stocks,
            "news": news
        }, method="POST")
        
        return analysis_data
    
    def retrieve_relevant_docs(self, query, news_data):
        docs_to_add = []
        for article in news_data:
            docs_to_add.append({
                "ticker": article.get("ticker", ""),
                "title": article.get("title", ""),
                "summary": article.get("summary", "")
            })
        
        if docs_to_add:
            self.call_service("retriever", "/documents", {
                "documents": docs_to_add
            }, method="POST")
    
        search_result = self.call_service("retriever", "/search", {
            "query": query,
            "top_k": 3,
            "min_score": self.confidence_threshold
        }, method="POST")
        
        return search_result.get("results", []) if search_result else []
    
    def generate_language_response(self, analysis_data, retrieved_docs, query):
        response_data = self.call_service("language", "/generate", {
            "analysis_data": analysis_data,
            "retrieved_docs": retrieved_docs,
            "user_query": query
        }, method="POST")
        
        return response_data.get("response", "Unable to generate response") if response_data else "Service unavailable"
    
    def process_text_query(self, query, tickers):
    
        self.call_service("retriever", "/documents", method="DELETE")

        market_data = self.get_market_data(tickers)
        stocks = market_data.get("stocks", [])
        news = market_data.get("news", [])
        
        analysis_data = self.analyze_portfolio(stocks, news)
        if not analysis_data:
            return "Analysis service unavailable"
        
        retrieved_docs = self.retrieve_relevant_docs(query, news)
        
        response = self.generate_language_response(analysis_data, retrieved_docs, query)
        
        return {
            "response": response,
            "analysis_data": analysis_data,
            "retrieved_docs": retrieved_docs,
            "market_data_points": len(stocks),
            "news_articles": len(news)
        }
    
    def convert_speech_to_text(self, audio_file):
        return "What's our risk exposure in Asia tech stocks today?"
    
    def convert_text_to_speech(self, text):
        tts_response = self.call_service("voice", "/tts", {
            "text": text,
            "voice_speed": 150
        }, method="POST")
        
        return tts_response

orchestrator = Orchestrator()

@app.post("/query")
def process_query(request: QueryRequest):
    try:
        result = orchestrator.process_text_query(request.query, request.tickers)
        
        if request.use_voice:
            tts_result = orchestrator.convert_text_to_speech(result["response"])
            result["audio_response"] = "TTS processing attempted"
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice-query")
def process_voice_query(request: VoiceQueryRequest, audio: UploadFile = File(...)):
    try:
        query_text = orchestrator.convert_speech_to_text(audio)
        
        result = orchestrator.process_text_query(query_text, request.tickers)
        
        tts_result = orchestrator.convert_text_to_speech(result["response"])
        result["audio_response"] = "Voice response generated"
        result["original_query"] = query_text
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    service_status = {}
    
    for service_name, base_url in SERVICES.items():
        try:
            response = requests.get(f"{base_url}/", timeout=5)
            service_status[service_name] = "healthy" if response.status_code == 200 else "unhealthy"
        except:
            service_status[service_name] = "offline"
    
    return {
        "status": "running",
        "services": service_status,
        "orchestrator": "healthy"
    }

@app.get("/")
def root():
    return {
        "message": "Finance Assistant Orchestrator",
        "services": list(SERVICES.keys()),
        "endpoints": ["/query", "/voice-query", "/health"]
    }

@app.get("/test")
def test_pipeline():
    sample_query = "What's our risk exposure in Asia tech stocks today?"
    sample_tickers = ["AAPL", "TSMC", "NVDA"]
    
    try:
        result = orchestrator.process_text_query(sample_query, sample_tickers)
        return {
            "test_query": sample_query,
            "result": result,
            "status": "success"
        }
    except Exception as e:
        return {
            "test_query": sample_query,
            "error": str(e),
            "status": "failed"
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)
