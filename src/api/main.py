"""ATN API - Complete API with evaluation system"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from contextlib import asynccontextmanager
import sqlite3
import os
from datetime import datetime

DB_PATH = os.getenv("DATABASE_URL", "sqlite:///atn.db").replace("sqlite:///", "")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
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
    
    # Reputation log
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reputation_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            change INTEGER,
            reason TEXT,
            timestamp TEXT
        )
    ''')
    
    # Evaluations/Feedback table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user_id INTEGER,
            to_user_id INTEGER,
            rating INTEGER CHECK(rating >= 1 AND rating <= 5),
            comment TEXT,
            task_type TEXT,
            created_at TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    yield

app = FastAPI(
    title="Agent Trust Network API",
    description="Decentralized AI Agent Reputation System with Evaluations",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Models
class AgentCreate(BaseModel):
    telegram_id: str
    metadata_uri: str

class EvaluationCreate(BaseModel):
    from_user_id: int
    to_user_id: int
    rating: int
    comment: Optional[str] = None
    task_type: str = "general"

class EvaluationResponse(BaseModel):
    id: int
    from_user_id: int
    to_user_id: int
    rating: int
    comment: Optional[str]
    task_type: str
    created_at: str

class UserResponse(BaseModel):
    user_id: int
    username: Optional[str]
    first_name: str
    reputation_score: int
    tasks_completed: int
    avg_rating: float
    evaluation_count: int

# ============ EVALUATION ENDPOINTS ============

@app.post("/evaluations", response_model=dict)
async def create_evaluation(data: EvaluationCreate, db: sqlite3.Connection = Depends(get_db)):
    """Submit an evaluation for an agent"""
    # Verify target user exists
    cursor = db.execute("SELECT user_id, reputation_score FROM users WHERE user_id = ?", (data.to_user_id,))
    user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="Target user not found")
    
    # Insert evaluation
    cursor.execute('''
        INSERT INTO evaluations (from_user_id, to_user_id, rating, comment, task_type, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (data.from_user_id, data.to_user_id, data.rating, data.comment, data.task_type, datetime.now().isoformat()))
    
    # Update reputation (rating * 10 points)
    score_change = data.rating * 10
    cursor.execute("UPDATE users SET reputation_score = reputation_score + ? WHERE user_id = ?", 
                   (score_change, data.to_user_id))
    
    # Log reputation change
    cursor.execute("INSERT INTO reputation_log (user_id, change, reason, timestamp) VALUES (?, ?, ?, ?)",
                   (data.to_user_id, score_change, f"Evaluation: {data.task_type}", datetime.now().isoformat()))
    
    db.commit()
    
    return {"status": "success", "rating": data.rating, "score_awarded": score_change}

@app.get("/evaluations/{user_id}", response_model=List[dict])
async def get_user_evaluations(user_id: int, db: sqlite3.Connection = Depends(get_db)):
    """Get all evaluations for a user"""
    cursor = db.execute('''
        SELECT e.id, e.from_user_id, e.rating, e.comment, e.task_type, e.created_at,
               u.username, u.first_name
        FROM evaluations e
        JOIN users u ON e.from_user_id = u.user_id
        WHERE e.to_user_id = ?
        ORDER BY e.created_at DESC
    ''', (user_id,))
    
    return [
        {
            "id": row[0],
            "from_user_id": row[1],
            "from_username": row[6] or row[7],
            "rating": row[2],
            "comment": row[3],
            "task_type": row[4],
            "created_at": row[5]
        }
        for row in cursor.fetchall()
    ]

@app.get("/users/{user_id}/stats", response_model=UserResponse)
async def get_user_stats(user_id: int, db: sqlite3.Connection = Depends(get_db)):
    """Get user stats including ratings"""
    cursor = db.execute('''
        SELECT user_id, username, first_name, reputation_score, tasks_completed,
               (SELECT AVG(rating) FROM evaluations WHERE to_user_id = ?),
               (SELECT COUNT(*) FROM evaluations WHERE to_user_id = ?)
        FROM users WHERE user_id = ?
    ''', (user_id, user_id, user_id))
    
    row = cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": row[0],
        "username": row[1],
        "first_name": row[2],
        "reputation_score": row[3],
        "tasks_completed": row[4],
        "avg_rating": round(row[5] or 0, 2),
        "evaluation_count": row[6]
    }

@app.get("/leaderboard")
async def get_leaderboard(db: sqlite3.Connection = Depends(get_db), limit: int = Query(default=20, le=100)):
    """Get top agents by reputation"""
    cursor = db.execute('''
        SELECT user_id, username, first_name, reputation_score, tasks_completed,
               (SELECT AVG(rating) FROM evaluations WHERE to_user_id = users.user_id) as avg_rating
        FROM users ORDER BY reputation_score DESC LIMIT ?
    ''', (limit,))
    
    return {
        "leaderboard": [
            {
                "rank": i + 1,
                "user_id": row[0],
                "username": row[1] or row[2],
                "first_name": row[2],
                "reputation_score": row[3],
                "tasks_completed": row[4],
                "avg_rating": round(row[5] or 0, 2)
            }
            for i, row in enumerate(cursor.fetchall())
        ]
    }

@app.get("/agents/trending")
async def get_trending_agents(db: sqlite3.Connection = Depends(get_db)):
    """Get recently active agents with good ratings"""
    cursor = db.execute('''
        SELECT user_id, username, first_name, reputation_score,
               (SELECT AVG(rating) FROM evaluations WHERE to_user_id = users.user_id) as avg_rating,
               (SELECT COUNT(*) FROM evaluations WHERE to_user_id = users.user_id) as eval_count
        FROM users 
        WHERE is_agent = 1
        ORDER BY last_active DESC 
        LIMIT 10
    ''')
    
    return {
        "trending": [
            {
                "user_id": row[0],
                "username": row[1] or row[2],
                "reputation_score": row[3],
                "avg_rating": round(row[4] or 0, 2),
                "evaluation_count": row[5]
            }
            for row in cursor.fetchall()
        ]
    }

@app.get("/health")
async def health():
    return {"status": "ok", "service": "ATN API v2.0"}
