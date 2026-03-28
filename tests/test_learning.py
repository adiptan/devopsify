"""
Автотесты для режима обучения (learning mode)
"""

import pytest
import os
import sys
import json
import tempfile

# Добавить путь к модулям бота
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from bot.db.models import init_db, get_session
from bot.db.crud import get_or_create_user, load_tasks_from_json, get_task_by_id


@pytest.fixture
def test_db():
    """Временная БД для тестов"""
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


@pytest.fixture
def lectures_data():
    """Загрузить лекции из JSON"""
    lectures_file = os.path.join(
        os.path.dirname(__file__),
        '..',
        'bot',
        'content',
        'lectures.json'
    )
    with open(lectures_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def test_lectures_structure(lectures_data):
    """Проверить структуру lectures.json"""
    required_topics = ['nginx', 'bash', 'kubernetes', 'git', 'docker']
    
    for topic in required_topics:
        assert topic in lectures_data, f"Тема '{topic}' отсутствует"
        
        lecture = lectures_data[topic]
        assert 'title' in lecture, f"У темы '{topic}' нет title"
        assert 'lecture' in lecture, f"У темы '{topic}' нет lecture"
        assert 'tasks' in lecture, f"У темы '{topic}' нет tasks"
        
        # Проверить что лекция не пустая
        assert len(lecture['lecture']) > 100, f"Лекция '{topic}' слишком короткая"
        
        # Проверить что есть задачи
        assert len(lecture['tasks']) >= 2, f"У темы '{topic}' мало задач"


def test_lecture_tasks_exist(test_db, lectures_data):
    """Проверить что все задачи из лекций существуют в БД"""
    session = get_session()
    
    # Загрузить все задачи в БД
    tasks_file = os.path.join(
        os.path.dirname(__file__),
        '..',
        'bot',
        'tasks',
        'tasks.json'
    )
    with open(tasks_file, 'r', encoding='utf-8') as f:
        tasks_data = json.load(f)
    
    load_tasks_from_json(session, tasks_data)
    
    # Проверить что все задачи из лекций существуют
    for topic, lecture in lectures_data.items():
        for task_id in lecture['tasks']:
            task = get_task_by_id(session, task_id)
            assert task is not None, f"Задача {task_id} из темы '{topic}' не найдена в БД"
            assert task.category == topic, f"Задача {task_id} имеет неправильную категорию"
    
    session.close()


def test_learning_session_flow(test_db):
    """Проверить полный флоу обучающей сессии"""
    session = get_session()
    
    # Создать пользователя
    user = get_or_create_user(session, user_id=12345, username="test_learner")
    
    # Симуляция обучающей сессии
    learning_session = {
        'topic': 'nginx',
        'tasks': [1, 2, 3],
        'current_task_index': 0
    }
    
    # Проверить что можем получить задачи
    tasks_file = os.path.join(
        os.path.dirname(__file__),
        '..',
        'bot',
        'tasks',
        'tasks.json'
    )
    with open(tasks_file, 'r', encoding='utf-8') as f:
        tasks_data = json.load(f)
    
    load_tasks_from_json(session, tasks_data)
    
    for task_id in learning_session['tasks']:
        task = get_task_by_id(session, task_id)
        assert task is not None
        assert task.explanation is not None, "У задачи нет объяснения"
        assert len(task.explanation) > 10, "Объяснение слишком короткое"
    
    session.close()


def test_all_tasks_have_explanations(test_db):
    """Проверить что у всех задач есть детальные объяснения"""
    session = get_session()
    
    # Загрузить задачи
    tasks_file = os.path.join(
        os.path.dirname(__file__),
        '..',
        'bot',
        'tasks',
        'tasks.json'
    )
    with open(tasks_file, 'r', encoding='utf-8') as f:
        tasks_data = json.load(f)
    
    for task_data in tasks_data:
        assert 'explanation' in task_data, f"Задача {task_data['id']} без explanation"
        assert len(task_data['explanation']) > 20, f"Задача {task_data['id']}: объяснение слишком короткое"
    
    session.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
