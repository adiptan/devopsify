# DevOps Interview Bot - Deployment Guide

## 📦 Улучшенный Ansible Playbook

**Что нового:**
- ✅ Автоматическая синхронизация кода (rsync)
- ✅ Автоматическая синхронизация миграций (`bot/db/migrations/*.sql`)
- ✅ Автоматическая синхронизация `migrate.py`
- ✅ Исправлено копирование `.env` (без warnings)
- ✅ Pre-flight checks перед деплоем
- ✅ Верификация миграций на target хосте
- ✅ Подробное логирование каждого шага

---

## 🚀 Как деплоить

### 1. Деплой на TEST (sandbox)

```bash
cd /root/.openclaw/workspace

ansible-playbook \
  -i infrastructure/inventory/devops_interview_bot/test.yml \
  projects/devops_interview_bot/deploy/playbooks/deploy.yml \
  -e "project=devops_interview_bot" \
  -e "branch=main"
```

**Что происходит:**
- Запускается локально (ansible_connection: local)
- Использует `.env` из `/root/.openclaw/workspace/deploy/secrets/env/devops_interview_bot_test.env`
- НЕ синхронизирует код (уже на месте)
- Build → Start → Migrate → Health checks

---

### 2. Деплой на PROD (raspi)

```bash
cd /root/.openclaw/workspace

ansible-playbook \
  -i infrastructure/inventory/devops_interview_bot/prod.yml \
  projects/devops_interview_bot/deploy/playbooks/deploy.yml \
  -e "project=devops_interview_bot" \
  -e "branch=main"
```

**Что происходит:**
1. **Pre-flight checks:**
   - Проверяет наличие миграций локально
   - Проверяет наличие `migrate.py` локально
   - Проверяет наличие `.env` файла

2. **Синхронизация кода (rsync):**
   - Копирует весь проект с sandbox на raspi
   - Включая миграции (`bot/db/migrations/*.sql`)
   - Включая `migrate.py`
   - Исключает `.git/`, `data/`, `.env`, `__pycache__/`, `venv/`

3. **Setup environment:**
   - Копирует `.env` из `/root/.openclaw/workspace/deploy/secrets/env/devops_interview_bot_prod.env`
   - Создаёт backup старого `.env` (если был)

4. **Verify migrations:**
   - Показывает список миграций на target хосте
   - Проверяет наличие `migrate.py`

5. **Docker build & deploy:**
   - `docker compose down`
   - `docker compose build`
   - `docker compose up -d`

6. **Run migrations:**
   - `docker compose exec -T devops_bot python -m bot.db.migrate`
   - 3 попытки с задержкой 2 сек

7. **Health checks:**
   - Рестарт контейнеров
   - Проверка статуса
   - Показ логов (последние 20 строк)

---

## 📁 Структура inventory

```
infrastructure/inventory/devops_interview_bot/
├── prod.yml    # Production (raspi)
└── test.yml    # Test (sandbox)
```

### prod.yml

```yaml
all:
  children:
    prod:
      hosts:
        raspi:
          ansible_host: 192.168.1.55
          ansible_user: vovchik_ai
          ansible_ssh_private_key_file: /root/.ssh/id_ed25519
      
      vars:
        env_name: prod
        project_config:
          name: devops_interview_bot
          path: ~/projects/devops_interview_bot
          repo: https://github.com/kotivproduction/devops_interview_bot.git
          branch: main
          env_file: /root/.openclaw/workspace/deploy/secrets/env/devops_interview_bot_prod.env
        
        sync_config:
          source: /root/.openclaw/workspace/projects/devops_interview_bot/
          exclude:
            - '.git/'
            - 'data/'
            - '.env'
            - '__pycache__/'
            - '*.pyc'
            - 'venv/'
```

---

## 🧪 Тестирование синхронизации

### Симуляция проблемы (удалить Migration 002)

```bash
ssh vovchik_ai@192.168.1.55 "rm ~/projects/devops_interview_bot/bot/db/migrations/002_add_auto_training.sql"
```

### Запустить playbook

```bash
cd /root/.openclaw/workspace

ansible-playbook \
  -i infrastructure/inventory/devops_interview_bot/prod.yml \
  projects/devops_interview_bot/deploy/playbooks/deploy.yml \
  -e "project=devops_interview_bot" \
  -e "branch=main"
```

### Проверить результат

```bash
ssh vovchik_ai@192.168.1.55 "ls -la ~/projects/devops_interview_bot/bot/db/migrations/"
```

**Ожидаемый результат:**
```
-rw-r--r-- 1 vovchik_ai vovchik_ai  262 Mar 28 12:40 001_add_learning_columns.sql
-rw-r--r-- 1 vovchik_ai vovchik_ai  362 Mar 28 15:45 002_add_auto_training.sql
```

✅ Migration 002 восстановлена автоматически!

---

## 🔍 Диагностика

### Проверить статус контейнеров

```bash
ssh vovchik_ai@192.168.1.55 "docker ps | grep devops"
```

### Проверить логи

```bash
ssh vovchik_ai@192.168.1.55 "docker logs -f devops_bot"
```

### Проверить миграции

```bash
ssh vovchik_ai@192.168.1.55 "ls -la ~/projects/devops_interview_bot/bot/db/migrations/"
```

### Проверить .env

```bash
ssh vovchik_ai@192.168.1.55 "ls -la ~/projects/devops_interview_bot/.env"
```

---

## ⚠️ Troubleshooting

### Problem: rsync fails with "permission denied"

**Причина:** SSH ключ не найден или неправильные права.

**Решение:**
```bash
chmod 600 /root/.ssh/id_ed25519
ssh-add /root/.ssh/id_ed25519
```

### Problem: "Could not find or access .env file"

**Причина:** `.env` файл не существует на control node (sandbox).

**Решение:**
```bash
ls -la /root/.openclaw/workspace/deploy/secrets/env/devops_interview_bot_prod.env
```

Если файла нет — создай его:
```bash
echo "BOT_TOKEN=your_token_here" > /root/.openclaw/workspace/deploy/secrets/env/devops_interview_bot_prod.env
chmod 600 /root/.openclaw/workspace/deploy/secrets/env/devops_interview_bot_prod.env
```

### Problem: Migrations missing after sync

**Причина:** `sync_config.source` указывает на неправильную директорию.

**Решение:**
Проверь что source существует:
```bash
ls -la /root/.openclaw/workspace/projects/devops_interview_bot/bot/db/migrations/
```

Если миграций нет — playbook остановится на pre-flight checks.

---

## 📝 Changelog

### v2.0 (2026-03-28)

**Добавлено:**
- ✅ Полная синхронизация кода через rsync
- ✅ Автоматическая синхронизация миграций
- ✅ Автоматическая синхронизация `migrate.py`
- ✅ Pre-flight checks (проверка миграций, .env)
- ✅ Верификация миграций на target хосте
- ✅ Подробное логирование каждого шага
- ✅ Deployment summary в конце

**Исправлено:**
- ✅ Warning при копировании `.env` (использовался `~` вместо абсолютного пути)
- ✅ Миграции теперь синхронизируются автоматически (не нужно копировать вручную)
- ✅ `migrate.py` синхронизируется автоматически (не нужно обновлять вручную)

**Удалено:**
- ❌ Git pull на target хосте (теперь используется rsync)
- ❌ Хардкод токена в playbook (теперь через `.env` файл)

---

## 🎯 Next Steps

1. Протестировать playbook на TEST
2. Протестировать playbook на PROD (симуляция удаления миграций)
3. Закоммитить изменения в git
4. Обновить документацию (если нужно)

---

**Playbook готов к использованию!** 🚀
