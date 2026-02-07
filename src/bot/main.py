"""ATN Telegram Bot - Main entry point with complete functionality"""

import asyncio
import logging
import sqlite3
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime

# Configuration
from config import TELEGRAM_BOT_TOKEN, DATABASE_URL

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Bot and Dispatcher
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# Database path
DB_PATH = DATABASE_URL.replace("sqlite:///", "")


def init_database():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create users table
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
    
    # Create transactions table for reputation tracking
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
    logger.info("Database initialized")


def get_user(user_id):
    """Get user from database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user


def create_user(user_id, username, first_name):
    """Create new user in database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute(
        "INSERT OR REPLACE INTO users (user_id, username, first_name, registered_at, last_active) VALUES (?, ?, ?, ?, ?)",
        (user_id, username, first_name, now, now)
    )
    conn.commit()
    conn.close()


def update_user_score(user_id, score_change, reason):
    """Update user reputation score"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    
    cursor.execute(
        "UPDATE users SET reputation_score = reputation_score + ?, last_active = ? WHERE user_id = ?",
        (score_change, now, user_id)
    )
    
    cursor.execute(
        "INSERT INTO reputation_log (user_id, change, reason, timestamp) VALUES (?, ?, ?, ?)",
        (user_id, score_change, reason, now)
    )
    
    conn.commit()
    conn.close()


def update_user_tasks(user_id):
    """Increment tasks completed count"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET tasks_completed = tasks_completed + 1 WHERE user_id = ?",
        (user_id,)
    )
    conn.commit()
    conn.close()


# Inline keyboard for main menu
def get_main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🤖 Register as Agent", callback_data="register_agent"),
            InlineKeyboardButton(text="📊 My Profile", callback_data="my_profile")
        ],
        [
            InlineKeyboardButton(text="⭐ Reputation", callback_data="reputation_info"),
            InlineKeyboardButton(text="📈 Leaderboard", callback_data="leaderboard")
        ],
        [
            InlineKeyboardButton(text="📋 Available Tasks", callback_data="tasks"),
            InlineKeyboardButton(text="❓ Help", callback_data="help")
        ]
    ])


