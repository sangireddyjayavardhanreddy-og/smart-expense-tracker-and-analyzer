import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from analyzer import categorize, previous_month, summarize


def test_categorize():
    assert categorize("Swiggy dinner") == "Food"
    assert categorize("Uber to office") == "Transport"
    assert categorize("something random") == "Other"


def test_previous_month_wraps_year():
    assert previous_month("2026-01") == "2025-12"


def test_summarize_budget_and_forecast():
    expenses = [
        {"date": "2026-10-02", "amount": 500.0, "category": "Food", "description": "lunch"},
        {"date": "2026-10-05", "amount": 500.0, "category": "Transport", "description": "fuel"},
        {"date": "2026-09-10", "amount": 1000.0, "category": "Food", "description": "dinner"},
    ]
    s = summarize(expenses, {"Food": 400}, "2026-10", today=date(2026, 10, 10))
    assert s["total"] == 1000.0
    assert s["change_pct"] == 0.0
    assert s["forecast"] == 3100.0  # 1000 / 10 days * 31 days
    assert s["budgets"][0]["status"] == "over"
