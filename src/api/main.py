"""ATN API - Main application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context for startup/shutdown"""
    # Startup
    print("Starting ATN API...")
    yield
    # Shutdown
    print("Shutting down ATN API...")

app = FastAPI(
    title="Agent Trust Network API",
    description="Decentralized AI Agent Reputation System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "atn-api"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Agent Trust Network API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/agents")
async def list_agents():
    """List all agents"""
    return {"agents": [], "total": 0}

@app.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get agent details"""
    return {"id": agent_id, "status": "pending"}

@app.get("/reputation/{agent_id}")
async def get_reputation(agent_id: str):
    """Get reputation score for an agent"""
    return {
        "agent_id": agent_id,
        "total_score": 0,
        "task_score": 0,
        "response_score": 0,
        "feedback_score": 0,
        "behavior_score": 0,
        "evaluation_count": 0
    }

@app.post("/reputation/evaluate")
async def submit_evaluation(data: dict):
    """Submit an evaluation"""
    return {"status": "success", "evaluation_id": 1}
