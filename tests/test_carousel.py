"""
Тесты для карусели карточек обучения
"""

import pytest
import json
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Добавить корневую директорию в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from bot.handlers.learning import (
    load_learning_cards,
    get_card_keyboard,
    format_card_message,
    jump_to_card
)


class TestLearningCards:
    """Тесты для загрузки и структуры карточек"""
    
    def test_load_learning_cards(self):
        """Проверка загрузки карточек из JSON"""
        cards = load_learning_cards()
        
        # Проверить основные темы
        assert 'nginx' in cards
        assert 'bash' in cards
        assert 'kubernetes' in cards
        assert 'git' in cards
        assert 'docker' in cards
    
    def test_cards_structure(self):
        """Проверка структуры карточек"""
        cards = load_learning_cards()
        
        # Ожидаемое количество карточек по темам
        expected_counts = {
            'nginx': 10,
            'bash': 15,
            'kubernetes': 10,
            'git': 10,
            'docker': 10,
            'tcpip': 5,
            'systemd': 5,
            'network_utils': 5,
            'linux_files': 5,
            'http_methods': 5
        }
        
        for topic, topic_data in cards.items():
            # Проверить обязательные поля темы
            assert 'title' in topic_data
            assert 'cards' in topic_data
            assert 'tasks' in topic_data
            
            # Проверить количество карточек
            cards_count = len(topic_data['cards'])
            expected_count = expected_counts.get(topic, 10)  # Default 10 if not specified
            assert cards_count == expected_count, f"{topic} should have {expected_count} cards, but has {cards_count}"
            
            # Проверить структуру каждой карточки
            for card in topic_data['cards']:
                assert 'id' in card
                assert 'title' in card
                assert 'content' in card
                assert 'key_points' in card
                
                # Проверить длину контента (200-300 слов примерно)
                assert len(card['content']) > 100, f"Card {card['id']} content too short"
    
    def test_card_ids_sequential(self):
        """Проверка что ID карточек последовательные"""
        cards = load_learning_cards()
        
        for topic, topic_data in cards.items():
            card_ids = [card['id'] for card in topic_data['cards']]
            expected_ids = list(range(1, len(card_ids) + 1))
            assert card_ids == expected_ids, f"{topic} cards have non-sequential IDs"


class TestKeyboardGeneration:
    """Тесты для генерации клавиатур навигации"""
    
    def test_first_card_keyboard(self):
        """Первая карточка: нет кнопки 'Предыдущая'"""
        keyboard = get_card_keyboard('nginx', 1, 10)
        
        # Проверить что есть кнопка "Следующая"
        buttons_text = self._extract_button_texts(keyboard)
        assert "➡️ Следующая" in buttons_text
        assert "⬅️ Предыдущая" not in buttons_text
        assert "1/10" in buttons_text
    
    def test_last_card_keyboard(self):
        """Последняя карточка: нет кнопки 'Следующая'"""
        keyboard = get_card_keyboard('nginx', 10, 10)
        
        buttons_text = self._extract_button_texts(keyboard)
        assert "⬅️ Предыдущая" in buttons_text
        assert "➡️ Следующая" not in buttons_text
        assert "10/10" in buttons_text
    
    def test_middle_card_keyboard(self):
        """Средняя карточка: обе кнопки навигации"""
        keyboard = get_card_keyboard('nginx', 5, 10)
        
        buttons_text = self._extract_button_texts(keyboard)
        assert "⬅️ Предыдущая" in buttons_text
        assert "➡️ Следующая" in buttons_text
        assert "5/10" in buttons_text
    
    def test_keyboard_has_action_buttons(self):
        """Проверка наличия кнопок действий"""
        keyboard = get_card_keyboard('nginx', 5, 10)
        
        buttons_text = self._extract_button_texts(keyboard)
        assert "✅ Начать тесты" in buttons_text
        assert "🔄 Начать сначала" in buttons_text
        assert "🏠 В меню" in buttons_text
    
    def _extract_button_texts(self, keyboard):
        """Извлечь текст всех кнопок из клавиатуры"""
        texts = []
        for row in keyboard.inline_keyboard:
            for button in row:
                texts.append(button.text)
        return texts


