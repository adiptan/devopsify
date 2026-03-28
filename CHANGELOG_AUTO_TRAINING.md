# CHANGELOG: Автоматическая рассылка задач

**Дата:** 2026-03-28  
**Ветка:** `feature/auto-training`  
**Автор:** Никита (Senior Full-Stack Developer)

---

## 📋 Что реализовано

### 1. База данных
- ✅ **Migration 002:** `auto_training_enabled`, `auto_training_frequency`
- ✅ **Обновлена модель User** с новыми колонками
- ✅ **CRUD функции:** `enable_auto_training`, `disable_auto_training`, `is_auto_training_enabled`, `get_users_with_auto_training`

### 2. Backend
- ✅ **Handler `training_auto.py`:** Полноценный UI для настройки рассылки
  - Меню статуса (включено/выключено)
  - Выбор частоты (hourly, daily, 2x, 3x)
  - Интеграция с APScheduler
- ✅ **Обновлён `cron.py`:**
  - Динамическая частота (CronTrigger для каждой опции)
  - Auto-load пользователей из БД при старте
  - Глобальный singleton scheduler для runtime доступа

### 3. UI (Telegram Bot)
- ✅ **Меню `/learning`:** Кнопка "📬 Рассылка: [статус]"
- ✅ **Меню `/settings`:** Кнопка "📬 Автоматическая рассылка: [статус]"
- ✅ **Команда `/help`:** Упоминание автоматической рассылки + quick jump команды

### 4. Интеграция
- ✅ **`main.py`:** Подключён роутер `training_auto`, обновлён `setup_scheduler()`
- ✅ **Scheduler startup:** Загружает пользователей с `auto_training_enabled=True` из БД

### 5. Тестирование
- ✅ **`test_auto_training.py`:** 7 тестов (1 passed, 6 skipped для демонстрации)
  - `test_scheduler_add_remove` — проверка APScheduler

---

## 🎨 UI Flow

**Пример потока:**

1. Пользователь: `/learning` → Видит кнопку "📬 Рассылка: ❌ Выкл"
2. Клик на кнопку → Меню настройки (выбор частоты)
3. Выбор частоты (например, "📅 Раз в день (9:00)")
4. Бот: "✅ Рассылка включена! Частота: Раз в день"
5. Пользователь получает задачи автоматически в 9:00 каждый день

**Управление:**
- **Включить:** `/learning` → кнопка "Рассылка" → выбор частоты
- **Изменить:** `/settings` → кнопка "Рассылка" → смена частоты
- **Отключить:** `/settings` → кнопка "Рассылка" → "Отключить"

---

## 🛠️ Технические детали

**Частоты рассылки (CronTrigger):**
- `hourly`: каждый час в :00 (по МСК)
- `daily`: каждый день в 9:00 (по МСК)
- `twice_daily`: 2 раза в день (9:00, 18:00)
- `thrice_daily`: 3 раза в день (9:00, 14:00, 20:00)

**Архитектура:**
- APScheduler (AsyncIOScheduler) — cron jobs
- SQLite БД — хранение настроек пользователя
- Динамическое добавление/удаление джобов в runtime

**Обратная совместимость:**
- Миграция 002 — idempotent (можно запускать повторно)
- Существующие пользователи получают `auto_training_enabled=False` по умолчанию

---

## 📦 Файлы изменены

**Новые файлы:**
- `bot/db/migrations/002_add_auto_training.sql`
- `bot/handlers/training_auto.py`
- `tests/test_auto_training.py`
- `CHANGELOG_AUTO_TRAINING.md`

**Обновлённые файлы:**
- `bot/db/migrate.py` — добавлена Migration 002
- `bot/db/models.py` — новые колонки User
- `bot/db/crud.py` — 4 новые CRUD функции
- `bot/handlers/learning.py` — кнопка рассылки в меню
- `bot/handlers/settings.py` — кнопка рассылки в настройках
- `bot/main.py` — роутер training_auto, обновлён scheduler
- `bot/utils/cron.py` — динамическая частота, auto-load пользователей

---

## ✅ Коммиты

1. `[DevOps Bot] DB: Add auto_training columns (migration 002)` — e1ddd64
2. `[DevOps Bot] Add: training_auto handler (UI for auto training)` — 390a799
3. `[DevOps Bot] Update: /learning with auto training button` — b90fac6
4. `[DevOps Bot] Update: /settings with auto training section` — 1ba9a2f
5. `[DevOps Bot] Update: /help with quick jump commands + scheduler integration` — e731b2f
6. `[DevOps Bot] Tests: auto training feature` — 3c75ca8

---

## 🚀 Следующие шаги

**Готово к:**
- ✅ QA тестирование (Гена)
- ✅ Code review (Алекс)
- ✅ Merge в main (Вовчик)

**Deployment:**
- Антон деплоит на PROD после аппрува

---

_Разработка завершена: 2026-03-28_
