"""Configuration for ATN Bot"""

import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///atn.db")

# Blockchain Configuration
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "")
RPC_URL = os.getenv("RPC_URL", "https://rpc.example.com")

# Admin IDs (comma-separated)
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x]
