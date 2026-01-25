from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from backend.database.db_manager import execute_query, fetch_all, execute_insert, fetch_one

router = APIRouter()

# --- Models ---

class StaffBase(BaseModel):
    name: str
    role: Optional[str] = ""
    phone: Optional[str] = ""
    staff_type: str = "full_time"  # 'full_time' or 'part_time'
    wage: float = 0.0

class Staff(StaffBase):
    id: int
    is_active: bool = True

class EventStaffBase(BaseModel):
    reservation_id: int
    staff_id: int
    payment_status: str = "pending"
    notes: Optional[str] = ""

class EventStaff(EventStaffBase):
    id: int

# --- Staff CRUD ---

@router.get("/", response_model=List[Staff])
def get_all_staff():
    rows = fetch_all("SELECT id, name, role, phone, staff_type, wage, is_active FROM staff WHERE is_active = 1")
    return [
        {"id": r[0], "name": r[1], "role": r[2], "phone": r[3], "staff_type": r[4], "wage": r[5], "is_active": bool(r[6])}
        for r in rows
    ]

@router.get("/part-time", response_model=List[Staff])
def get_part_time_staff():
    rows = fetch_all("SELECT id, name, role, phone, staff_type, wage, is_active FROM staff WHERE is_active = 1 AND staff_type = 'part_time'")
    return [
        {"id": r[0], "name": r[1], "role": r[2], "phone": r[3], "staff_type": r[4], "wage": r[5], "is_active": bool(r[6])}
        for r in rows
    ]

@router.get("/full-time", response_model=List[Staff])
def get_full_time_staff():
    rows = fetch_all("SELECT id, name, role, phone, staff_type, wage, is_active FROM staff WHERE is_active = 1 AND staff_type = 'full_time'")
    return [
        {"id": r[0], "name": r[1], "role": r[2], "phone": r[3], "staff_type": r[4], "wage": r[5], "is_active": bool(r[6])}
        for r in rows
    ]

@router.post("/", response_model=Staff)
def add_staff(staff: StaffBase):
    try:
        query = "INSERT INTO staff (name, role, phone, staff_type, wage) VALUES (?, ?, ?, ?, ?)"
        last_id = execute_insert(query, (staff.name, staff.role, staff.phone, staff.staff_type, staff.wage))
        return {**staff.dict(), "id": last_id, "is_active": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{staff_id}", response_model=Staff)
def update_staff(staff_id: int, staff: StaffBase):
    try:
        query = "UPDATE staff SET name = ?, role = ?, phone = ?, staff_type = ?, wage = ? WHERE id = ?"
        execute_query(query, (staff.name, staff.role, staff.phone, staff.staff_type, staff.wage, staff_id))
        return {**staff.dict(), "id": staff_id, "is_active": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{staff_id}")
def delete_staff(staff_id: int):
    execute_query("UPDATE staff SET is_active = 0 WHERE id = ?", (staff_id,))
    return {"message": "Personel silindi (soft delete)"}

# --- Event Staff Assignment ---

@router.get("/assignments/{reservation_id}")
def get_staff_for_event(reservation_id: int):
    query = """
        SELECT es.id, es.reservation_id, es.staff_id, es.payment_status, es.notes, s.name, s.role, s.wage
        FROM event_staff es
        JOIN staff s ON es.staff_id = s.id
        WHERE es.reservation_id = ?
    """
    rows = fetch_all(query, (reservation_id,))
    return [
        {
            "id": r[0], "reservation_id": r[1], "staff_id": r[2], "payment_status": r[3], "notes": r[4],
            "staff_name": r[5], "staff_role": r[6], "staff_wage": r[7]
        }
        for r in rows
    ]

@router.post("/assignments", response_model=EventStaff)
def assign_staff_to_event(assignment: EventStaffBase):
    try:
        query = "INSERT INTO event_staff (reservation_id, staff_id, payment_status, notes) VALUES (?, ?, ?, ?)"
        last_id = execute_insert(query, (assignment.reservation_id, assignment.staff_id, assignment.payment_status, assignment.notes))
        return {**assignment.dict(), "id": last_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/assignments/{assignment_id}")
def remove_staff_from_event(assignment_id: int):
    execute_query("DELETE FROM event_staff WHERE id = ?", (assignment_id,))
    return {"message": "Personel etkinlikten çıkarıldı"}

@router.patch("/assignments/{assignment_id}/pay")
def mark_staff_paid(assignment_id: int):
    execute_query("UPDATE event_staff SET payment_status = 'paid' WHERE id = ?", (assignment_id,))
    return {"message": "Ödeme yapıldı olarak işaretlendi"}