class TestMessageFormatting:
    """Тесты для форматирования сообщений карточек"""
    
    def test_format_card_message_basic(self):
        """Проверка базового форматирования карточки"""
        cards = load_learning_cards()
        topic_data = cards['nginx']
        card = topic_data['cards'][0]
        
        message = format_card_message(topic_data, card, 1, 10)
        
        assert "📘" in message
        assert "Nginx" in message
        assert "1/10" in message
        assert card['title'] in message
        assert card['content'] in message
    
    def test_format_card_with_example(self):
        """Проверка форматирования с примером кода"""
        cards = load_learning_cards()
        topic_data = cards['nginx']
        card = topic_data['cards'][1]  # Вторая карточка обычно с примером
        
        message = format_card_message(topic_data, card, 2, 10)
        
        if card.get('example'):
            assert "<b>Пример:</b>" in message
            assert "<code>" in message
    
    def test_format_card_with_key_points(self):
        """Проверка форматирования с ключевыми пунктами"""
        cards = load_learning_cards()
        topic_data = cards['nginx']
        card = topic_data['cards'][0]
        
        message = format_card_message(topic_data, card, 1, 10)
        
        assert "<b>Ключевые моменты:</b>" in message
        for point in card['key_points']:
            assert point in message


class TestCardNavigation:
    """Тесты для навигации по карточкам"""
    
    @pytest.mark.asyncio
    async def test_jump_to_valid_card(self):
        """Переход к валидной карточке"""
        # Создать мок message
        message = Mock()
        message.from_user.id = 12345
        message.text = "/nginx 5"
        message.answer = MagicMock()
        
        # Мокнуть БД операции
        with patch('bot.handlers.learning.get_session') as mock_session:
            with patch('bot.handlers.learning.get_learning_progress') as mock_progress:
                with patch('bot.handlers.learning.update_learning_progress') as mock_update:
                    mock_progress.return_value = {'topic': None, 'card': 1}
                    
                    await jump_to_card(message, 'nginx')
                    
                    # Проверить что был вызван answer
                    assert message.answer.called
                    
                    # Проверить что прогресс был обновлён
                    mock_update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_jump_to_card_too_large(self):
        """Переход к несуществующей карточке (номер больше макс)"""
        message = Mock()
        message.from_user.id = 12345
        message.text = "/nginx 999"
        message.answer = MagicMock()
        
        with patch('bot.handlers.learning.get_session'):
            with patch('bot.handlers.learning.get_learning_progress') as mock_progress:
                with patch('bot.handlers.learning.update_learning_progress'):
                    mock_progress.return_value = {'topic': None, 'card': 1}
                    
                    await jump_to_card(message, 'nginx')
                    
                    # Проверить что был показан предупреждение
                    call_args = message.answer.call_args_list
                    assert len(call_args) >= 1
                    
                    # Первый вызов должен содержать предупреждение
                    warning_text = call_args[0][0][0]
                    assert "⚠️" in warning_text or "Всего" in warning_text
    
    @pytest.mark.asyncio
    async def test_jump_to_card_invalid_format(self):
        """Переход с неверным форматом номера"""
        message = Mock()
        message.from_user.id = 12345
        message.text = "/nginx abc"
        message.answer = MagicMock()
        
        await jump_to_card(message, 'nginx')
        
        # Проверить что был показан error
        assert message.answer.called
        error_text = message.answer.call_args[0][0]
        assert "❌" in error_text or "Неверный формат" in error_text


class TestDatabaseIntegration:
    """Тесты для интеграции с БД"""
    
    def test_crud_functions_exist(self):
        """Проверка что CRUD функции для прогресса существуют"""
        from bot.db import crud
        
        # Проверить что функции импортируются
        assert hasattr(crud, 'update_learning_progress')
        assert hasattr(crud, 'get_learning_progress')
        assert hasattr(crud, 'reset_learning_progress')
        
        # Проверить что функции вызываемые
        assert callable(crud.update_learning_progress)
        assert callable(crud.get_learning_progress)
        assert callable(crud.reset_learning_progress)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
