"""
Database initialization and migration management
"""

from .models import Base, Task, User, Progress, MockSession, init_db, get_session, get_db_engine
from .migrate import run_migrations

__all__ = [
    'Base',
    'Task',
    'User',
    'Progress',
    'MockSession',
    'init_db',
    'get_session',
    'get_db_engine',
    'run_migrations',
]


def initialize_database():
    """
    Полная инициализация БД:
    1. Создаёт таблицы (если их нет)
    2. Запускает миграции (для существующих БД)
    """
    # Create tables
    engine = init_db()
    
    # Run migrations
    import os
    db_path = os.getenv('DATABASE_PATH', 'data/devops_bot.db')
    run_migrations(db_path)
    
    return engine
