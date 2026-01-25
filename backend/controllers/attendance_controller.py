from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from backend.database.db_manager import execute_query, fetch_all, execute_insert, fetch_one

router = APIRouter()

# --- Models ---

class AttendanceBase(BaseModel):
    staff_id: int
    date: str  # ISO date YYYY-MM-DD
    status: str = "present"  # 'present', 'late', 'absent'
    notes: Optional[str] = ""

class Attendance(AttendanceBase):
    id: int
    staff_name: Optional[str] = None

class WorkScheduleBase(BaseModel):
    staff_id: int
    date: str  # ISO date YYYY-MM-DD
    is_scheduled: bool = True
    notes: Optional[str] = ""

class WorkSchedule(WorkScheduleBase):
    id: int

# --- Table Creation ---

def create_attendance_table():
    """Create attendance table if not exists"""
    query = """
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            status TEXT DEFAULT 'present',
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (staff_id) REFERENCES staff(id),
            UNIQUE(staff_id, date)
        )
    """
    execute_query(query)

def create_schedule_table():
    """Create work schedule table if not exists"""
    query = """
        CREATE TABLE IF NOT EXISTS work_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            is_scheduled INTEGER DEFAULT 1,
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (staff_id) REFERENCES staff(id),
            UNIQUE(staff_id, date)
        )
    """
    execute_query(query)

# --- Attendance CRUD ---

@router.get("/", response_model=List[Attendance])
def get_attendance(
    date: Optional[str] = Query(None, description="Filter by date (ISO format)"),
    staff_id: Optional[int] = Query(None, description="Filter by staff ID"),
    start_date: Optional[str] = Query(None, description="Start of date range"),
    end_date: Optional[str] = Query(None, description="End of date range")
):
    """Get attendance records with optional filters"""
    query = """
        SELECT a.id, a.staff_id, a.date, a.status, a.notes, s.name
        FROM attendance a
        JOIN staff s ON a.staff_id = s.id
        WHERE 1=1
    """
    params = []
    
    if date:
        query += " AND a.date = ?"
        params.append(date)
    if staff_id:
        query += " AND a.staff_id = ?"
        params.append(staff_id)
    if start_date:
        query += " AND a.date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND a.date <= ?"
        params.append(end_date)
    
    query += " ORDER BY a.date DESC, s.name"
    
    rows = fetch_all(query, tuple(params))
    return [
        {
            "id": r[0], "staff_id": r[1], "date": r[2], 
            "status": r[3], "notes": r[4], "staff_name": r[5]
        }
        for r in rows
    ]

@router.get("/weekly")
def get_weekly_attendance(
    start_date: str = Query(..., description="Week start date (Monday)"),
    end_date: str = Query(..., description="Week end date (Sunday)")
):
    """Get attendance for a week with staff info"""
    """Get attendance and schedule for a week with staff info"""
    query = """
        SELECT 
            s.id, s.name, s.role, s.staff_type, 
            a.date as att_date, a.status, a.notes as att_notes, a.id as attendance_id,
            ws.date as sch_date, ws.is_scheduled, ws.notes as sch_notes, ws.id as schedule_id
        FROM staff s
        LEFT JOIN attendance a ON s.id = a.staff_id AND a.date BETWEEN ? AND ?
        LEFT JOIN work_schedule ws ON s.id = ws.staff_id AND ws.date BETWEEN ? AND ?
        WHERE s.is_active = 1
        ORDER BY s.name
    """
    rows = fetch_all(query, (start_date, end_date, start_date, end_date))
    
    # Group by staff
    staff_dict = {}
    for r in rows:
        staff_id = r[0]
        if staff_id not in staff_dict:
            staff_dict[staff_id] = {
                "id": r[0], "name": r[1], "role": r[2], "staff_type": r[3],
                "attendance": {},
                "schedule": {}
            }
        
        # Process attendance record
        att_date = r[4]
        if att_date:
            staff_dict[staff_id]["attendance"][att_date] = {
                "status": r[5], "notes": r[6], "attendance_id": r[7]
            }
            
        # Process schedule record
        sch_date = r[8]
        if sch_date:
            staff_dict[staff_id]["schedule"][sch_date] = {
                "is_scheduled": bool(r[9]), "notes": r[10], "schedule_id": r[11]
            }
    
    return list(staff_dict.values())

