"""
Режим тренировки - отправляет задачи раз в час

Функционал:
- Отправка случайной задачи пользователю
- Кнопки: Показать решение, Подсказка, Пропустить
- Отслеживание прогресса
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from datetime import datetime
import json

from ..db.models import get_session
from ..db.crud import get_or_create_user, get_random_task, save_progress, get_user_progress, get_task_by_id

router = Router()

# Хранилище активных задач (в продакшене лучше Redis)
active_tasks = {}


@router.message(Command("training"))
async def cmd_training(message: Message):
    """Запустить режим тренировки"""
    session = get_session()
    user = get_or_create_user(session, message.from_user.id, message.from_user.username)
    
    # Получить прогресс
    progress = get_user_progress(session, user.user_id)
    
    await message.answer(
        f"🎯 <b>Режим тренировки</b>\n\n"
        f"Раз в час я буду присылать тебе задачу по DevOps.\n"
        f"Решай, учись, прокачивайся!\n\n"
        f"📊 Твой прогресс: {progress['solved_tasks']}/{progress['total_tasks']} "
        f"({progress['progress_percent']}%)\n\n"
        f"Получить задачу сейчас: /task",
        parse_mode="HTML"
    )
    session.close()


@router.message(Command("task"))
async def cmd_task(message: Message):
    """Получить случайную задачу"""
    session = get_session()
    user = get_or_create_user(session, message.from_user.id, message.from_user.username)
    
    task = get_random_task(session, user.user_id)
    
    if not task:
        await message.answer(
            "🎉 Поздравляю! Ты решил все задачи!\n\n"
            "Твой прогресс впечатляет. Попробуй мок-собес: /mock_interview"
        )
        session.close()
        return
    
    # Сохранить активную задачу
    active_tasks[user.user_id] = {
        'task_id': task.id,
        'started_at': datetime.now().timestamp(),
        'hint_shown': False
    }
    
    # Кнопки
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Показать решение", callback_data=f"solution_{task.id}"),
            InlineKeyboardButton(text="🤔 Подсказка", callback_data=f"hint_{task.id}")
        ],
        [
            InlineKeyboardButton(text="⏭️ Пропустить", callback_data=f"skip_{task.id}")
        ]
    ])
    
    await message.answer(
        f"📝 <b>Задача #{task.id}</b>\n\n"
        f"<b>Категория:</b> {task.category.upper()}\n"
        f"<b>Сложность:</b> {task.difficulty}\n"
        f"<b>Время:</b> {task.time_limit // 60} мин\n\n"
        f"<b>Задание:</b>\n{task.question}\n\n"
        f"Попробуй решить самостоятельно, затем нажми кнопку ниже!",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    
    session.close()


@router.callback_query(F.data.startswith("solution_"))
async def show_solution(callback: CallbackQuery):
    """Показать решение"""
    task_id = int(callback.data.split("_")[1])
    session = get_session()
    
    task = get_task_by_id(session, task_id)
    if not task:
        await callback.answer("Задача не найдена", show_alert=True)
        session.close()
        return
    
    # Посчитать время
    user_id = callback.from_user.id
    time_spent = None
    if user_id in active_tasks and active_tasks[user_id]['task_id'] == task_id:
        time_spent = int(datetime.now().timestamp() - active_tasks[user_id]['started_at'])
    
    # Сохранить прогресс
    save_progress(session, user_id, task_id, solved=True, time_spent=time_spent)
    
    # Получить обновлённый прогресс
    progress = get_user_progress(session, user_id)
    
    time_str = f"{time_spent // 60} мин {time_spent % 60} сек" if time_spent else "?"
    
    await callback.message.edit_text(
        f"✅ <b>Решение задачи #{task_id}</b>\n\n"
        f"<code>{task.solution}</code>\n\n"
        f"<b>Объяснение:</b>\n{task.explanation}\n\n"
        f"⏱ Время: {time_str}\n"
        f"📊 Прогресс: {progress['solved_tasks']}/{progress['total_tasks']} ({progress['progress_percent']}%)\n\n"
        f"Следующая задача: /task",
        parse_mode="HTML"
    )
    
    # Очистить активную задачу
    if user_id in active_tasks:
        del active_tasks[user_id]
    
    await callback.answer()
    session.close()


@router.callback_query(F.data.startswith("hint_"))
async def show_hint(callback: CallbackQuery):
    """Показать подсказку"""
    task_id = int(callback.data.split("_")[1])
    session = get_session()
    
    task = get_task_by_id(session, task_id)
    if not task:
        await callback.answer("Задача не найдена", show_alert=True)
        session.close()
        return
    
    # Отметить, что подсказка показана
    user_id = callback.from_user.id
    if user_id in active_tasks:
        active_tasks[user_id]['hint_shown'] = True
    
    hints_text = "\n".join([f"• {hint}" for hint in task.hints])
    
    await callback.answer(
        f"💡 Подсказка:\n{hints_text}",
        show_alert=True
    )
    
    session.close()


@router.callback_query(F.data.startswith("skip_"))
async def skip_task(callback: CallbackQuery):
    """Пропустить задачу"""
    task_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    session = get_session()
    
    # Сохранить прогресс как нерешённую
    save_progress(session, user_id, task_id, solved=False)
    
    await callback.message.edit_text(
        f"⏭️ Задача #{task_id} пропущена.\n\n"
        f"Не страшно! Попробуй другую: /task"
    )
    
    # Очистить активную задачу
    if user_id in active_tasks:
        del active_tasks[user_id]
    
    await callback.answer()
    session.close()


async def send_scheduled_task(bot, user_id: int):
    """
    Отправить задачу по расписанию (вызывается из cron)
    
    Args:
        bot: aiogram Bot instance
        user_id: Telegram user ID
    """
    session = get_session()
    user = get_or_create_user(session, user_id)
    
    # Проверить что тренировка включена
    if not user.training_enabled:
        session.close()
        return
    
    task = get_random_task(session, user_id)
    
    if not task:
        # Все задачи решены
        session.close()
        return
    
    # Сохранить активную задачу
    active_tasks[user_id] = {
        'task_id': task.id,
        'started_at': datetime.now().timestamp(),
        'hint_shown': False
    }
    
    # Кнопки
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Показать решение", callback_data=f"solution_{task.id}"),
            InlineKeyboardButton(text="🤔 Подсказка", callback_data=f"hint_{task.id}")
        ],
        [
            InlineKeyboardButton(text="⏭️ Пропустить", callback_data=f"skip_{task.id}")
        ]
    ])
    
    await bot.send_message(
        user_id,
        f"⏰ <b>Время новой задачи!</b>\n\n"
        f"📝 <b>Задача #{task.id}</b>\n\n"
        f"<b>Категория:</b> {task.category.upper()}\n"
        f"<b>Сложность:</b> {task.difficulty}\n"
        f"<b>Время:</b> {task.time_limit // 60} мин\n\n"
        f"<b>Задание:</b>\n{task.question}",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    
    session.close()
