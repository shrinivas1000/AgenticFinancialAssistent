# Finance Assistant - Multi-Agent System

A sophisticated multi-agent AI system for financial portfolio analysis, risk assessment, and market intelligence with voice capabilities.

## Architecture

The system consists of 6 microservices orchestrated through a central coordinator:

- **Frontend (Streamlit)** - Port 8501: User interface and visualization
- **Orchestrator (FastAPI)** - Port 8005: Central coordination hub
- **API Agent** - Port 8000: Real-time financial data retrieval
- **Retriever Agent** - Port 8001: Document search and context
- **Analysis Agent** - Port 8002: Portfolio risk assessment
- **Language Agent** - Port 8003: Natural language response generation
- **Voice Agent** - Port 8004: Speech processing (STT/TTS)

## Features

**Real-time Portfolio Analysis** - Live market data and risk metrics
**Multi-Agent Coordination** - Distributed processing architecture
**Voice Interface** - Speech-to-text and text-to-speech capabilities
**Natural Language Processing** - Intelligent response generation
**Risk Assessment** - VaR, Sharpe ratio, beta calculations
**Market Intelligence** - News sentiment and technical analysis

## Quick Start

### Local Development

Install dependencies
pip install -r requirements.txt

Start all services
chmod +x run.sh
./run.sh

Access application
Frontend: http://localhost:8501
API Docs: http://localhost:8005/docs


### Docker Deployment

Build and run
docker build -t finance-assistant .
docker run -p 8501:8501 finance-assistant

Or use docker-compose
docker-compose up --build


## Technology Stack

**Backend**: FastAPI, Uvicorn, Pydantic
**Frontend**: Streamlit, Plotly
**AI/ML**: Sentence Transformers, Whisper, FAISS
**Data**: Pandas, NumPy, YFinance
**Voice**: gTTS, SpeechRecognition
**Deployment**: Docker, Docker Compose


## Deployment


**Local Setup**:
1. Clone repository
2. Install requirements: `pip install -r requirements.txt`
3. Run services: `./run.sh`
4. Access frontend: http://localhost:8501

**Docker**:
1. Build: `docker build -t finance-assistant .`
2. Run: `docker run -p 8501:8501 finance-assistant`





