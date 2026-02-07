"""ATN API - Complete API with database integration"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from contextlib import asynccontextmanager
import sqlite3
import os

# Database path
DB_PATH = os.getenv("DATABASE_URL", "sqlite:///atn.db").replace("sqlite:///", "")

def get_db():
    """Database connection dependency"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context for startup/shutdown"""
    # Startup - initialize database
    print("Starting ATN API...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Ensure tables exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            reputation_score INTEGER DEFAULT 0,
            tasks_completed INTEGER DEFAULT 0,
            registered_at TEXT,
            last_active TEXT,
            is_agent INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reputation_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            change INTEGER,
            reason TEXT,
            timestamp TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized")
    
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

# Pydantic models
class AgentCreate(BaseModel):
    telegram_id: str
    metadata_uri: str

class AgentResponse(BaseModel):
    token_id: int
    telegram_id: str
    metadata_uri: str
    registration_time: str
    active: bool

class ReputationUpdate(BaseModel):
    user_id: int
    score_change: int
    reason: str

class UserResponse(BaseModel):
    user_id: int
    username: Optional[str]
    first_name: str
    reputation_score: int
    tasks_completed: int
    is_agent: bool

# Routes
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "atn-api", "version": "1.0.0"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Agent Trust Network API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/agents", response_model=List[AgentResponse])
async def list_agents(db: sqlite3.Connection = Depends(get_db)):
    """List all registered agents"""
    cursor = db.execute("SELECT * FROM users WHERE is_agent = 1")
    rows = cursor.fetchall()
    return [
        {
            "token_id": row[0],  # user_id as token_id
            "telegram_id": str(row[0]),
            "metadata_uri": "",
            "registration_time": row[5] or "",
            "active": True
        }
        for row in rows
    ]

@app.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: int, db: sqlite3.Connection = Depends(get_db)):
    """Get agent details by ID"""
    cursor = db.execute("SELECT * FROM users WHERE user_id = ? AND is_agent = 1", (agent_id,))
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return {
        "token_id": row[0],
        "telegram_id": str(row[0]),
        "metadata_uri": "",
        "registration_time": row[5] or "",
        "active": True
    }

@app.get("/reputation/{user_id}")
async def get_reputation(user_id: int, db: sqlite3.Connection = Depends(get_db)):
    """Get reputation score for a user"""
    cursor = db.execute(
        "SELECT reputation_score, tasks_completed FROM users WHERE user_id = ?",
        (user_id,)
    )
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    
    score = row[0]
    tasks = row[1]
    
    # Calculate breakdown
    task_score = tasks * 10
    response_score = 0  # Would need response time tracking
    feedback_score = 0   # Would need feedback tracking
    behavior_score = 0   # Would need behavior tracking
    
    return {
        "user_id": user_id,
        "total_score": score,
        "task_score": task_score,
        "response_score": response_score,
        "feedback_score": feedback_score,
        "behavior_score": behavior_score,
        "evaluation_count": tasks
    }

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: sqlite3.Connection = Depends(get_db)):
    """Get user details"""
    cursor = db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": row[0],
        "username": row[1],
        "first_name": row[2],
        "reputation_score": row[3],
        "tasks_completed": row[4],
        "is_agent": bool(row[7])
    }

@app.get("/leaderboard")
async def get_leaderboard(db: sqlite3.Connection = Depends(get_db)):
    """Get top users by reputation"""
    cursor = db.execute(
        "SELECT user_id, username, first_name, reputation_score, tasks_completed "
        "FROM users ORDER BY reputation_score DESC LIMIT 10"
    )
    rows = cursor.fetchall()
    
    return {
        "leaderboard": [
            {
                "rank": i + 1,
                "user_id": row[0],
                "username": row[1],
                "first_name": row[2],
                "reputation_score": row[3],
                "tasks_completed": row[4]
            }
            for i, row in enumerate(rows)
        ]
    }

@app.post("/reputation/update")
async def update_reputation(data: ReputationUpdate, db: sqlite3.Connection = Depends(get_db)):
    """Update user reputation score"""
    cursor = db.execute(
        "UPDATE users SET reputation_score = reputation_score + ? WHERE user_id = ?",
        (data.score_change, data.user_id)
    )
    
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Log the change
    from datetime import datetime
    cursor.execute(
        "INSERT INTO reputation_log (user_id, change, reason, timestamp) VALUES (?, ?, ?, ?)",
        (data.user_id, data.score_change, data.reason, datetime.now().isoformat())
    )
    
    db.commit()
    
    return {
        "status": "success",
        "user_id": data.user_id,
        "new_score": data.score_change,
        "reason": data.reason
    }