@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command"""
    user = message.from_user
    
    # Create or update user in database
    if not get_user(user.id):
        create_user(user.id, user.username, user.first_name)
    
    welcome_text = (
        f"🤖 Welcome to Agent Trust Network, {user.first_name}!\n\n"
        f"Your decentralized AI Agent reputation system.\n\n"
        f"🌟 Earn reputation by completing tasks and helping others.\n"
        f"🎯 Build your AI Agent profile and track your reputation.\n\n"
        f"Use the menu below to get started:"
    )
    
    await message.answer(welcome_text, reply_markup=get_main_keyboard())


@dp.message(Command("register"))
async def cmd_register(message: Message):
    """Handle /register command - Register as an AI Agent"""
    user = message.from_user
    
    # Create user if not exists
    if not get_user(user.id):
        create_user(user.id, user.username, user.first_name)
    
    await message.answer(
        f"📝 Agent Registration for {user.first_name}\n\n"
        f"Telegram ID: {user.id}\n"
        f"Username: @{user.username or 'N/A'}\n\n"
        f"✅ Your registration request has been submitted!\n"
        f"You will receive a confirmation once processed.",
        reply_markup=get_main_keyboard()
    )
    
    # Update user's agent status
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_agent = 1 WHERE user_id = ?", (user.id,))
    conn.commit()
    conn.close()
    
    logger.info(f"User {user.id} registered as agent")


@dp.message(Command("profile"))
async def cmd_profile(message: Message):
    """Handle /profile command"""
    user = message.from_user
    
    user_data = get_user(user.id)
    if not user_data:
        create_user(user.id, user.username, user.first_name)
        user_data = get_user(user.id)
    
    username, first_name, score, tasks, registered, last_active, is_agent = user_data[1:]
    status = "✅ Verified Agent" if is_agent else "🔹 Registered User"
    
    profile_text = (
        f"👤 Profile for {first_name}\n\n"
        f"• Telegram ID: {user.id}\n"
        f"• Username: @{user.username or 'N/A'}\n"
        f"• Status: {status}\n"
        f"• Reputation Score: ⭐ {score}\n"
        f"• Tasks Completed: ✅ {tasks}\n"
        f"• Registered: {registered[:10] if registered else 'N/A'}\n"
        f"• Last Active: {last_active[:10] if last_active else 'N/A'}"
    )
    
    await message.answer(profile_text, reply_markup=get_main_keyboard())


@dp.message(Command("score"))
async def cmd_score(message: Message):
    """Handle /score command - Show reputation details"""
    user = message.from_user
    
    user_data = get_user(user.id)
    if not user_data:
        create_user(user.id, user.username, user.first_name)
        user_data = get_user(user.id)
    
    username, first_name, score, tasks, registered, last_active, is_agent = user_data[1:]
    
    # Determine rank based on score
    if score >= 1000:
        rank = "🏆 Legendary Agent"
    elif score >= 500:
        rank = "🥇 Elite Agent"
    elif score >= 100:
        rank = "🥈 Trusted Agent"
    else:
        rank = "🥉 Newcomer"
    
    score_text = (
        f"⭐ Your Reputation Score\n\n"
        f"Current Score: {score}\n"
        f"Rank: {rank}\n\n"
        f"📊 Score Breakdown:\n"
        f"• Tasks Completed: {tasks} × 10 = {tasks * 10}\n"
        f"• Community Contributions: 0\n\n"
        f"💡 Tips to increase your score:\n"
        f"• Complete AI agent tasks\n"
        f"• Provide quality feedback\n"
        f"• Help other community members"
    )
    
    await message.answer(score_text, reply_markup=get_main_keyboard())


@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command"""
    help_text = (
        "❓ ATN Bot Help\n\n"
        "Available Commands:\n"
        "• /start - Start the bot\n"
        "• /register - Register as an AI Agent\n"
        "• /profile - View your profile\n"
        "• /score - Check your reputation score\n"
        "• /help - Show this help message\n\n"
        "Features:\n"
        "🤖 Agent Registration - Become a verified AI Agent\n"
        "⭐ Reputation System - Earn points for contributions\n"
        "📊 Track Progress - Monitor your AI Agent performance\n\n"
        "Need more help? Contact @admin"
    )
    await message.answer(help_text, reply_markup=get_main_keyboard())


@dp.callback_query()
async def handle_callback(callback: CallbackQuery):
    """Handle inline button callbacks"""
    user = callback.from_user
    data = callback.data
    
    # Ensure user exists in database
    if not get_user(user.id):
        create_user(user.id, user.username, user.first_name)
    
    if data == "register_agent":
        await cmd_register(callback.message)
    elif data == "my_profile":
        await cmd_profile(callback.message)
    elif data == "reputation_info":
        await cmd_score(callback.message)
    elif data == "leaderboard":
        # Get top 5 users
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT first_name, reputation_score, tasks_completed FROM users ORDER BY reputation_score DESC LIMIT 5"
        )
        top_users = cursor.fetchall()
        conn.close()
        
        if top_users:
            leaderboard_text = "🏆 Top Agents Leaderboard\n\n"
            for i, (name, score, tasks) in enumerate(top_users, 1):
                leaderboard_text += f"{i}. {name}: ⭐ {score} (Tasks: {tasks})\n"
        else:
            leaderboard_text = "🏆 Leaderboard\n\nNo agents registered yet. Be the first!"
        
        await callback.message.answer(leaderboard_text, reply_markup=get_main_keyboard())
    elif data == "tasks":
        await callback.message.answer(
            "📋 Available Tasks\n\n"
            "🔹 Verification Task - Complete your agent verification (+50 pts)\n"
            "🔹 Quality Check - Review other agents' work (+25 pts)\n"
            "🔹 Community Help - Assist community members (+10 pts)\n\n"
            "Use /register to start earning rewards!",
            reply_markup=get_main_keyboard()
        )
    elif data == "help":
        await cmd_help(callback.message)
    
    await callback.answer()


async def main():
    """Main entry point"""
    logger.info("Starting ATN Bot...")
    init_database()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
