# DevOps Interview Bot - Project Context

**Дата создания:** 2026-03-27  
**Статус:** В разработке

---

## 📍 Описание проекта

Telegram-бот для подготовки к собеседованиям DevOps Engineer.

**Два режима:**
1. **Тренировка** — раз в час отправляет задачу с решением
2. **Мок-собес** — симуляция реального собеседования (30 мин, 3-5 задач)

**Цель:** Прокачать скорость решения типичных задач DevOps (Nginx, Bash, K8s, Git, Docker).

---

## 🗂️ Репозиторий

**GitHub:** (будет создан Алексом)  
**Локальный путь (sandbox):** `/root/.openclaw/workspace/projects/devops_interview_bot/`

**Структура:**
```
devops_interview_bot/
├── bot/
│   ├── main.py              # Точка входа
│   ├── handlers/
│   │   ├── training.py      # Режим тренировки
│   │   └── mock_interview.py # Режим мок-собеса
│   ├── db/
│   │   ├── models.py        # SQLAlchemy models
│   │   └── crud.py          # CRUD операции
│   ├── tasks/
│   │   └── tasks.json       # 50 задач с решениями
│   └── utils/
│       ├── cron.py          # Отправка задач раз в час
│       └── scoring.py       # Подсчёт статистики
├── deploy/
│   ├── playbooks/
│   │   └── deploy.yml       # Ansible playbook
│   └── secrets/
│       └── env/
│           └── test.env     # Токен бота (sandbox)
├── docker-compose.yml       # Docker orchestration
├── Dockerfile               # Контейнер бота
├── requirements.txt         # Python dependencies
├── .gitignore
└── README.md
```

---

## 📋 Notion

**Страница проекта:** (будет создана)  
**База задач:** (будет создана)

---

## 🛠️ Технологический стек

- **Python 3.12**
- **aiogram** (Telegram bot framework)
- **SQLite** (база данных)
- **SQLAlchemy** (ORM)
- **Docker** + **docker-compose**
- **Ansible** (деплой)

---

## 🔧 Разработка

### Локальный запуск (sandbox)
```bash
cd /root/.openclaw/workspace/projects/devops_interview_bot
docker compose up -d
```

### Тестовый токен
Использует токен `time_counting_bot` (временно, пока в песочнице).

---

## 📦 Деплой

**Окружение:** Sandbox (localhost)  
**Позже:** Raspi (production)

**Через Ansible:**
```bash
cd /root/.openclaw/workspace
ansible-playbook \
  projects/devops_interview_bot/deploy/playbooks/deploy.yml \
  -i infrastructure/inventory/devops_interview_bot/test.yml
```

---

## ✅ Задачи (Roadmap)

### Фаза 1: MVP (тестовый бот на sandbox)
- [ ] Создать базу данных (SQLite schema)
- [ ] Написать 50 задач с решениями (tasks.json)
- [ ] Реализовать режим тренировки (раз в час → задача)
- [ ] Реализовать режим мок-собеса (диалог 30 мин)
- [ ] Docker контейнер
- [ ] Ansible playbook для деплоя
- [ ] Запуск на sandbox

### Фаза 2: Production (Raspi)
- [ ] Создать отдельного бота (новый токен)
- [ ] Деплой на Raspi
- [ ] Мониторинг и логирование

### Фаза 3: Улучшения
- [ ] Статистика прогресса (dashboard)
- [ ] Кастомные задачи (добавление пользователем)
- [ ] Уровни сложности (Junior/Middle/Senior)

---

## 🔑 Credentials

**Тестовый токен:** (из time_counting_bot .env)  
**Admin Chat ID:** 384973490 (Алекс)

---

## 📝 История изменений

**2026-03-27 18:15:** Проект создан (Вовчик)  
- Создана структура PROJECT.md
- Определена архитектура
- Подготовлена структура Git репо
