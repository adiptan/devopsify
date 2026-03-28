# AI/ML вопросы для DevOps Interview Bot

**Дата:** 2026-03-28  
**Автор:** Вовчик + Алекс  
**Цель:** Добавить категорию AI/ML для подготовки к собесам DevOps с AI-опытом

---

## 📋 Контекст

**Источник:** Резюме Алекса (AI-Enhanced Version)

**AI опыт в резюме:**
- Claude Code (Anthropic) — анализ инфраструктурных проблем, code review, debugging
- OpenClaw AI Agents — кастомные агенты для автоматизации задач
- GitHub Copilot / Cursor — AI-assisted coding
- Root Cause Analysis — AI-анализ production-инцидентов
- Bug Detection — обнаружение багов через AI
- Custom AI Agents — разработка агентов для Confluence/Jira integration
- Prompt Engineering — работа с промптами
- AI-Powered Efficiency — сокращение времени на анализ на 40-50%

---

## 🎯 Категории вопросов

### 1. AI Tools & Platforms (Junior → Senior)

**Junior (базовые знания инструментов):**
1. Что такое Claude Code и для чего используется?
2. Назови 3 популярных AI-инструмента для DevOps
3. Что такое GitHub Copilot?
4. Какие задачи можно автоматизировать с помощью AI в DevOps?
5. Что такое prompt engineering?

**Middle (опыт использования):**
6. Как использовать Claude для анализа логов Nginx?
7. Как интегрировать AI в CI/CD pipeline?
8. Какие метрики используются для оценки качества AI-ассистирован
ного кода?
9. Как Claude может помочь с root cause analysis инцидента?
10. Напиши промпт для анализа 500-й ошибки в production

**Senior (глубокая экспертиза):**
11. Как построить AI-агента для мониторинга инфраструктуры?
12. Какие риски использования AI в production?
13. Как обеспечить security при интеграции AI API?
14. Сравни разные LLM для DevOps задач (Claude, GPT, Gemini)
15. Как измерить ROI от внедрения AI-инструментов?

---

### 2. Prompt Engineering (Junior → Senior)

**Junior:**
16. Что такое промпт?
17. Чем отличается хороший промпт от плохого?
18. Назови 3 правила написания промптов
19. Что такое "system prompt"?
20. Приведи пример промпта для анализа Bash-скрипта

**Middle:**
21. Как структурировать промпт для code review?
22. Что такое few-shot prompting?
23. Как использовать chain-of-thought в промптах?
24. Напиши промпт для анализа Kubernetes pod crash
25. Как оптимизировать промпт для сокращения токенов?

**Senior:**
26. Как реализовать multi-agent prompt orchestration?
27. Что такое prompt injection и как защититься?
28. Как версионировать и тестировать промпты?
29. Разработай систему промптов для AI DevOps ассистента
30. Как измерить эффективность промпта?

---

### 3. AI Agents & Automation (Junior → Senior)

**Junior:**
31. Что такое AI-агент?
32. Чем AI-агент отличается от обычного скрипта?
33. Назови примеры задач для AI-агентов в DevOps
34. Что такое OpenClaw?
35. Какие компоненты нужны для AI-агента?

**Middle:**
36. Как создать AI-агента для автоматизации Jira задач?
37. Как агент может интегрироваться с Confluence?
38. Напиши архитектуру AI-агента для мониторинга
39. Как обрабатывать ошибки в AI-агентах?
40. Как логировать действия AI-агентов?

**Senior:**
41. Разработай multi-agent систему для DevOps
42. Как обеспечить idempotency в AI-агентах?
43. Как масштабировать AI-агентов на 1000+ серверов?
44. Сравни подходы: single agent vs multi-agent
45. Как тестировать AI-агентов в CI/CD?

---

### 4. AI-Driven Incident Management (Junior → Senior)

**Junior:**
46. Как AI помогает в анализе логов?
47. Что такое root cause analysis?
48. Назови преимущества AI для incident management
49. Как Claude анализирует 500-е ошибки?
50. Что такое anomaly detection?

**Middle:**
51. Как автоматизировать анализ Kubernetes events через AI?
52. Напиши промпт для анализа Docker container crash
53. Как AI может предсказать инциденты?
54. Как интегрировать AI в alerting систему?
55. Как приоритизировать инциденты с помощью AI?

**Senior:**
56. Разработай AI-систему для predictive incident management
57. Как обучить модель на исторических инцидентах?
58. Сравни supervised vs unsupervised learning для RCA
59. Как минимизировать false positives в AI alerting?
60. Как измерить MTTR с/без AI?

---

### 5. AI & Security (Junior → Senior)

