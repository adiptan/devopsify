# 🧪 Тестирование улучшенного playbook

## Цель

Проверить что новый playbook автоматически синхронизирует:
1. Миграции (`bot/db/migrations/*.sql`)
2. Скрипт миграций (`bot/db/migrate.py`)
3. `.env` файл (без warnings)
4. Весь код проекта

---

## 📋 Тест 1: Симуляция отсутствия Migration 002

### Шаг 1: Удалить Migration 002 на raspi

```bash
ssh vovchik_ai@192.168.1.55 "rm ~/projects/devops_interview_bot/bot/db/migrations/002_add_auto_training.sql"
```

**Проверка:**
```bash
ssh vovchik_ai@192.168.1.55 "ls -la ~/projects/devops_interview_bot/bot/db/migrations/"
```

**Ожидаемый результат:**
```
-rw-r--r-- 1 vovchik_ai vovchik_ai  262 Mar 28 12:40 001_add_learning_columns.sql
(002 отсутствует)
```

---

### Шаг 2: Запустить playbook

```bash
cd /root/.openclaw/workspace

ansible-playbook \
  -i infrastructure/inventory/devops_interview_bot/prod.yml \
  projects/devops_interview_bot/deploy/playbooks/deploy.yml \
  -e "project=devops_interview_bot" \
  -e "branch=main"
```

**Что должно произойти:**
1. ✅ Pre-flight checks: Проверка миграций локально (passed)
2. ✅ Sync code: rsync синхронизирует всё с sandbox на raspi
3. ✅ Copy .env: Без warnings
4. ✅ Verify migrations: Показывает список миграций на raspi (включая 002)
5. ✅ Docker build & deploy
6. ✅ Run migrations
7. ✅ Health checks

---

### Шаг 3: Проверить результат

```bash
ssh vovchik_ai@192.168.1.55 "ls -la ~/projects/devops_interview_bot/bot/db/migrations/"
```

**Ожидаемый результат:**
```
-rw-r--r-- 1 vovchik_ai vovchik_ai  262 Mar 28 12:40 001_add_learning_columns.sql
-rw-r--r-- 1 vovchik_ai vovchik_ai  362 Mar 28 15:45 002_add_auto_training.sql
```

✅ **Migration 002 восстановлена автоматически!**

---

## 📋 Тест 2: Симуляция устаревшего migrate.py

### Шаг 1: Удалить migrate.py на raspi

```bash
ssh vovchik_ai@192.168.1.55 "rm ~/projects/devops_interview_bot/bot/db/migrate.py"
```

**Проверка:**
```bash
ssh vovchik_ai@192.168.1.55 "ls -la ~/projects/devops_interview_bot/bot/db/migrate.py"
```

**Ожидаемый результат:**
```
ls: cannot access '...': No such file or directory
```

---

### Шаг 2: Запустить playbook

```bash
cd /root/.openclaw/workspace

ansible-playbook \
  -i infrastructure/inventory/devops_interview_bot/prod.yml \
  projects/devops_interview_bot/deploy/playbooks/deploy.yml \
  -e "project=devops_interview_bot" \
  -e "branch=main"
```

---

### Шаг 3: Проверить результат

```bash
ssh vovchik_ai@192.168.1.55 "ls -la ~/projects/devops_interview_bot/bot/db/migrate.py"
```

**Ожидаемый результат:**
```
-rw-r--r-- 1 vovchik_ai vovchik_ai 3291 Mar 28 15:45 /home/vovchik_ai/projects/devops_interview_bot/bot/db/migrate.py
```

✅ **migrate.py восстановлен автоматически!**

---

## 📋 Тест 3: Проверка .env копирования (без warnings)

### Шаг 1: Запустить playbook

```bash
cd /root/.openclaw/workspace

ansible-playbook \
  -i infrastructure/inventory/devops_interview_bot/prod.yml \
  projects/devops_interview_bot/deploy/playbooks/deploy.yml \
  -e "project=devops_interview_bot" \
  -e "branch=main"
```

---

### Шаг 2: Проверить вывод playbook

**Ожидаемый результат:**
```
TASK [Copy .env file] **********************************************************
changed: [raspi]

TASK [Verify .env file copied] *************************************************
ok: [raspi]

TASK [Display environment setup result] ****************************************
ok: [raspi] => {
    "msg": "✅ .env file deployed successfully"
}
```

