"""
DevOps Interview Bot - главный файл

Telegram бот для подготовки к собеседованиям DevOps Engineer
"""

import asyncio
import logging
import os
import sys
import json

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties

# Импорт handlers
from .handlers import training, mock_interview

# Импорт БД
from .db.models import init_db, get_session
from .db.crud import load_tasks_from_json, get_or_create_user

# Импорт планировщика
from .utils.cron import setup_scheduler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Получить токен из .env
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    logger.error("BOT_TOKEN not found in environment variables!")
    sys.exit(1)

# Создать бота и диспетчер
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    session = get_session()
    user = get_or_create_user(session, message.from_user.id, message.from_user.username)
    session.close()
    
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        f"Я — <b>DevOps Interview Bot</b>.\n"
        f"Помогу тебе подготовиться к собеседованию DevOps Engineer.\n\n"
        f"<b>Режимы:</b>\n"
        f"• /training — Тренировка (раз в час задача)\n"
        f"• /mock_interview — Мок-собес (30 мин, 3-5 задач)\n"
        f"• /task — Получить задачу сейчас\n"
        f"• /help — Помощь\n\n"
        f"Погнали! 🚀"
    )


@dp.message(lambda message: message.text == "/help")
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    await message.answer(
        "<b>📚 Команды бота:</b>\n\n"
        "<b>Тренировка:</b>\n"
        "• /training — Включить режим тренировки\n"
        "• /task — Получить задачу сейчас\n\n"
        "<b>Мок-собес:</b>\n"
        "• /mock_interview — Запустить мок-собес (30 мин)\n"
        "• /next_task — Следующая задача в собесе\n\n"
        "<b>Категории задач:</b>\n"
        "• Nginx (10 задач)\n"
        "• Bash/CLI (15 задач)\n"
        "• Kubernetes (10 задач)\n"
        "• Git (10 задач)\n"
        "• Docker (5 задач)\n\n"
        "<b>Сложность:</b> Junior, Middle, Senior\n\n"
        "Удачи на собесах! 💪"
    )


async def init_tasks_db():
    """Загрузить задачи из JSON в БД (один раз при запуске)"""
    tasks_file = os.path.join(os.path.dirname(__file__), 'tasks', 'tasks.json')
    
    if not os.path.exists(tasks_file):
        logger.error(f"Tasks file not found: {tasks_file}")
        return
    
    with open(tasks_file, 'r', encoding='utf-8') as f:
        tasks_data = json.load(f)
    
    session = get_session()
    load_tasks_from_json(session, tasks_data)
    session.close()
    
    logger.info(f"Loaded {len(tasks_data)} tasks into database")


async def main():
    """Главная функция запуска бота"""
    # Инициализировать БД
    logger.info("Initializing database...")
    init_db()
    
    # Загрузить задачи
    logger.info("Loading tasks...")
    await init_tasks_db()
    
    # Подключить роутеры
    dp.include_router(training.router)
    dp.include_router(mock_interview.router)
    
    # Настроить планировщик (пока пустой список пользователей)
    # В продакшене можно хранить подписанных пользователей в БД
    scheduler = setup_scheduler(bot, user_ids=[])
    scheduler.start()
    logger.info("Scheduler started")
    
    # Запустить бота
    logger.info("Starting bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
