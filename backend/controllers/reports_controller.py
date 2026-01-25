from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
from backend.database.db_manager import execute_query, fetch_all, execute_insert, fetch_one

router = APIRouter()

# --- Models ---

class ExpenseBase(BaseModel):
    date: str
    category: str  # 'staff', 'supplies', 'rent', 'marketing', 'other'
    description: Optional[str] = ""
    amount: float
    reservation_id: Optional[int] = None

class Expense(ExpenseBase):
    id: int
    created_at: Optional[str] = None

class RevenueSummary(BaseModel):
    total_revenue: float
    event_count: int
    start_date: str
    end_date: str

class ProfitLossSummary(BaseModel):
    total_revenue: float
    total_expenses: float
    net_profit: float
    start_date: str
    end_date: str

class MonthlySummaryItem(BaseModel):
    month: str
    revenue: float
    expenses: float
    profit: float

# --- Expense CRUD ---

@router.get("/expenses", response_model=List[Expense])
def get_expenses(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    category: Optional[str] = Query(None)
):
    query = "SELECT id, date, category, description, amount, reservation_id, created_at FROM expenses WHERE 1=1"
    params = []
    
    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)
    if category:
        query += " AND category = ?"
        params.append(category)
    
    query += " ORDER BY date DESC"
    rows = fetch_all(query, tuple(params))
    
    return [
        {"id": r[0], "date": r[1], "category": r[2], "description": r[3], "amount": r[4], "reservation_id": r[5], "created_at": r[6]}
        for r in rows
    ]

@router.post("/expenses", response_model=Expense)
def add_expense(expense: ExpenseBase):
    try:
        query = "INSERT INTO expenses (date, category, description, amount, reservation_id) VALUES (?, ?, ?, ?, ?)"
        last_id = execute_insert(query, (expense.date, expense.category, expense.description, expense.amount, expense.reservation_id))
        return {**expense.dict(), "id": last_id, "created_at": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    execute_query("DELETE FROM expenses WHERE id = ?", (expense_id,))
    return {"message": "Gider silindi"}

# --- Revenue Calculation ---

@router.get("/revenue", response_model=RevenueSummary)
def get_revenue_summary(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    query = """
        SELECT 
            COALESCE(SUM(COALESCE(event_price, 0) + COALESCE(menu_price, 0)), 0) as total,
            COUNT(*) as count
        FROM reservations 
        WHERE 1=1
    """
    params = []
    
    if start_date:
        query += " AND event_date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND event_date <= ?"
        params.append(end_date)
    
    row = fetch_one(query, tuple(params))
    
    return {
        "total_revenue": row[0] if row else 0,
        "event_count": row[1] if row else 0,
        "start_date": start_date or "all",
        "end_date": end_date or "all"
    }

# --- Expense Summary ---

@router.get("/expenses/summary")
def get_expense_summary(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    query = """
        SELECT 
            category,
            SUM(amount) as total
        FROM expenses 
        WHERE 1=1
    """
    params = []
    
    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)
    
    query += " GROUP BY category"
    rows = fetch_all(query, tuple(params))
    
    return [{"category": r[0], "total": r[1]} for r in rows]

# --- Profit/Loss ---

@router.get("/profit-loss", response_model=ProfitLossSummary)
def get_profit_loss(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    # Get revenue
    revenue_query = """
        SELECT COALESCE(SUM(COALESCE(event_price, 0) + COALESCE(menu_price, 0)), 0)
        FROM reservations WHERE 1=1
    """
    expense_query = "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE 1=1"
    
    params = []
    if start_date:
        revenue_query += " AND event_date >= ?"
        expense_query += " AND date >= ?"
        params.append(start_date)
    if end_date:
        revenue_query += " AND event_date <= ?"
        expense_query += " AND date <= ?"
        params.append(end_date)
    
    revenue_row = fetch_one(revenue_query, tuple(params[:len(params)//2 + len(params)%2] if start_date or end_date else ()))
    expense_row = fetch_one(expense_query, tuple(params[len(params)//2:] if start_date or end_date else ()))
    
    # Fix param passing
    rev_params = []
    exp_params = []
    if start_date:
        rev_params.append(start_date)
        exp_params.append(start_date)
    if end_date:
        rev_params.append(end_date)
        exp_params.append(end_date)
    
    revenue_row = fetch_one(revenue_query.replace(" 1=1", " 1=1"), tuple(rev_params))
    expense_row = fetch_one(expense_query.replace(" 1=1", " 1=1"), tuple(exp_params))
    
    total_revenue = revenue_row[0] if revenue_row else 0
    total_expenses = expense_row[0] if expense_row else 0
    
    return {
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "net_profit": total_revenue - total_expenses,
        "start_date": start_date or "all",
        "end_date": end_date or "all"
    }

# --- Monthly Summary for Charts ---

@router.get("/monthly-summary")
def get_monthly_summary(year: int = Query(default=2026)):
    # Revenue by month
    revenue_query = """
        SELECT strftime('%m', event_date) as month, 
               COALESCE(SUM(COALESCE(event_price, 0) + COALESCE(menu_price, 0)), 0) as total
        FROM reservations 
        WHERE strftime('%Y', event_date) = ?
        GROUP BY strftime('%m', event_date)
    """
    revenue_rows = fetch_all(revenue_query, (str(year),))
    revenue_map = {r[0]: r[1] for r in revenue_rows}
    
    # Expenses by month
    expense_query = """
        SELECT strftime('%m', date) as month, 
               COALESCE(SUM(amount), 0) as total
        FROM expenses 
        WHERE strftime('%Y', date) = ?
        GROUP BY strftime('%m', date)
    """
    expense_rows = fetch_all(expense_query, (str(year),))
    expense_map = {r[0]: r[1] for r in expense_rows}
    
    months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
    month_names = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", 
                   "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
    
    result = []
    for i, m in enumerate(months):
        rev = revenue_map.get(m, 0)
        exp = expense_map.get(m, 0)
        result.append({
            "month": month_names[i],
            "revenue": rev,
            "expenses": exp,
            "profit": rev - exp
        })
    
    return result
