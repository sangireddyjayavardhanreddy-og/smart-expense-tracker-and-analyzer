"""Smart Expense Tracker and Analyzer - Flask + SQLite backend."""
import csv
import io
import os
import sqlite3
from datetime import date

from flask import Flask, Response, g, jsonify, render_template, request

from analyzer import CATEGORIES, categorize, summarize

app = Flask(__name__)
DB_PATH = os.environ.get("EXPENSE_DB", "expenses.db")
CURRENCY = os.environ.get("CURRENCY", "₹")


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db:
        db.close()


def init_db():
    with sqlite3.connect(DB_PATH) as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS budgets (
                category TEXT PRIMARY KEY,
                monthly_limit REAL NOT NULL
            );
            """
        )


def error(message, status=400):
    return jsonify({"error": message}), status


def valid_month(value):
    try:
        date.fromisoformat(value + "-01")
        return True
    except (TypeError, ValueError):
        return False


@app.get("/")
def index():
    return render_template("index.html", currency=CURRENCY, categories=CATEGORIES)


@app.get("/api/expenses")
def list_expenses():
    month = request.args.get("month")
    query, params = "SELECT * FROM expenses", []
    if month:
        if not valid_month(month):
            return error("month must look like 2026-10")
        query += " WHERE date LIKE ?"
        params.append(month + "%")
    rows = get_db().execute(query + " ORDER BY date DESC, id DESC", params).fetchall()
    return jsonify([dict(r) for r in rows])


@app.post("/api/expenses")
def add_expense():
    data = request.get_json(silent=True) or {}
    description = str(data.get("description", "")).strip()
    try:
        amount = round(float(data.get("amount")), 2)
        day = date.fromisoformat(str(data.get("date") or date.today()))
    except (TypeError, ValueError):
        return error("Enter a valid amount and date.")
    if not description:
        return error("Add a short description.")
    if amount <= 0:
        return error("Amount must be greater than zero.")
    category = data.get("category") or categorize(description)
    if category not in CATEGORIES:
        return error("Unknown category.")
    db = get_db()
    cur = db.execute(
        "INSERT INTO expenses (date, amount, category, description) VALUES (?, ?, ?, ?)",
        (day.isoformat(), amount, category, description),
    )
    db.commit()
    return jsonify({"id": cur.lastrowid, "category": category}), 201


@app.delete("/api/expenses/<int:expense_id>")
def delete_expense(expense_id):
    db = get_db()
    db.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    db.commit()
    return "", 204


@app.get("/api/budgets")
def get_budgets():
    rows = get_db().execute("SELECT category, monthly_limit FROM budgets").fetchall()
    return jsonify({r["category"]: r["monthly_limit"] for r in rows})


@app.post("/api/budgets")
def set_budget():
    data = request.get_json(silent=True) or {}
    category = data.get("category")
    try:
        limit = float(data.get("limit"))
    except (TypeError, ValueError):
        return error("Enter a valid budget amount.")
    if category not in CATEGORIES or limit < 0:
        return error("Pick a category and a budget of zero or more.")
    db = get_db()
    if limit == 0:
        db.execute("DELETE FROM budgets WHERE category = ?", (category,))
    else:
        db.execute("REPLACE INTO budgets (category, monthly_limit) VALUES (?, ?)", (category, limit))
    db.commit()
    return jsonify({"ok": True})


@app.get("/api/summary")
def summary():
    month = request.args.get("month") or date.today().strftime("%Y-%m")
    if not valid_month(month):
        return error("month must look like 2026-10")
    db = get_db()
    expenses = [dict(r) for r in db.execute("SELECT * FROM expenses")]
    budgets = {r["category"]: r["monthly_limit"] for r in db.execute("SELECT * FROM budgets")}
    return jsonify(summarize(expenses, budgets, month))


@app.get("/api/export.csv")
def export_csv():
    rows = get_db().execute("SELECT date, category, description, amount FROM expenses ORDER BY date").fetchall()
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["date", "category", "description", "amount"])
    writer.writerows([tuple(r) for r in rows])
    return Response(out.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=expenses.csv"})


init_db()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
