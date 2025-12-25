from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid

from src.graph import app as graph_app
from src.state import ResearchState

app = FastAPI(title="Quantum Gravity Agent API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RESEARCH_CACHE: Dict[str, Any] = {}

class ResearchRequest(BaseModel):
    objective: str
class ResearchResponse(BaseModel):
    session_id: str
    message: str

def run_agent_workflow(session_id: str, objective: str):
    """
    Background task that runs the LangGraph workflow.
    """
    print(f"[SERVER] Starting Background Task: {session_id}")
    
    initial_state = {
        "research_objective": objective,
        "current_hypothesis": {
            "status": "NEW",
            "iteration_count": 0,
            "title": "Initializing...",
            "description": "",
            "mathematical_formulation": "",
            "simulation_data": {}
        },
        "messages": ["System: Simulation initialized."],
        "literature_context": ""
    }
    
    RESEARCH_CACHE[session_id] = initial_state
    
    config = {"recursion_limit": 15}
    
    try:
        for output in graph_app.stream(initial_state, config=config):
            for node_name, state_update in output.items():
                
                current_cache = RESEARCH_CACHE[session_id]
                
                if "messages" in state_update:
                    pass
                    
                RESEARCH_CACHE[session_id].update(state_update)
                print(f"[UPDATE] Node: {node_name} finished.")
    
    except Exception as e:
        print(f"[ERROR] Simulation failed: {e}")
        RESEARCH_CACHE[session_id]["messages"].append(f"System Error: {str(e)}")
        RESEARCH_CACHE[session_id]["current_hypothesis"]["status"] = "ERROR"

@app.post("/api/research", response_model=ResearchResponse)
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    """
    Endpoint to kick off the AI. Returns a Session ID immediately.
    """
    session_id = str(uuid.uuid4())
    
    background_tasks.add_task(run_agent_workflow, session_id, request.objective)
    
    return {
        "session_id": session_id,
        "message": "Research simulation started."
    }

@app.get("/api/research/{session_id}")
async def get_research_status(session_id: str):
    """
    Frontend polls this endpoint every 2 seconds to get the latest logs and data.
    """
    if session_id not in RESEARCH_CACHE:
        raise HTTPException(status_code=404, detail="session not found")
    
    data = RESEARCH_CACHE[session_id]
    
    return data

@app.get("/")
def health_check():
    return {"status": "Quantum Gravity Interface Online"}