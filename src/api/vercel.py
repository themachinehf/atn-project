from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(title="ATN API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ATN API", "version": "2.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/api/v1/agents")
def list_agents():
    return {"agents": [], "total": 0}

@app.get("/api/v1/reputation/{agent_id}")
def get_reputation(agent_id: str):
    return {"agent_id": agent_id, "reputation": None}
