from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from dateutil.relativedelta import relativedelta
import calendar

from app.database import engine, Base, get_db
from app.models import Expense
from app.schemas import ExpenseCreate, ExpenseResponse, SummaryResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Spend Tracker API")

@app.post("/expenses", response_model=ExpenseResponse, status_code=201)
def create_expense(expense_in: ExpenseCreate, db: Session = Depends(get_db)):
    expense = Expense(**expense_in.model_dump())
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense

@app.get("/expenses", response_model=list[ExpenseResponse])
def list_expenses(
    category: str | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    db: Session = Depends(get_db),
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must precede end_date")
    
    query = db.query(Expense)
    if category:
        query = query.filter(Expense.category.ilike(category.strip()))
    if start_date:
        query = query.filter(Expense.date >= start_date)
    if end_date:
        query = query.filter(Expense.date <= end_date)
        
    return query.order_by(Expense.date.desc()).all()

@app.get("/summary", response_model=SummaryResponse)
def get_summary(db: Session = Depends(get_db)):
    total = db.query(func.coalesce(func.sum(Expense.amount), 0.0)).scalar()

    cat_rows = (
        db.query(Expense.category, func.sum(Expense.amount))
        .group_by(Expense.category)
        .all()
    )
    by_category = {cat: round(float(amt), 2) for cat, amt in cat_rows}

    today = date.today()
    curr_start = today.replace(day=1)
    _, last_day = calendar.monthrange(today.year, today.month)
    curr_end = today.replace(day=last_day)

    prev_month_anchor = curr_start - relativedelta(days=1)
    prev_start = prev_month_anchor.replace(day=1)
    _, prev_last_day = calendar.monthrange(prev_month_anchor.year, prev_month_anchor.month)
    prev_end = prev_month_anchor.replace(day=prev_last_day)

    curr_total = db.query(func.coalesce(func.sum(Expense.amount), 0.0)).filter(
        Expense.date >= curr_start, Expense.date <= curr_end
    ).scalar()

    prev_total = db.query(func.coalesce(func.sum(Expense.amount), 0.0)).filter(
        Expense.date >= prev_start, Expense.date <= prev_end
    ).scalar()

    curr_val = round(float(curr_total), 2)
    prev_val = round(float(prev_total), 2)

    mom_pct = None
    if prev_val > 0:
        mom_pct = round(((curr_val - prev_val) / prev_val) * 100, 2)

    return SummaryResponse(
        total_spend=round(float(total), 2),
        by_category=by_category,
        current_month_spend=curr_val,
        previous_month_spend=prev_val,
        month_over_month_change_pct=mom_pct,
    )

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_ui():
    return FileResponse("static/index.html")
