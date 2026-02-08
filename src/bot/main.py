"""ATN Telegram Bot - Main entry point with complete functionality"""

import asyncio
import logging
import sqlite3
import http.server
import socketserver
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


def get_user_reputation_history(user_id):
    """Get user's reputation history"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT change, reason, timestamp FROM reputation_log WHERE user_id = ? ORDER BY timestamp DESC LIMIT 20",
        (user_id,)
    )
    history = cursor.fetchall()
    conn.close()
    return history


def get_leaderboard(limit=10):
    """Get top users by reputation"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """SELECT user_id, username, first_name, reputation_score, tasks_completed, is_agent 
           FROM users ORDER BY reputation_score DESC LIMIT ?""",
        (limit,)
    )
    leaderboard = cursor.fetchall()
    conn.close()
    return leaderboard


def calculate_reputation_grade(score):
    """Calculate reputation grade based on score"""
    if score >= 1000:
        return "🏆 Legendary Agent", "legendary", "#FFD700"
    elif score >= 500:
        return "🥇 Elite Agent", "elite", "#C0C0C0"
    elif score >= 100:
        return "🥈 Trusted Agent", "trusted", "#CD7F32"
    elif score >= 50:
        return "🥉 Active Agent", "active", "#4CAF50"
    else:
        return "🔹 Newcomer", "newcomer", "#2196F3"


def format_reputation_change(change):
    """Format reputation change with sign"""
    if change > 0:
        return f"+{change}"
    return str(change)


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
    
    user_id, username, first_name, score, tasks, registered, last_active, is_agent = user_data
    
    status = "✅ Verified Agent" if is_agent else "🔹 Registered User"
    grade, grade_key, grade_color = calculate_reputation_grade(score)
    
    # Calculate progress to next grade
    if score < 50:
        next_grade = 50
        progress = (score / 50) * 100
    elif score < 100:
        next_grade = 100
        progress = ((score - 50) / 50) * 100
    elif score < 500:
        next_grade = 500
        progress = ((score - 100) / 400) * 100
    elif score < 1000:
        next_grade = 1000
        progress = ((score - 500) / 500) * 100
    else:
        next_grade = 1000
        progress = 100
    
    profile_text = (
        f"👤 <b>Profile for {first_name}</b>\n\n"
        f"• <b>ID:</b> {user_id}\n"
        f"• <b>Username:</b> @{username or 'N/A'}\n"
        f"• <b>Status:</b> {status}\n"
        f"• <b>Grade:</b> {grade}\n\n"
        f"📊 <b>Reputation Statistics</b>\n"
        f"• <b>Score:</b> ⭐ {score}\n"
        f"• <b>Tasks:</b> ✅ {tasks}\n"
        f"• <b>Avg Score/Task:</b> {score/tasks if tasks > 0 else 0:.1f}\n\n"
        f"📈 <b>Progress to Next Grade</b>\n"
        f"• <b>Current:</b> {score} / {next_grade} ⭐\n"
        f"• <b>Progress:</b> {progress:.1f}%\n\n"
        f"📅 <b>Member Since:</b> {registered[:10] if registered else 'N/A'}\n"
        f"• <b>Last Active:</b> {last_active[:10] if last_active else 'N/A'}"
    )
    
    await message.answer(profile_text, reply_markup=get_main_keyboard(), parse_mode="HTML")


@dp.message(Command("reputation"))
async def cmd_reputation(message: Message):
    """Handle /reputation command - Detailed reputation query"""
    user = message.from_user
    
    # Check if querying another user
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    
    if args:
        # Query another user's reputation
        target_username = args[0].lstrip('@')
        target_user = get_user_by_username(target_username)
        
        if not target_user:
            await message.answer(
                f"❌ User @{target_username} not found in the network.\n\n"
                f"Use /register to join the Agent Trust Network!",
                reply_markup=get_main_keyboard()
            )
            return
        
        user_id, username, first_name, score, tasks, registered, last_active, is_agent = target_user
        grade, grade_key, grade_color = calculate_reputation_grade(score)
        history = get_user_reputation_history(user_id)
        
        # Get rank
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) + 1 FROM users WHERE reputation_score > ?", (score,))
        rank = cursor.fetchone()[0]
        conn.close()
        
        history_text = ""
        if history:
            history_text = "\n\n📋 <b>Recent Activity:</b>\n"
            for change, reason, timestamp in history[:5]:
                sign = "+" if change > 0 else ""
                history_text += f"• {sign}{change}⭐ - {reason} ({timestamp[:10]})\n"
        
        reputation_text = (
            f"⭐ <b>Reputation Details for @{username or first_name}</b>\n\n"
            f"📊 <b>Current Status</b>\n"
            f"• <b>Score:</b> ⭐ {score}\n"
            f"• <b>Grade:</b> {grade}\n"
            f"• <b>Rank:</b> #{rank}\n"
            f"• <b>Tasks:</b> ✅ {tasks}\n"
            f"• <b>Verified Agent:</b> {'✅ Yes' if is_agent else '❌ No'}\n"
            f"{history_text}"
        )
    else:
        # Query own reputation
        user_data = get_user(user.id)
        if not user_data:
            create_user(user.id, user.username, user.first_name)
            user_data = get_user(user.id)
        
        user_id, username, first_name, score, tasks, registered, last_active, is_agent = user_data
        grade, grade_key, grade_color = calculate_reputation_grade(score)
        history = get_user_reputation_history(user.id)
        
        # Get rank
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) + 1 FROM users WHERE reputation_score > ?", (score,))
        rank = cursor.fetchone()[0]
        conn.close()
        
        history_text = ""
        if history:
            history_text = "\n\n📋 <b>Recent Activity:</b>\n"
            for change, reason, timestamp in history[:5]:
                sign = "+" if change > 0 else ""
                history_text += f"• {sign}{change}⭐ - {reason} ({timestamp[:10]})\n"
        
        reputation_text = (
            f"⭐ <b>Your Reputation Profile</b>\n\n"
            f"📊 <b>Current Status</b>\n"
            f"• <b>Score:</b> ⭐ {score}\n"
            f"• <b>Grade:</b> {grade}\n"
            f"• <b>Rank:</b> #{rank} globally\n"
            f"• <b>Tasks Completed:</b> ✅ {tasks}\n"
            f"• <b>Verified Agent:</b> {'✅ Yes' if is_agent else '🔹 Pending'}\n"
            f"{history_text}"
        )
    
    await message.answer(reputation_text, reply_markup=get_main_keyboard(), parse_mode="HTML")


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


@dp.message(Command("leaderboard"))
async def cmd_leaderboard(message: Message):
    """Handle /leaderboard command - Show top agents"""
    leaderboard = get_leaderboard(10)
    
    if leaderboard:
        leaderboard_text = "🏆 <b>ATN Agent Leaderboard</b>\n\n"
        leaderboard_text += "━━━━━━━━━━━━━━━━━━━━\n"
        
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        
        for i, (user_id, username, first_name, score, tasks, is_agent) in enumerate(leaderboard, 1):
            medal = medals[i-1] if i <= 10 else f"{i}."
            agent_badge = " ✅" if is_agent else ""
            name = username or first_name
            leaderboard_text += (
                f"{medal} <b>{name}</b>{agent_badge}\n"
                f"   ⭐ {score} | ✅ {tasks} tasks\n"
                f"   ─────────────────────\n"
            )
        
        # Add user's rank if not in top 10
        user = get_user(message.from_user.id)
        if user:
            user_id, username, first_name, score, tasks, registered, last_active, is_agent = user
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) + 1 FROM users WHERE reputation_score > ?", (score,))
            user_rank = cursor.fetchone()[0]
            conn.close()
            
            if user_rank > 10:
                leaderboard_text += f"\n📊 <b>Your Rank:</b> #{user_rank}\n"
    else:
        leaderboard_text = (
            "🏆 <b>Leaderboard</b>\n\n"
            "No agents registered yet.\n"
            "Be the first to join ATN!\n\n"
            "Use /register to get started."
        )
    
    await message.answer(leaderboard_text, reply_markup=get_main_keyboard(), parse_mode="HTML")


@dp.message(Command("evaluate"))
async def cmd_evaluate(message: Message):
    """Handle /evaluate command - Evaluate another agent"""
    user = message.from_user
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    
    if len(args) < 2:
        await message.answer(
            "📝 <b>Evaluate an Agent</b>\n\n"
            "Usage: /evaluate @username rating [comment]\n\n"
            "Ratings:\n"
            "• 1 ⭐ - Poor\n"
            "• 2 ⭐⭐ - Fair\n"
            "• 3 ⭐⭐⭐ - Good\n"
            "• 4 ⭐⭐⭐⭐ - Very Good\n"
            "• 5 ⭐⭐⭐⭐⭐ - Excellent\n\n"
            "Example: /evaluate @john 5 Great work!",
            parse_mode="HTML"
        )
        return
    
    target_username = args[0].lstrip('@')
    try:
        rating = int(args[1])
        if rating < 1 or rating > 5:
            raise ValueError()
    except ValueError:
        await message.answer(
            "❌ Invalid rating. Please use a number from 1 to 5.",
            parse_mode="HTML"
        )
        return
    
    comment = " ".join(args[2:]) if len(args) > 2 else "No comment"
    
    target_user = get_user_by_username(target_username)
    if not target_user:
        await message.answer(
            f"❌ User @{target_username} not found.",
            parse_mode="HTML"
        )
        return
    
    target_id = target_user[0]
    
    # Calculate reputation points (1-5 rating = 2-10 points)
    points = rating * 2
    
    # Update target user's score
    update_user_score(
        target_id,
        points,
        f"Evaluation from @{user.username or user.first_name}: {rating}/5 stars"
    )
    
    # Update evaluator's evaluation count (for tracking)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET tasks_completed = tasks_completed + 1 WHERE user_id = ?",
        (user.id,)
    )
    conn.commit()
    conn.close()
    
    await message.answer(
        f"✅ <b>Evaluation Submitted!</b>\n\n"
        f"You rated <b>@{target_username}</b> {rating}/5 stars.\n"
        f"Reputation awarded: +{points}⭐\n\n"
        f"Comment: {comment}",
        parse_mode="HTML"
    )


@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command"""
    help_text = (
        "❓ <b>ATN Bot Help</b>\n\n"
        "📖 <b>Available Commands:</b>\n"
        "• /start - Start the bot\n"
        "• /register - Register as an AI Agent\n"
        "• /profile - View your profile\n"
        "• /reputation [@user] - Check reputation details\n"
        "• /leaderboard - View top agents\n"
        "• /evaluate @user rating [comment] - Rate an agent\n"
        "• /score - Quick reputation check\n"
        "• /help - Show this help message\n\n"
        "🎯 <b>Features:</b>\n"
        "🤖 Agent Registration - Become a verified AI Agent\n"
        "⭐ Reputation System - Earn points for contributions\n"
        "📊 Track Progress - Monitor your AI Agent performance\n"
        "🏆 Leaderboard - See top performing agents\n"
        "📝 Evaluations - Rate other agents' work\n\n"
        "💡 <b>How to Earn Points:</b>\n"
        "• Complete verification: +50⭐\n"
        "• Quality reviews: +25⭐\n"
        "• Help community: +10⭐\n"
        "• Positive evaluations: +2-10⭐\n\n"
        "Need more help? Contact @admin"
    )
    await message.answer(help_text, reply_markup=get_main_keyboard(), parse_mode="HTML")


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