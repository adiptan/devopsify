"""
Автотесты для новых категорий learning карточек
(TCP/IP, systemd, network utils, linux files, HTTP methods)
"""

import pytest
import os
import sys
import json

# Добавить путь к модулям бота
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture
def learning_cards():
    """Загрузить learning_cards.json"""
    cards_file = os.path.join(
        os.path.dirname(__file__),
        '..',
        'bot',
        'content',
        'learning_cards.json'
    )
    with open(cards_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def test_new_categories_exist(learning_cards):
    """Проверить что новые категории существуют"""
    new_topics = ['tcpip', 'systemd', 'network_utils', 'linux_files', 'http_methods']
    
    for topic in new_topics:
        assert topic in learning_cards, f"Категория '{topic}' не найдена"
        assert 'title' in learning_cards[topic], f"У категории '{topic}' нет title"
        assert 'cards' in learning_cards[topic], f"У категории '{topic}' нет cards"


def test_new_categories_count(learning_cards):
    """Проверить количество карточек в новых категориях"""
    expected_counts = {
        'tcpip': 5,
        'systemd': 5,
        'network_utils': 5,
        'linux_files': 5,
        'http_methods': 5
    }
    
    for topic, expected_count in expected_counts.items():
        cards = learning_cards[topic]['cards']
        actual_count = len(cards)
        assert actual_count == expected_count, \
            f"Категория '{topic}': ожидалось {expected_count} карточек, найдено {actual_count}"


def test_cards_structure(learning_cards):
    """Проверить структуру карточек (обязательные поля)"""
    new_topics = ['tcpip', 'systemd', 'network_utils', 'linux_files', 'http_methods']
    
    for topic in new_topics:
        cards = learning_cards[topic]['cards']
        
        for i, card in enumerate(cards, 1):
            # Обязательные поля
            assert 'id' in card, f"{topic} card #{i}: отсутствует поле 'id'"
            assert 'title' in card, f"{topic} card #{i}: отсутствует поле 'title'"
            assert 'content' in card, f"{topic} card #{i}: отсутствует поле 'content'"
            
            # Валидация значений
            assert card['id'] == i, f"{topic} card #{i}: неправильный id (ожидался {i}, найден {card['id']})"
            assert len(card['title']) > 0, f"{topic} card #{i}: пустой title"
            assert len(card['content']) > 50, f"{topic} card #{i}: content слишком короткий"


def test_total_cards_count(learning_cards):
    """Проверить общее количество карточек"""
    total = sum(len(cat['cards']) for cat in learning_cards.values())
    assert total == 80, f"Общее количество карточек: {total}, ожидалось 80 (55 старых + 25 новых)"


def test_old_categories_intact(learning_cards):
    """Проверить что старые категории не повреждены"""
    old_topics = {
        'nginx': 10,
        'bash': 15,
        'kubernetes': 10,
        'git': 10,
        'docker': 10
    }
    
    for topic, expected_count in old_topics.items():
        assert topic in learning_cards, f"Старая категория '{topic}' пропала!"
        cards = learning_cards[topic]['cards']
        assert len(cards) == expected_count, \
            f"Категория '{topic}': было {expected_count} карточек, стало {len(cards)}"


def test_card_ids_sequential(learning_cards):
    """Проверить что id карточек последовательные (1, 2, 3, 4, 5)"""
    new_topics = ['tcpip', 'systemd', 'network_utils', 'linux_files', 'http_methods']
    
    for topic in new_topics:
        cards = learning_cards[topic]['cards']
        ids = [card['id'] for card in cards]
        
        # Должны быть [1, 2, 3, 4, 5]
        expected_ids = list(range(1, len(cards) + 1))
        assert ids == expected_ids, \
            f"Категория '{topic}': неправильные id карточек. Ожидалось {expected_ids}, найдено {ids}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
