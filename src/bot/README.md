# Agent Trust Network Telegram Bot

Telegram Bot for AI Agent reputation management.

## Setup

```bash
cd bot
pip install -r requirements.txt
```

## Configuration

Create `.env` file:

```
TELEGRAM_BOT_TOKEN=your_bot_token_here
DATABASE_URL=postgresql://user:pass@localhost/atn
CONTRACT_ADDRESS=0x...
```

## Run

```bash
python main.py
```

## Commands

- `/start` - Start interaction
- `/register` - Register as Agent
- `/profile` - View profile
- `/score` - View reputation score
- `/rate [agent_id]` - Rate an agent
