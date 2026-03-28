"""
Settings - управление настройками бота

Функционал:
- Переключение режима тренировки (раз в час)
- Переключение режима обучения (интерактивные лекции)
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from ..db.models import get_session
from ..db.crud import get_or_create_user, update_user_settings, get_user_settings

router = Router()


@router.message(Command("settings"))
async def cmd_settings(message: Message):
    """Показать настройки"""
    session = get_session()
    user = get_or_create_user(session, message.from_user.id, message.from_user.username)
    settings = get_user_settings(session, user.user_id)
    session.close()
    
    # Кнопки с текущим состоянием
    training_text = "ВКЛ ✅" if settings['training_enabled'] else "ВЫКЛ"
    learning_text = "ВКЛ ✅" if settings['learning_enabled'] else "ВЫКЛ"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"🎓 Тренировка: {training_text}",
                callback_data="toggle_training"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"📚 Обучение: {learning_text}",
                callback_data="toggle_learning"
            )
        ]
    ])
    
    await message.answer(
        "⚙️ <b>Настройки</b>\n\n"
        f"🎓 <b>Тренировка:</b> {training_text}\n"
        "Отправляет случайную задачу раз в час.\n\n"
        f"📚 <b>Обучение:</b> {learning_text}\n"
        "Интерактивные лекции по темам DevOps.\n\n"
        "Нажми на кнопку чтобы переключить режим.",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@router.callback_query(F.data == "toggle_training")
async def toggle_training(callback: CallbackQuery):
    """Переключить режим тренировки"""
    session = get_session()
    user_id = callback.from_user.id
    settings = get_user_settings(session, user_id)
    
    # Переключить состояние
    new_state = not settings['training_enabled']
    update_user_settings(session, user_id, training_enabled=new_state)
    
    # Обновить кнопки
    settings = get_user_settings(session, user_id)
    session.close()
    
    training_text = "ВКЛ ✅" if settings['training_enabled'] else "ВЫКЛ"
    learning_text = "ВКЛ ✅" if settings['learning_enabled'] else "ВЫКЛ"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"🎓 Тренировка: {training_text}",
                callback_data="toggle_training"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"📚 Обучение: {learning_text}",
                callback_data="toggle_learning"
            )
        ]
    ])
    
    status = "включена" if new_state else "выключена"
    await callback.answer(f"Тренировка {status}", show_alert=False)
    
    await callback.message.edit_text(
        "⚙️ <b>Настройки</b>\n\n"
        f"🎓 <b>Тренировка:</b> {training_text}\n"
        "Отправляет случайную задачу раз в час.\n\n"
        f"📚 <b>Обучение:</b> {learning_text}\n"
        "Интерактивные лекции по темам DevOps.\n\n"
        "Нажми на кнопку чтобы переключить режим.",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@router.callback_query(F.data == "toggle_learning")
async def toggle_learning(callback: CallbackQuery):
    """Переключить режим обучения"""
    session = get_session()
    user_id = callback.from_user.id
    settings = get_user_settings(session, user_id)
    
    # Переключить состояние
    new_state = not settings['learning_enabled']
    update_user_settings(session, user_id, learning_enabled=new_state)
    
    # Обновить кнопки
    settings = get_user_settings(session, user_id)
    session.close()
    
    training_text = "ВКЛ ✅" if settings['training_enabled'] else "ВЫКЛ"
    learning_text = "ВКЛ ✅" if settings['learning_enabled'] else "ВЫКЛ"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"🎓 Тренировка: {training_text}",
                callback_data="toggle_training"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"📚 Обучение: {learning_text}",
                callback_data="toggle_learning"
            )
        ]
    ])
    
    status = "включено" if new_state else "выключено"
    await callback.answer(f"Обучение {status}", show_alert=False)
    
    await callback.message.edit_text(
        "⚙️ <b>Настройки</b>\n\n"
        f"🎓 <b>Тренировка:</b> {training_text}\n"
        "Отправляет случайную задачу раз в час.\n\n"
        f"📚 <b>Обучение:</b> {learning_text}\n"
        "Интерактивные лекции по темам DevOps.\n\n"
        "Нажми на кнопку чтобы переключить режим.",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