**Junior:**
61. Какие риски у AI в production?
62. Что такое prompt injection?
63. Как защитить API ключи AI-сервисов?
64. Что такое PII (Personally Identifiable Information)?
65. Можно ли отправлять production логи в AI?

**Middle:**
66. Как анонимизировать логи перед отправкой в AI?
67. Как построить on-premise AI решение?
68. Что такое model hallucination и как с этим работать?
69. Как аудировать использование AI в команде?
70. Напиши политику использования AI в DevOps

**Senior:**
71. Разработай архитектуру для secure AI integration
72. Как обеспечить compliance при использовании AI?
73. Сравни public vs private LLM для enterprise
74. Как защититься от data exfiltration через AI?
75. Как реализовать zero-trust для AI agents?

---

### 6. AI for Infrastructure as Code (Junior → Senior)

**Junior:**
76. Как AI помогает писать Ansible playbooks?
77. Может ли AI генерировать Terraform код?
78. Что такое AI-assisted code review?
79. Как Claude анализирует Dockerfile?
80. Назови 3 AI-инструмента для IaC

**Middle:**
81. Как оптимизировать Kubernetes manifest через AI?
82. Напиши промпт для review Terraform модуля
83. Как AI может выявить security issues в IaC?
84. Как автоматизировать миграцию legacy в IaC?
85. Как тестировать AI-генерированный IaC код?

**Senior:**
86. Разработай AI-систему для auto-remediation в K8s
87. Как интегрировать AI в GitOps workflow?
88. Сравни AI-generated vs human-written IaC
89. Как обеспечить consistency в AI-генерированном коде?
90. Как построить feedback loop для улучшения AI IaC?

---

### 7. AI Metrics & ROI (Middle → Senior)

**Middle:**
91. Какие метрики использовать для AI-эффективности?
92. Как измерить сокращение MTTR с AI?
93. Что такое token cost и как оптимизировать?
94. Как посчитать ROI от Claude Pro подписки?
95. Как измерить quality of AI suggestions?

**Senior:**
96. Разработай dashboard для AI metrics в Grafana
97. Как сравнить стоимость AI vs human для задачи?
98. Напиши cost-benefit анализ AI adoption
99. Как измерить developer productivity с AI?
100. Как построить A/B тест для AI tools?

---

## 📚 Дополнительные темы (для расширения)

### AI & Monitoring
- AI-powered anomaly detection
- Predictive alerting
- Log analysis automation
- Time-series forecasting

### AI & CI/CD
- AI code review в pipeline
- Auto-fix для flaky tests
- Intelligent test selection
- Deployment risk prediction

### AI & Cloud
- AI для cost optimization
- Auto-scaling с ML
- Capacity planning с AI
- Multi-cloud orchestration

### AI & Kubernetes
- AI-powered autoscaling
- Workload optimization
- Resource allocation
- Fault prediction

---

## 🎓 Рекомендации по обучению

**Для Junior:**
- Попробовать Claude Code / GitHub Copilot
- Изучить основы prompt engineering
- Прочитать best practices AI for DevOps

**Для Middle:**
- Создать первого AI-агента
- Интегрировать AI в свой workflow
- Измерить эффективность (до/после AI)

**Для Senior:**
- Построить multi-agent систему
- Разработать AI strategy для команды
- Публиковать кейсы и metrics

---

## 📊 Структура задач для бота

**Формат:**
```json
{
  "id": 51,
  "category": "ai_ml",
  "difficulty": "junior",
  "question": "Что такое Claude Code и для чего используется?",
  "solution": "Claude Code — AI-инструмент от Anthropic для code review, debugging, анализа инфраструктуры. Основные возможности: анализ логов, RCA, code review, генерация кода.",
  "explanation": "Claude Code — это интерфейс для взаимодействия с Claude AI специально для разработки и DevOps задач. Ключевые преимущества: понимание контекста, работа с большими кодовыми базами, интеграция в workflow.",
  "time_limit": 120,
  "hints": [
    "Это продукт от Anthropic",
    "Используется для анализа кода",
    "Помогает в debugging и RCA"
  ]
}
```

**Категории:**
- `ai_ml` — новая категория
- Сложность: junior (30), middle (40), senior (30)
- Всего: 100 задач

---

## 🚀 Next Steps

1. **Nikita:** Создать 100 задач по AI/ML
2. **Gena:** Протестировать задачи
3. **Deploy:** Обновить бота с новой категорией
4. **Update /help:** Добавить "AI/ML (100 задач)"

---

**Время разработки:** ~4-6 часов (100 задач)

**Оценка:** Отдельная ветка `feature/ai-ml-questions`
