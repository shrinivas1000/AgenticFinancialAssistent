echo "Starting all agents and orchestrator..."

uvicorn backend.api_agent.main:app --host 0.0.0.0 --port 8000 &
echo "API Agent started on port 8000"

uvicorn agents.retriever_agent.main:app --host 0.0.0.0 --port 8001 &
echo "Retriever Agent started on port 8001"

uvicorn agents.analysis_agent.main:app --host 0.0.0.0 --port 8002 &
echo "Analysis Agent started on port 8002"

uvicorn agents.language_agent.main:app --host 0.0.0.0 --port 8003 &
echo "Language Agent started on port 8003"

uvicorn agents.voice_agent.main:app --host 0.0.0.0 --port 8004 &
echo "Voice Agent started on port 8004"

uvicorn orchestrator:app --host 0.0.0.0 --port 8005 &
echo "Orchestrator started on port 8005"

wait
