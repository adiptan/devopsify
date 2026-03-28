"""
Режим обучения - интерактивные лекции по темам

Функционал:
- Выбор темы (Nginx, Bash, K8s, Git, Docker)
- Мини-лекция (200-300 слов)
- 2-3 задачи по теме с детальными объяснениями
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from datetime import datetime
import json
import os

from ..db.models import get_session
from ..db.crud import get_or_create_user, get_task_by_id, save_progress

router = Router()

# Хранилище активных обучающих сессий
learning_sessions = {}

# Загрузить лекции из JSON
def load_lectures():
    """Загрузить лекции из JSON файла"""
    lectures_file = os.path.join(os.path.dirname(__file__), '..', 'content', 'lectures.json')
    with open(lectures_file, 'r', encoding='utf-8') as f:
        return json.load(f)


@router.message(Command("learning"))
async def cmd_learning(message: Message):
    """Запустить режим обучения"""
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
        "• <b>Nginx</b> — логи, конфигурация, анализ трафика\n"
        "• <b>Bash</b> — скрипты, CLI утилиты, автоматизация\n"
        "• <b>Kubernetes</b> — поды, сервисы, деплойменты\n"
        "• <b>Git</b> — версионирование, ветки, коммиты\n"
        "• <b>Docker</b> — контейнеры, образы, Dockerfile\n\n"
        "Каждая тема включает:\n"
        "✅ Мини-лекцию\n"
        "✅ 2-3 задачи\n"
        "✅ Детальные объяснения решений",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("learn_"))
async def show_lecture(callback: CallbackQuery):
    """Показать лекцию по выбранной теме"""
    topic = callback.data.replace("learn_", "")
    lectures = load_lectures()
    
    if topic not in lectures:
        await callback.answer("Тема не найдена", show_alert=True)
        return
    
    lecture_data = lectures[topic]
    user_id = callback.from_user.id
    
    # Сохранить сессию обучения
    learning_sessions[user_id] = {
        'topic': topic,
        'tasks': lecture_data['tasks'].copy(),
        'current_task_index': 0,
        'started_at': datetime.now().timestamp()
    }
    
    # Кнопка для начала задач
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Начать задачи", callback_data=f"start_learning_tasks_{topic}")]
    ])
    
    await callback.message.edit_text(
        f"📚 <b>Обучение: {lecture_data['title']}</b>\n\n"
        f"{lecture_data['lecture']}\n\n"
        f"Готов попробовать решить задачи? 💪",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    
    await callback.answer()


@router.callback_query(F.data.startswith("start_learning_tasks_"))
async def start_learning_tasks(callback: CallbackQuery):
    """Начать задачи по теме"""
    user_id = callback.from_user.id
    
    if user_id not in learning_sessions:
        await callback.answer("Сессия истекла. Начни заново: /learning", show_alert=True)
        return
    
    # Отправить первую задачу
    await send_learning_task(callback.message, user_id)
    await callback.answer()


async def send_learning_task(message: Message, user_id: int):
    """Отправить следующую задачу в режиме обучения"""
    if user_id not in learning_sessions:
        await message.edit_text("Сессия истекла. Начни заново: /learning")
        return
    
    session_data = learning_sessions[user_id]
    current_index = session_data['current_task_index']
    tasks = session_data['tasks']
    
    if current_index >= len(tasks):
        # Все задачи завершены
        await message.edit_text(
            f"🎉 <b>Тема '{session_data['topic']}' завершена!</b>\n\n"
            f"Отличная работа! Ты изучил все задачи по этой теме.\n\n"
            f"Выбери другую тему: /learning\n"
            f"Или попробуй мок-собес: /mock_interview",
            parse_mode="HTML"
        )
        del learning_sessions[user_id]
        return
    
    # Получить текущую задачу
    task_id = tasks[current_index]
    db_session = get_session()
    task = get_task_by_id(db_session, task_id)
    db_session.close()
    
    if not task:
        await message.edit_text("Ошибка: задача не найдена")
        return
    
    # Сохранить время начала задачи
    session_data['task_started_at'] = datetime.now().timestamp()
    
    # Кнопки
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Показать решение", callback_data=f"learning_solution_{task_id}"),
            InlineKeyboardButton(text="💡 Подсказка", callback_data=f"learning_hint_{task_id}")
        ]
    ])
    
    await message.edit_text(
        f"📝 <b>Задача {current_index + 1}/{len(tasks)}</b>\n\n"
        f"<b>Категория:</b> {task.category.upper()}\n"
        f"<b>Сложность:</b> {task.difficulty}\n\n"
        f"<b>Задание:</b>\n{task.question}\n\n"
        f"Попробуй решить самостоятельно, затем нажми кнопку!",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("learning_solution_"))
async def show_learning_solution(callback: CallbackQuery):
    """Показать детальное решение задачи в режиме обучения"""
    task_id = int(callback.data.replace("learning_solution_", ""))
    user_id = callback.from_user.id
    
    db_session = get_session()
    task = get_task_by_id(db_session, task_id)
    
    if not task:
        await callback.answer("Задача не найдена", show_alert=True)
        db_session.close()
        return
    
    # Посчитать время
    time_spent = None
    if user_id in learning_sessions and 'task_started_at' in learning_sessions[user_id]:
        time_spent = int(datetime.now().timestamp() - learning_sessions[user_id]['task_started_at'])
    
    # Сохранить прогресс
    save_progress(db_session, user_id, task_id, solved=True, time_spent=time_spent)
    db_session.close()
    
    # Подготовить детальное объяснение
    explanation_parts = task.explanation.split("\n")
    detailed_explanation = "\n\n".join([f"• {part.strip()}" for part in explanation_parts if part.strip()])
    
    # Альтернативы и best practices (из hints)
    extras = ""
    if task.hints:
        extras = "\n\n<b>💡 Дополнительно:</b>\n" + "\n".join([f"• {hint}" for hint in task.hints])
    
    time_str = f"{time_spent // 60} мин {time_spent % 60} сек" if time_spent else "?"
    
    # Кнопка для следующей задачи
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➡️ Следующая задача", callback_data="learning_next_task")]
    ])
    
    await callback.message.edit_text(
        f"✅ <b>Решение задачи #{task_id}</b>\n\n"
        f"<code>{task.solution}</code>\n\n"
        f"<b>📖 Детальное объяснение:</b>\n{detailed_explanation}"
        f"{extras}\n\n"
        f"⏱ Твоё время: {time_str}",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    
    # Переместить к следующей задаче
    if user_id in learning_sessions:
        learning_sessions[user_id]['current_task_index'] += 1
    
    await callback.answer()


@router.callback_query(F.data.startswith("learning_hint_"))
async def show_learning_hint(callback: CallbackQuery):
    """Показать подсказку в режиме обучения"""
    task_id = int(callback.data.replace("learning_hint_", ""))
    
    db_session = get_session()
    task = get_task_by_id(db_session, task_id)
    db_session.close()
    
    if not task or not task.hints:
        await callback.answer("Подсказок нет для этой задачи", show_alert=True)
        return
    
    hints_text = "\n".join([f"• {hint}" for hint in task.hints])
    
    await callback.answer(
        f"💡 Подсказка:\n\n{hints_text}",
        show_alert=True
    )


@router.callback_query(F.data == "learning_next_task")
async def next_learning_task(callback: CallbackQuery):
    """Перейти к следующей задаче"""
    user_id = callback.from_user.id
    await send_learning_task(callback.message, user_id)
    await callback.answer()
