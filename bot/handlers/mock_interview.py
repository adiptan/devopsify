"""
Режим мок-собеса - симуляция реального собеседования

Функционал:
- 30 минут на 3-5 задач
- Подсчёт статистики
- Feedback и рекомендации
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from datetime import datetime
import asyncio

from ..db.models import get_session
from ..db.crud import (
    get_or_create_user,
    get_random_task,
    create_mock_session,
    complete_mock_session,
    save_progress,
    get_task_by_id
)
from ..utils.scoring import calculate_feedback

router = Router()

# Активные мок-сессии (в продакшене лучше Redis)
active_mock_sessions = {}


@router.message(Command("mock_interview"))
async def cmd_mock_interview(message: Message):
    """Запустить мок-собес"""
    user_id = message.from_user.id
    
    # Проверить, не запущена ли уже сессия
    if user_id in active_mock_sessions:
        await message.answer(
            "⚠️ У тебя уже запущен мок-собес!\n\n"
            "Закончи текущую сессию или дождись таймаута."
        )
        return
    
    session = get_session()
    user = get_or_create_user(session, user_id, message.from_user.username)
    
    # Создать мок-сессию в БД
    mock_session = create_mock_session(session, user_id)
    
    # Инициализировать активную сессию
    active_mock_sessions[user_id] = {
        'session_id': mock_session.session_id,
        'started_at': datetime.now().timestamp(),
        'tasks': [],
        'current_task_index': 0,
        'score': 0,
        'total_time': 1800  # 30 минут в секундах
    }
    
    await message.answer(
        "🎯 <b>Мок-собес начался!</b>\n\n"
        "⏱ У тебя 30 минут на решение 3-5 задач.\n"
        "Постарайся решить как можно больше за отведённое время.\n\n"
        "Готов? Получи первую задачу: /next_task",
        parse_mode="HTML"
    )
    
    session.close()


@router.message(Command("next_task"))
async def cmd_next_task(message: Message):
    """Получить следующую задачу в мок-собесе"""
    user_id = message.from_user.id
    
    if user_id not in active_mock_sessions:
        await message.answer(
            "❌ Мок-собес не запущен.\n\n"
            "Запусти новую сессию: /mock_interview"
        )
        return
    
    session_data = active_mock_sessions[user_id]
    elapsed_time = datetime.now().timestamp() - session_data['started_at']
    
    # Проверить таймаут
    if elapsed_time > session_data['total_time']:
        await end_mock_session(message, user_id, timeout=True)
        return
    
    # Проверить лимит задач (максимум 5)
    if len(session_data['tasks']) >= 5:
        await end_mock_session(message, user_id, timeout=False)
        return
    
    db_session = get_session()
    task = get_random_task(db_session, user_id)
    
    if not task:
        await message.answer(
            "🎉 Все задачи решены!\n\n"
            "Завершаю мок-собес..."
        )
        await end_mock_session(message, user_id, timeout=False)
        db_session.close()
        return
    
    # Добавить задачу в сессию
    session_data['tasks'].append({
        'task_id': task.id,
        'started_at': datetime.now().timestamp()
    })
    
    remaining_time = int(session_data['total_time'] - elapsed_time)
    remaining_min = remaining_time // 60
    
    # Кнопки
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Готов показать решение", callback_data=f"mock_solution_{task.id}")
        ]
    ])
    
    await message.answer(
        f"📝 <b>Задача {len(session_data['tasks'])}</b>\n\n"
        f"<b>Категория:</b> {task.category.upper()}\n"
        f"<b>Сложность:</b> {task.difficulty}\n\n"
        f"<b>Задание:</b>\n{task.question}\n\n"
        f"⏱ Осталось времени: {remaining_min} мин\n\n"
        f"Когда решишь — нажми кнопку ниже!",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    
    db_session.close()


@router.callback_query(F.data.startswith("mock_solution_"))
async def mock_show_solution(callback: CallbackQuery):
    """Показать решение в мок-собесе"""
    task_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    
    if user_id not in active_mock_sessions:
        await callback.answer("Мок-собес не активен", show_alert=True)
        return
    
    session_data = active_mock_sessions[user_id]
    current_task = session_data['tasks'][-1]
    
    if current_task['task_id'] != task_id:
        await callback.answer("Это не текущая задача", show_alert=True)
        return
    
    db_session = get_session()
    task = get_task_by_id(db_session, task_id)
    
    if not task:
        await callback.answer("Задача не найдена", show_alert=True)
        db_session.close()
        return
    
    # Посчитать время на задачу
    time_spent = int(datetime.now().timestamp() - current_task['started_at'])
    current_task['time_spent'] = time_spent
    
    # Проверка: решил ли пользователь правильно (упрощённо - просто засчитываем)
    session_data['score'] += 1
    
    # Сохранить прогресс
    save_progress(db_session, user_id, task_id, solved=True, time_spent=time_spent)
    
    time_str = f"{time_spent // 60} мин {time_spent % 60} сек"
    
    await callback.message.edit_text(
        f"✅ <b>Отлично!</b>\n\n"
        f"<b>Эталонное решение:</b>\n<code>{task.solution}</code>\n\n"
        f"<b>Объяснение:</b>\n{task.explanation}\n\n"
        f"⏱ Твоё время: {time_str}\n\n"
        f"Следующая задача: /next_task",
        parse_mode="HTML"
    )
    
    await callback.answer()
    db_session.close()


async def end_mock_session(message: Message, user_id: int, timeout: bool = False):
    """Завершить мок-сессию с результатами"""
    if user_id not in active_mock_sessions:
        return
    
    session_data = active_mock_sessions[user_id]
    score = session_data['score']
    total_tasks = len(session_data['tasks'])
    
    # Посчитать среднее время
    times = [t.get('time_spent', 0) for t in session_data['tasks'] if 'time_spent' in t]
    average_time = sum(times) // len(times) if times else 0
    
    # Получить feedback
    feedback = calculate_feedback(score, total_tasks, average_time)
    
    db_session = get_session()
    complete_mock_session(
        db_session,
        session_data['session_id'],
        score,
        total_tasks,
        average_time,
        feedback
    )
    db_session.close()
    
    # Удалить активную сессию
    del active_mock_sessions[user_id]
    
    # Формат результатов
    result_emoji = "🎉" if score == total_tasks else "💪" if score >= total_tasks * 0.6 else "📚"
    timeout_text = "\n\n⏰ <b>Время вышло!</b>" if timeout else ""
    
    await message.answer(
        f"{result_emoji} <b>Мок-собес завершён!</b>{timeout_text}\n\n"
        f"📊 <b>Результаты:</b>\n"
        f"• Решено задач: {score}/{total_tasks}\n"
        f"• Среднее время: {average_time // 60} мин {average_time % 60} сек\n\n"
        f"💡 <b>Рекомендации:</b>\n{feedback}\n\n"
        f"Хочешь попробовать ещё раз? /mock_interview",
        parse_mode="HTML"
    )
