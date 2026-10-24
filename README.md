# Smart Expense Tracker and Analyzer

A web app for logging daily spending and understanding where your money goes. Built with Python, Flask, SQLite and Chart.js.

## Features

- Add, view and delete expenses
- **Automatic categorisation** from the description (for example "Swiggy dinner" becomes Food)
- Monthly dashboard with category and day-by-day charts
- **Analysis**: comparison with last month, month-end spending forecast, largest expense
- **Budgets** per category with warnings at 80% and alerts when exceeded
- Plain-language insights
- Export all expenses to CSV

## Run it

```bash
git clone https://github.com/YOUR-USERNAME/smart-expense-tracker-and-analyzer.git
cd smart-expense-tracker-and-analyzer
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 in your browser.

Optional environment variables: `CURRENCY` (default `₹`), `EXPENSE_DB` (database file path).

## Run the tests

```bash
pytest
```

## Project structure

```
app.py              Flask routes and SQLite storage
analyzer.py         Categorisation, forecast, budgets and insights
templates/          Dashboard page (HTML, CSS, JavaScript)
tests/              Unit tests
```

## API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/expenses?month=YYYY-MM` | List expenses |
| POST | `/api/expenses` | Add an expense |
| DELETE | `/api/expenses/<id>` | Delete an expense |
| GET / POST | `/api/budgets` | Read or set category budgets |
| GET | `/api/summary?month=YYYY-MM` | Dashboard analysis |
| GET | `/api/export.csv` | Download all expenses |

## Ideas for next steps

User accounts, recurring expenses, receipt upload, and a machine-learning categoriser.

## License

MIT
