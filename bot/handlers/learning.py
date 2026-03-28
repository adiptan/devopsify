"""
Режим обучения - карусель карточек по темам

Функционал:
- Выбор темы (Nginx, Bash, K8s, Git, Docker)
- Карусель из 10-15 карточек с навигацией
- Сохранение прогресса (текущая карточка)
- Быстрый переход: /nginx 5, /bash 10, etc.
- Интеграция с задачами после прохождения теории
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from datetime import datetime
import json
import os

from ..db.models import get_session
from ..db.crud import (
    get_or_create_user,
    update_learning_progress,
    get_learning_progress,
    reset_learning_progress
)

router = Router()

# Загрузить карточки из JSON
def load_learning_cards():
    """Загрузить карточки обучения из JSON файла"""
    cards_file = os.path.join(os.path.dirname(__file__), '..', 'content', 'learning_cards.json')
    with open(cards_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_card_keyboard(topic: str, card_num: int, total_cards: int) -> InlineKeyboardMarkup:
    """Создать клавиатуру для карточки с навигацией"""
    buttons = []
    
    # Первая строка: навигация
    nav_row = []
    if card_num > 1:
        nav_row.append(InlineKeyboardButton(
            text="⬅️ Предыдущая",
            callback_data=f"carousel:prev:{topic}:{card_num}"
        ))
    
    nav_row.append(InlineKeyboardButton(
        text=f"{card_num}/{total_cards}",
        callback_data="carousel:noop"
    ))
    
    if card_num < total_cards:
        nav_row.append(InlineKeyboardButton(
            text="➡️ Следующая",
            callback_data=f"carousel:next:{topic}:{card_num}"
        ))
    
    buttons.append(nav_row)
    
    # Вторая строка: действия
    action_row = []
    
    if card_num == total_cards:
        # Последняя карточка: кнопка для перехода к тестам
        action_row.append(InlineKeyboardButton(
            text="✅ Начать тесты",
            callback_data=f"carousel:tests:{topic}"
        ))
    else:
        action_row.append(InlineKeyboardButton(
            text="✅ Начать тесты",
            callback_data=f"carousel:tests:{topic}"
        ))
    
    action_row.append(InlineKeyboardButton(
        text="🔄 Начать сначала",
        callback_data=f"carousel:restart:{topic}"
    ))
    
    buttons.append(action_row)
    
    # Третья строка: выход
    buttons.append([
        InlineKeyboardButton(text="🏠 В меню", callback_data="carousel:menu")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def format_card_message(topic_data: dict, card: dict, card_num: int, total_cards: int) -> str:
    """Форматировать сообщение карточки"""
    topic_title = topic_data['title']
    card_title = card['title']
    content = card['content']
    example = card.get('example', '')
    key_points = card.get('key_points', [])
    
    message = f"📘 <b>{topic_title}: {card_num}/{total_cards} — {card_title}</b>\n\n"
    message += f"{content}\n\n"
    
    if example:
        message += f"<b>Пример:</b>\n<code>{example}</code>\n\n"
    
    if key_points:
        message += "<b>Ключевые моменты:</b>\n"
        for point in key_points:
            message += f"• {point}\n"
    
    return message


@router.message(Command("learning"))
async def cmd_learning(message: Message):
    """Запустить режим обучения (выбор темы)"""
    session = get_session()
    user = get_or_create_user(session, message.from_user.id, message.from_user.username)
    session.close()
    
    # Кнопки выбора темы
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🌐 Nginx", callback_data="learn_nginx"),
            InlineKeyboardButton(text="⚡ Bash", callback_data="learn_bash")
        ],
        [
            InlineKeyboardButton(text="☸️ Kubernetes", callback_data="learn_kubernetes"),
            InlineKeyboardButton(text="🔀 Git", callback_data="learn_git")
        ],
        [
            InlineKeyboardButton(text="🐳 Docker", callback_data="learn_docker")
        ]
    ])
    
    await message.answer(
        "📚 <b>Режим обучения</b>\n\n"
        "Выбери тему для изучения:\n\n"
        "• <b>Nginx</b> — 10 карточек (от установки до best practices)\n"
        "• <b>Bash</b> — 15 карточек (команды, скрипты, автоматизация)\n"
        "• <b>Kubernetes</b> — 10 карточек (архитектура, поды, деплойменты)\n"
        "• <b>Git</b> — 10 карточек (основы, ветки, merge/rebase)\n"
        "• <b>Docker</b> — 10 карточек (контейнеры, образы, compose)\n\n"
        "Каждая тема включает:\n"
        "✅ Карусель теоретических карточек\n"
        "✅ Навигация ⬅️ ➡️\n"
        "✅ Практические задачи после теории\n\n"
        "Также доступны команды для быстрого перехода:\n"
        "<code>/nginx 5</code> — 5-я карточка Nginx\n"
        "<code>/bash 10</code> — 10-я карточка Bash\n"
        "<code>/k8s 3</code> — 3-я карточка Kubernetes",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("learn_"))
async def show_topic_first_card(callback: CallbackQuery):
    """Показать первую карточку выбранной темы"""
    topic = callback.data.replace("learn_", "")
    cards_data = load_learning_cards()
    
    if topic not in cards_data:
        await callback.answer("Тема не найдена", show_alert=True)
        return
    
    user_id = callback.from_user.id
    session = get_session()
    
    # Сохранить прогресс (начало темы)
    update_learning_progress(session, user_id, topic, 1)
    session.close()
    
    # Показать первую карточку
    topic_data = cards_data[topic]
    card = topic_data['cards'][0]
    total_cards = len(topic_data['cards'])
    
    message_text = format_card_message(topic_data, card, 1, total_cards)
    keyboard = get_card_keyboard(topic, 1, total_cards)
    
    await callback.message.edit_text(
        message_text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    
    await callback.answer()


@router.callback_query(F.data.startswith("carousel:"))
async def handle_carousel_action(callback: CallbackQuery):
    """Обработать действия карусели (prev, next, tests, restart, menu)"""
    parts = callback.data.split(":")
    action = parts[1]
    
    if action == "noop":
        # Кнопка-счётчик, ничего не делаем
        await callback.answer()
        return
    
    if action == "menu":
        # Вернуться в главное меню
        await cmd_learning(callback.message)
        await callback.answer()
        return
    
    topic = parts[2]
    cards_data = load_learning_cards()
    
    if topic not in cards_data:
        await callback.answer("Тема не найдена", show_alert=True)
        return
    
    topic_data = cards_data[topic]
    total_cards = len(topic_data['cards'])
    user_id = callback.from_user.id
    session = get_session()
    
    if action == "prev":
        current_card = int(parts[3])
        new_card = max(1, current_card - 1)
        update_learning_progress(session, user_id, topic, new_card)
        
        card = topic_data['cards'][new_card - 1]
        message_text = format_card_message(topic_data, card, new_card, total_cards)
        keyboard = get_card_keyboard(topic, new_card, total_cards)
        
        await callback.message.edit_text(
            message_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    
    elif action == "next":
        current_card = int(parts[3])
        new_card = min(total_cards, current_card + 1)
        update_learning_progress(session, user_id, topic, new_card)
        
        if new_card == total_cards:
            # Последняя карточка: поздравление
            card = topic_data['cards'][new_card - 1]
            message_text = format_card_message(topic_data, card, new_card, total_cards)
            message_text += f"\n\n🎓 <b>Поздравляю!</b> Ты прошёл всю теорию по {topic_data['title']}!"
            keyboard = get_card_keyboard(topic, new_card, total_cards)
            
            await callback.message.edit_text(
                message_text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        else:
            card = topic_data['cards'][new_card - 1]
            message_text = format_card_message(topic_data, card, new_card, total_cards)
            keyboard = get_card_keyboard(topic, new_card, total_cards)
            
            await callback.message.edit_text(
                message_text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
    
    elif action == "restart":
        # Начать тему сначала
        reset_learning_progress(session, user_id, topic)
        
        card = topic_data['cards'][0]
        message_text = format_card_message(topic_data, card, 1, total_cards)
        keyboard = get_card_keyboard(topic, 1, total_cards)
        
        await callback.message.edit_text(
            message_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    
    elif action == "tests":
        # Перейти к задачам по теме
        await callback.message.edit_text(
            f"🎯 <b>Задачи по теме: {topic_data['title']}</b>\n\n"
            f"Теперь время проверить знания на практике!\n\n"
            f"<i>Интеграция с задачами будет добавлена в следующей версии.</i>\n"
            f"Пока что используй команду <code>/task</code> для тренировки.\n\n"
            f"Выбери другую тему: /learning",
            parse_mode="HTML"
        )
    
    session.close()
    await callback.answer()


# ============= КОМАНДЫ БЫСТРОГО ПЕРЕХОДА =============

@router.message(Command("nginx"))
async def cmd_nginx_jump(message: Message):
    """Быстрый переход к карточке Nginx"""
    await jump_to_card(message, "nginx")


@router.message(Command("bash"))
async def cmd_bash_jump(message: Message):
    """Быстрый переход к карточке Bash"""
    await jump_to_card(message, "bash")


@router.message(Command("k8s", "kubernetes"))
async def cmd_k8s_jump(message: Message):
    """Быстрый переход к карточке Kubernetes"""
    await jump_to_card(message, "kubernetes")


@router.message(Command("git"))
async def cmd_git_jump(message: Message):
    """Быстрый переход к карточке Git"""
    await jump_to_card(message, "git")


@router.message(Command("docker"))
async def cmd_docker_jump(message: Message):
    """Быстрый переход к карточке Docker"""
    await jump_to_card(message, "docker")


async def jump_to_card(message: Message, topic: str):
    """Перейти к конкретной карточке темы"""
    cards_data = load_learning_cards()
    
    if topic not in cards_data:
        await message.answer("Тема не найдена. Используй /learning для выбора темы.")
        return
    
    topic_data = cards_data[topic]
    total_cards = len(topic_data['cards'])
    
    # Получить номер карточки из аргументов команды
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        # Если номер не указан, показать текущую или первую
        session = get_session()
        progress = get_learning_progress(session, message.from_user.id)
        session.close()
        
        if progress['topic'] == topic:
            card_num = progress['card']
        else:
            card_num = 1
    else:
        try:
            card_num = int(args[1])
        except ValueError:
            await message.answer(
                f"❌ Неверный формат. Используй: <code>/{topic} [номер]</code>\n"
                f"Пример: <code>/{topic} 5</code>",
                parse_mode="HTML"
            )
            return
    
    # Валидация номера карточки
    if card_num < 1:
        card_num = 1
        await message.answer(
            f"⚠️ Минимальный номер карточки: 1\n"
            f"Переход на первую карточку...",
            parse_mode="HTML"
        )
    elif card_num > total_cards:
        card_num = total_cards
        await message.answer(
            f"⚠️ Всего {total_cards} карточек в теме {topic_data['title']}\n"
            f"Переход на последнюю карточку...",
            parse_mode="HTML"
        )
    
    # Сохранить прогресс
    session = get_session()
    update_learning_progress(session, message.from_user.id, topic, card_num)
    session.close()
    
    # Показать карточку
    card = topic_data['cards'][card_num - 1]
    message_text = format_card_message(topic_data, card, card_num, total_cards)
    keyboard = get_card_keyboard(topic, card_num, total_cards)
    
    await message.answer(
        message_text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
