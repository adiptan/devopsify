"""
Подсчёт статистики и генерация feedback для мок-собеса
"""


def calculate_feedback(score: int, total_tasks: int, average_time: int) -> str:
    """
    Генерация рекомендаций на основе результатов мок-собеса
    
    Args:
        score: Количество решённых задач
        total_tasks: Всего задач в сессии
        average_time: Среднее время на задачу (в секундах)
    
    Returns:
        Текст с рекомендациями
    """
    success_rate = (score / total_tasks * 100) if total_tasks > 0 else 0
    avg_min = average_time // 60
    
    feedback_parts = []
    
    # Оценка по проценту решённых задач
    if success_rate == 100:
        feedback_parts.append("🔥 Идеальный результат! Ты справился со всеми задачами.")
    elif success_rate >= 80:
        feedback_parts.append("👍 Отличный результат! Небольшая доработка — и будешь идеален.")
    elif success_rate >= 60:
        feedback_parts.append("💪 Хороший результат, но есть куда расти.")
    elif success_rate >= 40:
        feedback_parts.append("📚 Нужно больше практики. Повтори основы.")
    else:
        feedback_parts.append("⚠️ Стоит уделить больше времени подготовке.")
    
    # Оценка по времени
    if avg_min <= 3:
        feedback_parts.append("⚡️ Ты очень быстр! Но проверь, что решения правильные.")
    elif avg_min <= 5:
        feedback_parts.append("✅ Отличная скорость решения задач.")
    elif avg_min <= 7:
        feedback_parts.append("⏱ Время неплохое, но можно быстрее.")
    else:
        feedback_parts.append("🐢 Старайся решать быстрее — на собесе время ограничено.")
    
    # Общие рекомендации
    if success_rate < 70:
        feedback_parts.append("\n💡 Совет: больше практики с Bash, Git и Kubernetes.")
    
    if avg_min > 6:
        feedback_parts.append("💡 Совет: повтори основные команды — это ускорит решение.")
    
    return "\n".join(feedback_parts)


def get_performance_summary(solved_tasks: int, total_tasks: int, mock_sessions: int) -> str:
    """
    Общая статистика пользователя
    
    Args:
        solved_tasks: Решённых задач в тренировке
        total_tasks: Всего задач
        mock_sessions: Количество пройденных мок-собесов
    
    Returns:
        Краткая сводка
    """
    progress = (solved_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    summary = f"📊 Твой прогресс:\n"
    summary += f"• Решено задач: {solved_tasks}/{total_tasks} ({progress:.1f}%)\n"
    summary += f"• Пройдено мок-собесов: {mock_sessions}\n"
    
    if progress >= 80:
        summary += "\n🔥 Ты почти готов к реальному собесу!"
    elif progress >= 50:
        summary += "\n💪 Хорошая база, продолжай практиковаться!"
    else:
        summary += "\n📚 Впереди много работы — но ты на правильном пути!"
    
    return summary
