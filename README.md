# DevOps Interview Bot

Telegram бот для подготовки к собеседованиям DevOps Engineer.

## Функционал

### Режим тренировки
- Раз в час отправляет задачу по DevOps
- Подсказки и эталонные решения
- Отслеживание прогресса (X/50 задач)
- **Включается/выключается через /settings**

### Режим обучения ✨ NEW (Carousel Feature)
- **Карусель карточек** по 5 темам: Nginx (10 карточек), Bash (15), Kubernetes (10), Git (10), Docker (10)
- **Навигация:** ⬅️ Предыдущая / ➡️ Следующая
- **Быстрый переход:** `/nginx 5`, `/bash 10`, `/k8s 3`, `/git 7`, `/docker 4`
- **Сохранение прогресса:** продолжай с последней карточки
- **Интеграция с задачами:** после теории → практические задачи

### Режим мок-собеса
- Симуляция реального собеседования
- 30 минут на 3-5 задач
- Детальный feedback и рекомендации

### Настройки
- `/settings` — управление режимами
- Включение/выключение тренировки
- Включение/выключение обучения

## Категории задач (50 штук)
- **Nginx** (10 задач)
- **Bash/CLI** (15 задач)
- **Kubernetes** (10 задач)
- **Git** (10 задач)
- **Docker** (5 задач)

## Технологии
- Python 3.12
- aiogram (Telegram Bot API)
- SQLite + SQLAlchemy
- Docker + docker-compose
- Ansible (деплой)

## Установка и запуск

### Локально
```bash
# 1. Создать .env файл из примера
cp .env.example .env
# Отредактируй .env и добавь свой Telegram bot token

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Запустить бота
python -m bot.main
```

### Docker
```bash
# 1. Создать .env файл из примера
cp .env.example .env
# Отредактируй .env и добавь свой Telegram bot token

# 2. Запустить контейнер
docker compose up -d

# 3. Посмотреть логи
docker compose logs -f
```

### Деплой через Ansible
```bash
cd /root/.openclaw/workspace
ansible-playbook \
  projects/devops_interview_bot/deploy/playbooks/deploy.yml \
  -i infrastructure/inventory/devops_interview_bot/test.yml
```

## Команды бота

- `/start` — Начать работу с ботом
- `/help` — Справка
- `/training` — Режим тренировки
- `/task` — Получить задачу сейчас
- `/learning` — Режим обучения (карусель карточек) ✨
- `/nginx [N]` — Перейти к N-й карточке Nginx ✨
- `/bash [N]` — Перейти к N-й карточке Bash ✨
- `/k8s [N]` или `/kubernetes [N]` — Карточка Kubernetes ✨
- `/git [N]` — Перейти к N-й карточке Git ✨
- `/docker [N]` — Перейти к N-й карточке Docker ✨
- `/mock_interview` — Запустить мок-собес
- `/next_task` — Следующая задача в собесе
- `/settings` — Настройки режимов ⚙️

## Структура проекта
```
devops_interview_bot/
├── bot/
│   ├── main.py              # Точка входа
│   ├── handlers/
│   │   ├── training.py      # Режим тренировки
│   │   ├── learning.py      # Режим обучения ✨
│   │   ├── settings.py      # Настройки ⚙️
│   │   └── mock_interview.py # Режим мок-собеса
│   ├── db/
│   │   ├── models.py        # SQLAlchemy models
│   │   └── crud.py          # CRUD операции
│   ├── content/
│   │   ├── lectures.json    # Старые лекции (deprecated)
│   │   └── learning_cards.json  # 60 карточек для карусели ✨
│   ├── tasks/
│   │   └── tasks.json       # 50 задач с решениями
│   └── utils/
│       ├── cron.py          # Планировщик задач
│       └── scoring.py       # Подсчёт статистики
├── tests/
│   ├── test_db.py           # Тесты БД
│   ├── test_learning.py     # Тесты обучения (старые)
│   ├── test_carousel.py     # Тесты карусели карточек ✨
│   ├── test_settings.py     # Тесты настроек
│   └── test_scoring.py      # Тесты scoring
├── deploy/
│   └── playbooks/
│       └── deploy.yml       # Ansible playbook
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Разработка

Разработчик: Nikita (Senior Python Developer)  
Проект: Koti V Production  
Дата: 2026-03-27
