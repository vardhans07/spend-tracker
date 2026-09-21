# Mini Spend Tracker

A lightweight, robust expense tracking REST API built with Python, FastAPI, SQLite, and a vanilla HTML/JS frontend.

## Features
- **RESTful Endpoints**:
  - `POST /expenses`: Create expense entry with amount, category, date, and note.
  - `GET /expenses`: Filterable by category and date range.
  - `GET /summary`: Aggregates total spend, category-wise breakdown, and month-over-month change percentage.
- **Validation**: Strict schema checks using Pydantic (positive amounts, non-empty categories, proper ISO date formatting).
- **Relational Storage**: SQLite with SQLAlchemy ORM using indexed columns.
- **Frontend**: Clean single-page interface served directly by FastAPI.
- **Automated Tests**: Pytest test suite covering endpoint functionality and input validation failure modes.

## Local Setup

1. **Clone the repository:**
   ```bash
   git clone <REPO_URL>
   cd spend-tracker


 **Run tests:**
   ```bash
   pytest
```

<img width="1009" height="438" alt="image" src="https://github.com/user-attachments/assets/651406cf-e9e9-4ac9-bd43-bf3a9740dad1" />
