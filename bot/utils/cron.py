"""
Планировщик задач (cron) для отправки тренировочных задач

Используется apscheduler для асинхронных задач
Поддерживает разные частоты: hourly, daily, twice_daily, thrice_daily
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

logger = logging.getLogger(__name__)

# Глобальный scheduler (singleton)
_scheduler = None


def get_scheduler():
    """Получить глобальный scheduler"""
    return _scheduler


def setup_scheduler(bot):
    """
    Настроить планировщик задач и загрузить пользователей из БД
    
    Args:
        bot: aiogram Bot instance
    
    Returns:
        AsyncIOScheduler instance
    """
    global _scheduler
    
    _scheduler = AsyncIOScheduler()
    
    # Загрузить пользователей с включённой автоматической рассылкой
    from ..db.models import get_session
    from ..db.crud import get_users_with_auto_training
    
    session = get_session()
    users = get_users_with_auto_training(session)
    
    for user in users:
        add_user_to_scheduler(_scheduler, bot, user.user_id, user.auto_training_frequency)
    
    session.close()
    
    logger.info(f"Scheduler initialized with {len(users)} users")
    
    return _scheduler


def add_user_to_scheduler(scheduler: AsyncIOScheduler, bot, user_id: int, frequency: str):
    """
    Добавить пользователя в планировщик с выбранной частотой
    
    Args:
        scheduler: AsyncIOScheduler instance
        bot: aiogram Bot instance
        user_id: Telegram user ID
        frequency: Частота рассылки (hourly, daily, twice_daily, thrice_daily)
    """
    from ..handlers.training import send_scheduled_task
    
    # Определить триггер по частоте
    triggers = {
        'hourly': CronTrigger(minute=0, timezone='Europe/Moscow'),
        'daily': CronTrigger(hour=9, minute=0, timezone='Europe/Moscow'),
        'twice_daily': CronTrigger(hour='9,18', minute=0, timezone='Europe/Moscow'),
        'thrice_daily': CronTrigger(hour='9,14,20', minute=0, timezone='Europe/Moscow')
    }
    
    trigger = triggers.get(frequency, triggers['hourly'])
    
    scheduler.add_job(
        send_scheduled_task,
        trigger=trigger,
        args=[bot, user_id],
        id=f"training_task_{user_id}",
        replace_existing=True
    )
    logger.info(f"Added user {user_id} to scheduler (frequency: {frequency})")


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
