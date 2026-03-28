"""
CRUD операции для DevOps Interview Bot

Функции для работы с БД:
- Создание/получение пользователей
- Получение задач (случайные, по категории)
- Сохранение прогресса
- Работа с мок-сессиями
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timezone
import random

from .models import Task, User, Progress, MockSession


# ============= USERS =============

def get_or_create_user(session: Session, user_id: int, username: Optional[str] = None) -> User:
    """Получить или создать пользователя"""
    user = session.query(User).filter(User.user_id == user_id).first()
    if not user:
        user = User(user_id=user_id, username=username)
        session.add(user)
        session.commit()
    return user


def update_user_settings(session: Session, user_id: int, training_enabled: Optional[bool] = None, learning_enabled: Optional[bool] = None) -> User:
    """Обновить настройки пользователя"""
    user = session.query(User).filter(User.user_id == user_id).first()
    if not user:
        return None
    
    if training_enabled is not None:
        user.training_enabled = training_enabled
    if learning_enabled is not None:
        user.learning_enabled = learning_enabled
    
    session.commit()
    return user


def get_user_settings(session: Session, user_id: int) -> dict:
    """Получить настройки пользователя"""
    user = session.query(User).filter(User.user_id == user_id).first()
    if not user:
        return {'training_enabled': False, 'learning_enabled': False}
    
    return {
        'training_enabled': user.training_enabled,
        'learning_enabled': user.learning_enabled
    }


def update_learning_progress(session: Session, user_id: int, topic: str, card_num: int) -> User:
    """Обновить прогресс обучения пользователя (карусель карточек)"""
    user = session.query(User).filter(User.user_id == user_id).first()
    if not user:
        return None
    
    user.learning_topic = topic
    user.learning_card = card_num
    session.commit()
    return user


def get_learning_progress(session: Session, user_id: int) -> dict:
    """Получить прогресс обучения пользователя"""
    user = session.query(User).filter(User.user_id == user_id).first()
    if not user:
        return {'topic': None, 'card': 1}
    
    return {
        'topic': user.learning_topic,
        'card': user.learning_card or 1
    }


def reset_learning_progress(session: Session, user_id: int, topic: str) -> User:
    """Сбросить прогресс обучения (начать тему сначала)"""
    user = session.query(User).filter(User.user_id == user_id).first()
    if not user:
        return None
    
    user.learning_topic = topic
    user.learning_card = 1
    session.commit()
    return user


# ============= TASKS =============

def load_tasks_from_json(session: Session, json_data: List[dict]):
    """Загрузить задачи из JSON в БД (один раз при инициализации)"""
    for task_data in json_data:
        existing = session.query(Task).filter(Task.id == task_data['id']).first()
        if not existing:
            task = Task(
                id=task_data['id'],
                category=task_data['category'],
                difficulty=task_data['difficulty'],
                question=task_data['question'],
                solution=task_data['solution'],
                explanation=task_data['explanation'],
                time_limit=task_data['time_limit'],
                hints=task_data.get('hints', [])
            )
            session.add(task)
    session.commit()


def get_random_task(session: Session, user_id: int, category: Optional[str] = None) -> Optional[Task]:
    """Получить случайную задачу (не решённую пользователем)"""
    # Найти нерешённые задачи
    solved_task_ids = session.query(Progress.task_id).filter(
        Progress.user_id == user_id,
        Progress.solved == True
    ).all()
    solved_ids = [t[0] for t in solved_task_ids]
    
    query = session.query(Task).filter(Task.id.notin_(solved_ids))
    if category:
        query = query.filter(Task.category == category)
    
    tasks = query.all()
    return random.choice(tasks) if tasks else None


def get_task_by_id(session: Session, task_id: int) -> Optional[Task]:
    """Получить задачу по ID"""
    return session.query(Task).filter(Task.id == task_id).first()


def get_all_tasks(session: Session) -> List[Task]:
    """Получить все задачи"""
    return session.query(Task).all()


# ============= PROGRESS =============

def save_progress(
    session: Session,
    user_id: int,
    task_id: int,
    solved: bool,
    time_spent: Optional[int] = None
) -> Progress:
    """Сохранить прогресс по задаче"""
    progress = session.query(Progress).filter(
        Progress.user_id == user_id,
        Progress.task_id == task_id
    ).first()
    
    if progress:
        progress.solved = solved
        if time_spent is not None:
            progress.time_spent = time_spent
        progress.attempts += 1
        progress.last_attempt_at = datetime.now(timezone.utc)
    else:
        progress = Progress(
            user_id=user_id,
            task_id=task_id,
            solved=solved,
            time_spent=time_spent,
            attempts=1
        )
        session.add(progress)
    
    session.commit()
    return progress


def get_user_progress(session: Session, user_id: int) -> dict:
    """Получить статистику прогресса пользователя"""
    total_tasks = session.query(Task).count()
    solved_tasks = session.query(Progress).filter(
        Progress.user_id == user_id,
        Progress.solved == True
    ).count()
    
    return {
        'total_tasks': total_tasks,
        'solved_tasks': solved_tasks,
        'progress_percent': round((solved_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0
    }


# ============= MOCK SESSIONS =============

def create_mock_session(session: Session, user_id: int) -> MockSession:
    """Создать новую мок-сессию"""
    mock_session = MockSession(user_id=user_id)
    session.add(mock_session)
    session.commit()
    return mock_session


def complete_mock_session(
    session: Session,
    session_id: int,
    score: int,
    total_tasks: int,
    average_time: int,
    feedback: Optional[str] = None
):
    """Завершить мок-сессию с результатами"""
    mock_session = session.query(MockSession).filter(
        MockSession.session_id == session_id
    ).first()
    
    if mock_session:
        mock_session.completed_at = datetime.now(timezone.utc)
        mock_session.score = score
        mock_session.total_tasks = total_tasks
        mock_session.average_time = average_time
        mock_session.feedback = feedback
        session.commit()


def get_user_mock_stats(session: Session, user_id: int) -> dict:
    """Получить статистику мок-собесов пользователя"""
    sessions = session.query(MockSession).filter(
        MockSession.user_id == user_id,
        MockSession.completed_at.isnot(None)
    ).all()
    
    if not sessions:
        return {
            'total_sessions': 0,
            'average_score': 0,
            'best_score': 0,
            'average_time': 0
        }
    
    total_sessions = len(sessions)
    avg_score = sum(s.score / s.total_tasks * 100 for s in sessions) / total_sessions
    best_session = max(sessions, key=lambda s: s.score / s.total_tasks)
    avg_time = sum(s.average_time for s in sessions if s.average_time) / total_sessions
    
    return {
        'total_sessions': total_sessions,
        'average_score': round(avg_score, 1),
        'best_score': f"{best_session.score}/{best_session.total_tasks}",
        'average_time': round(avg_time)
    }
