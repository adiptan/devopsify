"""
Автотесты для настроек (settings)
"""

import pytest
import os
import sys
import tempfile

# Добавить путь к модулям бота
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from bot.db.models import init_db, get_session, User
from bot.db.crud import get_or_create_user, update_user_settings, get_user_settings


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


def test_default_settings(test_db):
    """Проверить что новый пользователь имеет дефолтные настройки"""
    session = get_session()
    
    user = get_or_create_user(session, user_id=12345, username="test_user")
    settings = get_user_settings(session, user_id=12345)
    
    # По умолчанию оба режима выключены
    assert settings['training_enabled'] == False
    assert settings['learning_enabled'] == False
    
    session.close()


def test_toggle_training(test_db):
    """Проверить переключение режима тренировки"""
    session = get_session()
    
    user = get_or_create_user(session, user_id=12345)
    
    # Включить тренировку
    update_user_settings(session, user_id=12345, training_enabled=True)
    settings = get_user_settings(session, user_id=12345)
    assert settings['training_enabled'] == True
    
    # Выключить тренировку
    update_user_settings(session, user_id=12345, training_enabled=False)
    settings = get_user_settings(session, user_id=12345)
    assert settings['training_enabled'] == False
    
    session.close()


def test_toggle_learning(test_db):
    """Проверить переключение режима обучения"""
    session = get_session()
    
    user = get_or_create_user(session, user_id=12345)
    
    # Включить обучение
    update_user_settings(session, user_id=12345, learning_enabled=True)
    settings = get_user_settings(session, user_id=12345)
    assert settings['learning_enabled'] == True
    
    # Выключить обучение
    update_user_settings(session, user_id=12345, learning_enabled=False)
    settings = get_user_settings(session, user_id=12345)
    assert settings['learning_enabled'] == False
    
    session.close()


def test_independent_toggles(test_db):
    """Проверить что режимы работают независимо"""
    session = get_session()
    
    user = get_or_create_user(session, user_id=12345)
    
    # Включить оба режима
    update_user_settings(session, user_id=12345, training_enabled=True, learning_enabled=True)
    settings = get_user_settings(session, user_id=12345)
    assert settings['training_enabled'] == True
    assert settings['learning_enabled'] == True
    
    # Выключить только тренировку
    update_user_settings(session, user_id=12345, training_enabled=False)
    settings = get_user_settings(session, user_id=12345)
    assert settings['training_enabled'] == False
    assert settings['learning_enabled'] == True  # обучение остаётся включённым
    
    session.close()


def test_settings_persist(test_db):
    """Проверить что настройки сохраняются между сессиями"""
    # Первая сессия: установить настройки
    session1 = get_session()
    user = get_or_create_user(session1, user_id=12345)
    update_user_settings(session1, user_id=12345, training_enabled=True, learning_enabled=True)
    session1.close()
    
    # Вторая сессия: проверить что настройки сохранились
    session2 = get_session()
    settings = get_user_settings(session2, user_id=12345)
    assert settings['training_enabled'] == True
    assert settings['learning_enabled'] == True
    session2.close()


def test_nonexistent_user_settings(test_db):
    """Проверить получение настроек несуществующего пользователя"""
    session = get_session()
    
    settings = get_user_settings(session, user_id=99999)
    
    # Должны вернуться дефолтные значения
    assert settings['training_enabled'] == False
    assert settings['learning_enabled'] == False
    
    session.close()


def test_update_nonexistent_user(test_db):
    """Проверить обновление настроек несуществующего пользователя"""
    session = get_session()
    
    result = update_user_settings(session, user_id=99999, training_enabled=True)
    
    # Должно вернуть None
    assert result is None
    
    session.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