@router.post("/", response_model=Attendance)
def record_attendance(attendance: AttendanceBase):
    """Record or update attendance for a staff member on a date"""
    try:
        # Check if record exists (upsert logic)
        existing = fetch_one(
            "SELECT id FROM attendance WHERE staff_id = ? AND date = ?",
            (attendance.staff_id, attendance.date)
        )
        
        if existing:
            # Update existing
            execute_query(
                "UPDATE attendance SET status = ?, notes = ? WHERE id = ?",
                (attendance.status, attendance.notes, existing[0])
            )
            return {**attendance.dict(), "id": existing[0]}
        else:
            # Insert new
            query = "INSERT INTO attendance (staff_id, date, status, notes) VALUES (?, ?, ?, ?)"
            last_id = execute_insert(query, (attendance.staff_id, attendance.date, attendance.status, attendance.notes))
            return {**attendance.dict(), "id": last_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{attendance_id}")
def update_attendance(attendance_id: int, status: str, notes: Optional[str] = ""):
    """Update attendance status"""
    try:
        execute_query(
            "UPDATE attendance SET status = ?, notes = ? WHERE id = ?",
            (status, notes, attendance_id)
        )
        return {"message": "Yoklama güncellendi", "id": attendance_id, "status": status}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{attendance_id}")
def delete_attendance(attendance_id: int):
    """Delete attendance record"""
    execute_query("DELETE FROM attendance WHERE id = ?", (attendance_id,))
    return {"message": "Yoklama kaydı silindi"}

@router.get("/summary")
def get_attendance_summary(
    start_date: str = Query(...),
    end_date: str = Query(...)
):
    """Get attendance summary for a date range"""
    query = """
        SELECT 
            s.id, s.name, s.staff_type,
            COUNT(CASE WHEN a.status = 'present' THEN 1 END) as present_days,
            COUNT(CASE WHEN a.status = 'late' THEN 1 END) as late_days,
            COUNT(CASE WHEN a.status = 'absent' THEN 1 END) as absent_days
        FROM staff s
        LEFT JOIN attendance a ON s.id = a.staff_id AND a.date BETWEEN ? AND ?
        WHERE s.is_active = 1
        GROUP BY s.id
        ORDER BY s.name
    """
    rows = fetch_all(query, (start_date, end_date))
    return [
        {
            "staff_id": r[0], "name": r[1], "staff_type": r[2],
            "present": r[3] or 0, "late": r[4] or 0, "absent": r[5] or 0
        }
        for r in rows
    ]

# --- Schedule API ---

@router.post("/schedule", response_model=WorkSchedule)
def update_schedule(schedule: WorkScheduleBase):
    """Update work schedule for a staff member on a date"""
    try:
        # Check if record exists (upsert logic)
        existing = fetch_one(
            "SELECT id FROM work_schedule WHERE staff_id = ? AND date = ?",
            (schedule.staff_id, schedule.date)
        )
        
        if existing:
            # Update existing
            execute_query(
                "UPDATE work_schedule SET is_scheduled = ?, notes = ? WHERE id = ?",
                (int(schedule.is_scheduled), schedule.notes, existing[0])
            )
            return {**schedule.dict(), "id": existing[0]}
        else:
            # Insert new
            query = "INSERT INTO work_schedule (staff_id, date, is_scheduled, notes) VALUES (?, ?, ?, ?)"
            last_id = execute_insert(query, (schedule.staff_id, schedule.date, int(schedule.is_scheduled), schedule.notes))
            return {**schedule.dict(), "id": last_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
