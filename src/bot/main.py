"""ATN Telegram Bot - Main entry point"""

import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message

# Configuration
from config import TELEGRAM_BOT_TOKEN

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Bot and Dispatcher
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command"""
    await message.answer(
        "🤖 Welcome to Agent Trust Network!\n\n"
        "Your decentralized AI Agent reputation system.\n\n"
        "Use /register to become an Agent\n"
        "Use /profile to view your profile\n"
        "Use /score to check your reputation score"
    )


@dp.message(Command("register"))
async def cmd_register(message: Message):
    """Handle /register command"""
    await message.answer("📝 Registration feature coming soon!\nYour Telegram ID has been recorded.")


@dp.message(Command("profile"))
async def cmd_profile(message: Message):
    """Handle /profile command"""
    user = message.from_user
    await message.answer(
        f"👤 Profile for {user.first_name}:\n\n"
        f"• Telegram ID: {user.id}\n"
        f"• Username: @{user.username or 'N/A'}\n"
        f"• Status: Pending Registration"
    )


@dp.message(Command("score"))
async def cmd_score(message: Message):
    """Handle /score command"""
    await message.answer("⭐ Your reputation score: 0\n\nStart completing tasks to earn reputation!")


async def main():
    """Main entry point"""
    logger.info("Starting ATN Bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
