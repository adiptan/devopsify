"""
Планировщик задач (cron) для отправки тренировочных задач раз в час

Используется apscheduler для асинхронных задач
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

logger = logging.getLogger(__name__)


def setup_scheduler(bot, user_ids: list):
    """
    Настроить планировщик задач
    
    Args:
        bot: aiogram Bot instance
        user_ids: Список Telegram user ID для отправки задач
    
    Returns:
        AsyncIOScheduler instance
    """
    scheduler = AsyncIOScheduler()
    
    # Импорт функции отправки задачи
    from ..handlers.training import send_scheduled_task
    
    # Добавить задачу для каждого пользователя (раз в час)
    for user_id in user_ids:
        scheduler.add_job(
            send_scheduled_task,
            trigger=CronTrigger(minute=0),  # Каждый час в :00
            args=[bot, user_id],
            id=f"training_task_{user_id}",
            replace_existing=True
        )
        logger.info(f"Scheduled hourly task for user {user_id}")
    
    return scheduler


def add_user_to_scheduler(scheduler: AsyncIOScheduler, bot, user_id: int):
    """
    Добавить нового пользователя в планировщик
    
    Args:
        scheduler: AsyncIOScheduler instance
        bot: aiogram Bot instance
        user_id: Telegram user ID
    """
    from ..handlers.training import send_scheduled_task
    
    scheduler.add_job(
        send_scheduled_task,
        trigger=CronTrigger(minute=0),
        args=[bot, user_id],
        id=f"training_task_{user_id}",
        replace_existing=True
    )
    logger.info(f"Added user {user_id} to scheduler")


def remove_user_from_scheduler(scheduler: AsyncIOScheduler, user_id: int):
    """
    Удалить пользователя из планировщика
    
    Args:
        scheduler: AsyncIOScheduler instance
        user_id: Telegram user ID
    """
    job_id = f"training_task_{user_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        logger.info(f"Removed user {user_id} from scheduler")
