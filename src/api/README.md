# ATN API

FastAPI backend for Agent Trust Network.

## Setup

```bash
cd api
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints

### Agents
- `GET /agents` - List all agents
- `GET /agents/{id}` - Get agent details
- `POST /agents` - Register new agent

### Reputation
- `GET /reputation/{agent_id}` - Get reputation score
- `POST /reputation/evaluate` - Submit evaluation
- `GET /reputation/history/{agent_id}` - Get evaluation history

### Health
- `GET /health` - Health check
