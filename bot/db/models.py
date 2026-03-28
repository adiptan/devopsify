"""
SQLAlchemy models для DevOps Interview Bot

Схема БД:
- tasks: задачи с решениями
- users: пользователи бота
- progress: прогресс решения задач
- mock_sessions: сессии мок-собеса
"""

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime, timezone
import os

Base = declarative_base()


class Task(Base):
    """Задачи для тренировки и мок-собеса"""
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True)
    category = Column(String(50), nullable=False)  # nginx, bash, k8s, git, docker
    difficulty = Column(String(20), nullable=False)  # junior, middle, senior
    question = Column(Text, nullable=False)
    solution = Column(Text, nullable=False)
    explanation = Column(Text, nullable=False)
    time_limit = Column(Integer, nullable=False)  # секунды
    hints = Column(JSON, nullable=True)  # список подсказок
    
    # Связи
    progress_records = relationship("Progress", back_populates="task")
    
    def __repr__(self):
        return f"<Task(id={self.id}, category={self.category}, difficulty={self.difficulty})>"


class User(Base):
    """Пользователи бота"""
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Связи
    progress_records = relationship("Progress", back_populates="user")
    mock_sessions = relationship("MockSession", back_populates="user")
    
    def __repr__(self):
        return f"<User(user_id={self.user_id}, username={self.username})>"


class Progress(Base):
    """Прогресс решения задач пользователем"""
    __tablename__ = 'progress'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    task_id = Column(Integer, ForeignKey('tasks.id'), nullable=False)
    solved = Column(Boolean, default=False)
    time_spent = Column(Integer, nullable=True)  # секунды
    attempts = Column(Integer, default=0)
    last_attempt_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Связи
    user = relationship("User", back_populates="progress_records")
    task = relationship("Task", back_populates="progress_records")
    
    def __repr__(self):
        return f"<Progress(user_id={self.user_id}, task_id={self.task_id}, solved={self.solved})>"


class MockSession(Base):
    """Сессии мок-собеса"""
    __tablename__ = 'mock_sessions'
    
    session_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)
    score = Column(Integer, default=0)  # количество решённых задач
    total_tasks = Column(Integer, default=0)  # всего задач в сессии
    average_time = Column(Integer, nullable=True)  # среднее время на задачу (сек)
    feedback = Column(Text, nullable=True)  # рекомендации
    
    # Связи
    user = relationship("User", back_populates="mock_sessions")
    
    def __repr__(self):
        return f"<MockSession(session_id={self.session_id}, user_id={self.user_id}, score={self.score}/{self.total_tasks})>"


# Database setup
def get_db_engine():
    """Создаёт engine для БД"""
    db_path = os.getenv('DATABASE_PATH', 'data/devops_bot.db')
    if db_path != ':memory:' and os.path.dirname(db_path):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return create_engine(f'sqlite:///{db_path}', echo=False)


def init_db():
    """Инициализирует БД (создаёт таблицы)"""
    engine = get_db_engine()
    Base.metadata.create_all(engine)
    return engine


def get_session():
    """Возвращает SQLAlchemy session"""
    engine = get_db_engine()
    Session = sessionmaker(bind=engine)
    return Session()
