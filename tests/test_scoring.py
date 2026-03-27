"""
Автотесты для scoring и feedback
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from bot.utils.scoring import calculate_feedback, get_performance_summary


def test_calculate_feedback_perfect():
    """Тест feedback для идеального результата"""
    feedback = calculate_feedback(score=5, total_tasks=5, average_time=180)
    
    assert "Идеальный результат" in feedback
    assert len(feedback) > 0


def test_calculate_feedback_good():
    """Тест feedback для хорошего результата"""
    feedback = calculate_feedback(score=4, total_tasks=5, average_time=240)
    
    assert "Отличный" in feedback or "Хороший" in feedback


def test_calculate_feedback_needs_practice():
    """Тест feedback для слабого результата"""
    feedback = calculate_feedback(score=1, total_tasks=5, average_time=420)
    
    assert "практик" in feedback.lower() or "подготовк" in feedback.lower()


def test_calculate_feedback_time_warning():
    """Тест предупреждения о медленном решении"""
    feedback = calculate_feedback(score=5, total_tasks=5, average_time=480)
    
    assert "быстрее" in feedback.lower() or "время" in feedback.lower()


def test_performance_summary():
    """Тест общей статистики"""
    summary = get_performance_summary(solved_tasks=40, total_tasks=50, mock_sessions=3)
    
    assert "40/50" in summary
    assert "80.0%" in summary
    assert "3" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