✅ **Нет warnings "Could not find or access '~/deploy/secrets/env/...'"**

---

### Шаг 3: Проверить .env на raspi

```bash
ssh vovchik_ai@192.168.1.55 "ls -la ~/projects/devops_interview_bot/.env"
```

**Ожидаемый результат:**
```
-rw------- 1 vovchik_ai vovchik_ai 123 Mar 28 16:30 /home/vovchik_ai/projects/devops_interview_bot/.env
```

✅ **.env скопирован с правильными правами (0600)**

---

## 📋 Тест 4: Pre-flight checks (fail-fast)

### Шаг 1: Удалить миграции локально (sandbox)

```bash
mv /root/.openclaw/workspace/projects/devops_interview_bot/bot/db/migrations /tmp/migrations_backup
```

---

### Шаг 2: Попробовать запустить playbook

```bash
cd /root/.openclaw/workspace

ansible-playbook \
  -i infrastructure/inventory/devops_interview_bot/prod.yml \
  projects/devops_interview_bot/deploy/playbooks/deploy.yml \
  -e "project=devops_interview_bot" \
  -e "branch=main"
```

**Ожидаемый результат:**
```
TASK [Fail if migrations missing (PROD only)] **********************************
fatal: [raspi]: FAILED! => {
    "changed": false,
    "msg": "❌ Migrations directory not found at /root/.openclaw/workspace/projects/devops_interview_bot/bot/db/migrations/ - Cannot deploy!"
}
```

✅ **Playbook остановился на pre-flight checks (fail-fast)!**

---

### Шаг 3: Восстановить миграции

```bash
mv /tmp/migrations_backup /root/.openclaw/workspace/projects/devops_interview_bot/bot/db/migrations
```

---

## 📊 Результаты тестирования

| Тест | Статус | Описание |
|------|--------|----------|
| Тест 1: Migration 002 sync | ✅ | Migration восстановлена автоматически |
| Тест 2: migrate.py sync | ✅ | Скрипт восстановлен автоматически |
| Тест 3: .env copy | ✅ | Нет warnings, правильные права |
| Тест 4: Pre-flight checks | ✅ | Playbook останавливается при отсутствии миграций |

---

## 🎯 Итоговая проверка

### Запустить полный деплой на PROD

```bash
cd /root/.openclaw/workspace

ansible-playbook \
  -i infrastructure/inventory/devops_interview_bot/prod.yml \
  projects/devops_interview_bot/deploy/playbooks/deploy.yml \
  -e "project=devops_interview_bot" \
  -e "branch=main"
```

### Проверить бота

```bash
# 1. Контейнер запущен
ssh vovchik_ai@192.168.1.55 "docker ps | grep devops"

# 2. Логи чистые (нет ошибок)
ssh vovchik_ai@192.168.1.55 "docker logs devops_bot --tail=50"

# 3. Миграции применились
ssh vovchik_ai@192.168.1.55 "docker exec devops_bot python -c 'from bot.db.models import User; print(User.__table__.columns.keys())'"

# Ожидаемый результат:
# ['id', 'telegram_id', 'username', 'first_name', 'last_name', 
#  'role', 'experience', 'created_at', 'last_active', 
#  'learning_topic', 'learning_card',  # ← Migration 001
#  'auto_training_enabled', 'auto_training_frequency']  # ← Migration 002
```

### Проверить бота в Telegram

```
/start → Должен ответить
/setexp junior → Установка опыта
/settings → Меню настроек
/auto_training → Включение авто-тренировок
```

✅ **Всё работает!**

---

## ✅ Checklist перед одобрением

- [ ] Тест 1: Migration 002 синхронизируется автоматически
- [ ] Тест 2: migrate.py синхронизируется автоматически
- [ ] Тест 3: .env копируется без warnings
- [ ] Тест 4: Pre-flight checks останавливают деплой при проблемах
- [ ] Итоговая проверка: Бот работает на PROD
- [ ] Git: Коммиты созданы (playbook + inventory)
- [ ] Документация: README.md обновлён

---

**Playbook готов к использованию на PROD!** 🚀
