"""Categorisation and analysis logic (pure Python, no web or DB code)."""
import calendar
from collections import defaultdict
from datetime import date

CATEGORY_KEYWORDS = {
    "Food": ["restaurant", "cafe", "coffee", "lunch", "dinner", "swiggy", "zomato", "pizza", "snack", "biryani"],
    "Groceries": ["grocery", "supermarket", "vegetable", "fruit", "milk", "bigbasket", "dmart", "blinkit"],
    "Transport": ["uber", "ola", "taxi", "fuel", "petrol", "diesel", "metro", "bus", "train", "parking"],
    "Bills": ["electricity", "water bill", "internet", "wifi", "recharge", "rent", "insurance", "gas"],
    "Shopping": ["amazon", "flipkart", "myntra", "clothes", "shoes", "mall", "electronics"],
    "Health": ["pharmacy", "doctor", "hospital", "medicine", "clinic", "gym"],
    "Entertainment": ["movie", "netflix", "spotify", "game", "concert", "subscription"],
    "Education": ["course", "book", "tuition", "udemy", "exam", "college"],
    "Travel": ["flight", "hotel", "airbnb", "trip", "resort"],
}
CATEGORIES = list(CATEGORY_KEYWORDS) + ["Other"]


def categorize(description: str) -> str:
    """Guess a category from keywords in the description."""
    text = description.lower()
    for category, words in CATEGORY_KEYWORDS.items():
        if any(word in text for word in words):
            return category
    return "Other"


def previous_month(month: str) -> str:
    year, mon = map(int, month.split("-"))
    mon -= 1
    if mon == 0:
        year, mon = year - 1, 12
    return f"{year:04d}-{mon:02d}"


def summarize(expenses, budgets, month, today=None):
    """Build the dashboard summary for one month (YYYY-MM).

    expenses: list of dicts with date, amount, category, description
    budgets:  dict of category -> monthly limit
    """
    today = today or date.today()
    year, mon = map(int, month.split("-"))
    days_in_month = calendar.monthrange(year, mon)[1]

    current = [e for e in expenses if e["date"].startswith(month)]
    previous = [e for e in expenses if e["date"].startswith(previous_month(month))]
    total = round(sum(e["amount"] for e in current), 2)
    prev_total = round(sum(e["amount"] for e in previous), 2)

    by_cat = defaultdict(float)
    daily = [0.0] * days_in_month
    for e in current:
        by_cat[e["category"]] += e["amount"]
        daily[int(e["date"][8:10]) - 1] += e["amount"]
    by_category = [
        {"category": c, "amount": round(a, 2), "share": round(a / total * 100, 1) if total else 0}
        for c, a in sorted(by_cat.items(), key=lambda kv: -kv[1])
    ]

    # Forecast: project the average daily spend over the whole month.
    if (today.year, today.month) == (year, mon):
        elapsed = max(today.day, 1)
    else:
        elapsed = days_in_month
    forecast = round(total / elapsed * days_in_month, 2) if total else 0

    budget_rows = []
    for category, limit in budgets.items():
        spent = round(by_cat.get(category, 0), 2)
        pct = round(spent / limit * 100, 1) if limit else 0
        status = "over" if pct >= 100 else "warning" if pct >= 80 else "ok"
        budget_rows.append({"category": category, "limit": limit, "spent": spent, "pct": pct, "status": status})

    change_pct = round((total - prev_total) / prev_total * 100, 1) if prev_total else None

    insights = []
    if change_pct is not None:
        direction = "more" if change_pct > 0 else "less"
        insights.append(f"You spent {abs(change_pct)}% {direction} than last month.")
    if by_category:
        top = by_category[0]
        insights.append(f"{top['category']} is your biggest category at {top['share']}% of spending.")
    for b in budget_rows:
        if b["status"] == "over":
            insights.append(f"{b['category']} is over budget by {round(b['spent'] - b['limit'], 2)}.")
        elif b["status"] == "warning":
            insights.append(f"{b['category']} has used {b['pct']}% of its budget.")
    total_budget = sum(budgets.values())
    if total_budget and forecast > total_budget:
        insights.append(f"At this pace you will spend {forecast}, above your total budget of {total_budget}.")

    top_expense = max(current, key=lambda e: e["amount"], default=None)
    return {
        "month": month, "total": total, "prev_total": prev_total, "change_pct": change_pct,
        "forecast": forecast, "count": len(current), "by_category": by_category,
        "daily": [round(d, 2) for d in daily], "budgets": budget_rows,
        "insights": insights, "top_expense": top_expense,
    }
