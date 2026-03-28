"""
Автоматическая рассылка задач

Функционал:
- Настройка частоты рассылки (hourly, daily, twice_daily, thrice_daily)
- Включение/выключение автоматической рассылки
- Интеграция с APScheduler
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from ..db.models import get_session
from ..db.crud import (
    enable_auto_training, 
    disable_auto_training, 
    is_auto_training_enabled,
    get_or_create_user
)

router = Router()

# Маппинг частоты в читаемый текст
FREQUENCY_TEXT = {
    'hourly': 'Каждый час',
    'daily': 'Раз в день',
    'twice_daily': '2 раза в день',
    'thrice_daily': '3 раза в день'
}


def frequency_to_text(freq: str) -> str:
    """Преобразовать частоту в читаемый текст"""
    return FREQUENCY_TEXT.get(freq, freq)


@router.callback_query(F.data == "training_auto:menu")
async def auto_training_menu(callback: CallbackQuery):
    """Меню настройки автоматической рассылки"""
    session = get_session()
    user_id = callback.from_user.id
    
    # Проверить текущий статус
    enabled, frequency = is_auto_training_enabled(session, user_id)
    
    if enabled:
        # Рассылка включена — показать настройки
        status_text = f"📬 <b>Автоматическая рассылка задач</b>\n\n"
        status_text += f"Статус: ✅ Включена\n"
        status_text += f"Частота: {frequency_to_text(frequency)}\n\n"
        status_text += f"Ты будешь получать задачи автоматически по расписанию."
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⚙️ Изменить частоту", callback_data="training_auto:change_frequency")],
            [InlineKeyboardButton(text="❌ Отключить рассылку", callback_data="training_auto:disable")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="learning:menu")]
        ])
    else:
        # Рассылка выключена — предложить включить
        status_text = f"📬 <b>Автоматическая рассылка задач</b>\n\n"
        status_text += f"Статус: ❌ Отключена\n\n"
        status_text += f"Включи рассылку, чтобы получать задачи автоматически!\n"
        status_text += f"Выбери частоту:"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⏰ Каждый час", callback_data="training_auto:set:hourly")],
            [InlineKeyboardButton(text="📅 Раз в день (9:00)", callback_data="training_auto:set:daily")],
            [InlineKeyboardButton(text="📅 2 раза в день (9:00, 18:00)", callback_data="training_auto:set:twice_daily")],
            [InlineKeyboardButton(text="📅 3 раза в день (9:00, 14:00, 20:00)", callback_data="training_auto:set:thrice_daily")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="learning:menu")]
        ])
    
    await callback.message.edit_text(
        status_text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    
    await callback.answer()
    session.close()


@router.callback_query(F.data == "training_auto:change_frequency")
async def change_frequency_menu(callback: CallbackQuery):
    """Меню выбора новой частоты"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏰ Каждый час", callback_data="training_auto:set:hourly")],
        [InlineKeyboardButton(text="📅 Раз в день (9:00)", callback_data="training_auto:set:daily")],
        [InlineKeyboardButton(text="📅 2 раза в день (9:00, 18:00)", callback_data="training_auto:set:twice_daily")],
        [InlineKeyboardButton(text="📅 3 раза в день (9:00, 14:00, 20:00)", callback_data="training_auto:set:thrice_daily")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="training_auto:menu")]
    ])
    
    await callback.message.edit_text(
        "⚙️ <b>Выбери новую частоту рассылки:</b>",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    
    await callback.answer()


@router.callback_query(F.data.startswith("training_auto:set:"))
async def set_frequency(callback: CallbackQuery):
    """Включить рассылку с выбранной частотой"""
    frequency = callback.data.split(":")[2]  # training_auto:set:hourly -> hourly
    user_id = callback.from_user.id
    
    session = get_session()
    
    # Создать пользователя если не существует
    get_or_create_user(session, user_id, callback.from_user.username)
    
    # Включить рассылку
    enable_auto_training(session, user_id, frequency)
    
    # Добавить в scheduler (импортируем здесь чтобы избежать циклических импортов)
    from ..utils.cron import get_scheduler, add_user_to_scheduler
    from ..main import bot
    
    scheduler = get_scheduler()
    if scheduler:
        add_user_to_scheduler(scheduler, bot, user_id, frequency)
    
    await callback.message.edit_text(
        f"✅ <b>Рассылка включена!</b>\n\n"
        f"Частота: {frequency_to_text(frequency)}\n\n"
        f"Теперь ты будешь получать задачи автоматически.\n"
        f"Изменить настройки: /learning → Рассылка",
        parse_mode="HTML"
    )
    
    await callback.answer("Рассылка включена! ✅")
    session.close()


@router.callback_query(F.data == "training_auto:disable")
async def disable_training(callback: CallbackQuery):
    """Отключить автоматическую рассылку"""
    user_id = callback.from_user.id
    
    session = get_session()
    disable_auto_training(session, user_id)
    
    # Удалить из scheduler
    from ..utils.cron import get_scheduler, remove_user_from_scheduler
    
    scheduler = get_scheduler()
    if scheduler:
        remove_user_from_scheduler(scheduler, user_id)
    
    await callback.message.edit_text(
        f"❌ <b>Рассылка отключена</b>\n\n"
        f"Автоматические задачи больше не будут приходить.\n"
        f"Включить снова: /learning → Рассылка",
        parse_mode="HTML"
    )
    
    await callback.answer("Рассылка отключена")
    session.close()
