"""
Автотесты для базы данных DevOps Interview Bot
"""

import pytest
import os
import sys
from datetime import datetime

# Добавить путь к модулям бота
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from bot.db.models import init_db, get_session, Task, User, Progress, MockSession
from bot.db.crud import (
    get_or_create_user,
    load_tasks_from_json,
    get_random_task,
    save_progress,
    get_user_progress,
    create_mock_session,
    complete_mock_session
)


@pytest.fixture
def test_db():
    """Временная БД для тестов"""
    import tempfile
    import atexit
    
    # Создать временный файл для БД
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_file.close()
    
    os.environ['DATABASE_PATH'] = temp_file.name
    engine = init_db()
    
    yield engine
    
    # Cleanup
    if 'DATABASE_PATH' in os.environ:
        del os.environ['DATABASE_PATH']
    try:
        os.unlink(temp_file.name)
    except:
        pass


def test_init_db(test_db):
    """Тест инициализации БД"""
    session = get_session()
    
    # Проверить, что таблицы созданы
    assert session.query(Task).count() >= 0
    assert session.query(User).count() >= 0
    
    session.close()


def test_create_user(test_db):
    """Тест создания пользователя"""
    session = get_session()
    
    user = get_or_create_user(session, user_id=12345, username="test_user")
    
    assert user.user_id == 12345
    assert user.username == "test_user"
    assert user.created_at is not None
    
    # Повторный вызов должен вернуть того же пользователя
    user2 = get_or_create_user(session, user_id=12345)
    assert user2.user_id == user.user_id
    
    session.close()


def test_load_tasks(test_db):
    """Тест загрузки задач из JSON"""
    session = get_session()
    
    tasks_data = [
        {
            "id": 1,
            "category": "bash",
            "difficulty": "junior",
            "question": "Показать текущую директорию",
            "time_limit": 60,
            "solution": "pwd",
            "explanation": "pwd - print working directory",
            "hints": ["Команда pwd"]
        }
    ]
    
    load_tasks_from_json(session, tasks_data)
    
    task = session.query(Task).filter(Task.id == 1).first()
    assert task is not None
    assert task.category == "bash"
    assert task.solution == "pwd"
    
    session.close()


def test_save_and_get_progress(test_db):
    """Тест сохранения и получения прогресса"""
    session = get_session()
    
    # Создать пользователя и задачу
    user = get_or_create_user(session, user_id=12345)
    tasks_data = [
        {
            "id": 1,
            "category": "bash",
            "difficulty": "junior",
            "question": "Test",
            "time_limit": 60,
            "solution": "test",
            "explanation": "test",
            "hints": []
        }
    ]
    load_tasks_from_json(session, tasks_data)
    
    # Сохранить прогресс
    save_progress(session, user_id=12345, task_id=1, solved=True, time_spent=120)
    
    # Проверить прогресс
    progress = get_user_progress(session, user_id=12345)
    assert progress['solved_tasks'] == 1
    assert progress['total_tasks'] >= 1
    
    session.close()


def test_mock_session(test_db):
    """Тест мок-собеса"""
    session = get_session()
    
    user = get_or_create_user(session, user_id=12345)
    
    # Создать мок-сессию
    mock = create_mock_session(session, user_id=12345)
    assert mock.session_id is not None
    assert mock.started_at is not None
    
    # Завершить сессию
    complete_mock_session(
        session,
        session_id=mock.session_id,
        score=3,
        total_tasks=5,
        average_time=180,
        feedback="Good job!"
    )
    
    # Проверить обновление
    updated_mock = session.query(MockSession).filter(
        MockSession.session_id == mock.session_id
    ).first()
    assert updated_mock.score == 3
    assert updated_mock.total_tasks == 5
    assert updated_mock.feedback == "Good job!"
    
    session.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
