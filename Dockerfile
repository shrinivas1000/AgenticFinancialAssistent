FROM python:3.9-slim

WORKDIR /app


RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY . .


EXPOSE 8000 8001 8002 8003 8004 8005 8501


RUN echo '#!/bin/bash\n\
echo "Starting all services..."\n\
uvicorn backend.api_agent.main:app --host 0.0.0.0 --port 8000 &\n\
uvicorn agents.retriever_agent.main:app --host 0.0.0.0 --port 8001 &\n\
uvicorn agents.analysis_agent.main:app --host 0.0.0.0 --port 8002 &\n\
uvicorn agents.language_agent.main:app --host 0.0.0.0 --port 8003 &\n\
uvicorn agents.voice_agent.main:app --host 0.0.0.0 --port 8004 &\n\
uvicorn orchestrator:app --host 0.0.0.0 --port 8005 &\n\
echo "All backend services started, starting Streamlit..."\n\
streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true\n\
' > start.sh && chmod +x start.sh

CMD ["./start.sh"]
