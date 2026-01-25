from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from backend.database.db_manager import execute_query, fetch_all, execute_insert

router = APIRouter()

# --- Models ---

class SalonBase(BaseModel):
    name: str
    capacity: Optional[int] = 0
    price_factor: Optional[float] = 1.0
    color: Optional[str] = None
    is_active: bool = True

class Salon(SalonBase):
    id: int

class MenuBase(BaseModel):
    name: str
    content: Optional[str] = ""
    price_per_person: Optional[float] = 0.0
    is_active: bool = True

class Menu(MenuBase):
    id: int

class EventTypeBase(BaseModel):
    name: str
    default_duration: Optional[int] = 4
    is_active: bool = True

class EventType(EventTypeBase):
    id: int

# --- Salons ---

@router.get("/salons", response_model=List[Salon])
def get_salons():
    rows = fetch_all("SELECT * FROM settings_salons WHERE is_active = 1")
    return [
        {"id": r[0], "name": r[1], "capacity": r[2], "price_factor": r[3], "color": r[4], "is_active": bool(r[5])}
        for r in rows
    ]

@router.post("/salons", response_model=Salon)
def add_salon(salon: SalonBase):
    try:
        query = "INSERT INTO settings_salons (name, capacity, price_factor, color, is_active) VALUES (?, ?, ?, ?, ?)"
        last_id = execute_insert(query, (salon.name, salon.capacity, salon.price_factor, salon.color, salon.is_active))
        return {**salon.dict(), "id": last_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/salons/{salon_id}")
def delete_salon(salon_id: int):
    execute_query("UPDATE settings_salons SET is_active = 0 WHERE id = ?", (salon_id,))
    return {"message": "Salon silindi (soft delete)"}

# --- Menus ---

@router.get("/menus", response_model=List[Menu])
def get_menus():
    rows = fetch_all("SELECT * FROM settings_menus WHERE is_active = 1")
    return [
        {"id": r[0], "name": r[1], "content": r[2], "price_per_person": r[3], "is_active": bool(r[4])}
        for r in rows
    ]

@router.post("/menus", response_model=Menu)
def add_menu(menu: MenuBase):
    try:
        query = "INSERT INTO settings_menus (name, content, price_per_person, is_active) VALUES (?, ?, ?, ?)"
        last_id = execute_insert(query, (menu.name, menu.content, menu.price_per_person, menu.is_active))
        return {**menu.dict(), "id": last_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/menus/{menu_id}")
def delete_menu(menu_id: int):
    execute_query("UPDATE settings_menus SET is_active = 0 WHERE id = ?", (menu_id,))
    return {"message": "Menu silindi (soft delete)"}

# --- Event Types ---

@router.get("/event-types", response_model=List[EventType])
def get_event_types():
    rows = fetch_all("SELECT * FROM settings_event_types WHERE is_active = 1")
    return [
        {"id": r[0], "name": r[1], "default_duration": r[2], "is_active": bool(r[3])}
        for r in rows
    ]

@router.post("/event-types", response_model=EventType)
def add_event_type(event_type: EventTypeBase):
    try:
        query = "INSERT INTO settings_event_types (name, default_duration, is_active) VALUES (?, ?, ?)"
        last_id = execute_insert(query, (event_type.name, event_type.default_duration, event_type.is_active))
        return {**event_type.dict(), "id": last_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/event-types/{type_id}")
def delete_event_type(type_id: int):
    execute_query("UPDATE settings_event_types SET is_active = 0 WHERE id = ?", (type_id,))
    return {"message": "Etkinlik turu silindi (soft delete)"}
