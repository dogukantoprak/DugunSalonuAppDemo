from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.controllers.reservation_controller import (
    create_reservation,
    get_calendar_data,
    get_reservations_for_date,
    get_unavailable_slots,
)
from backend.controllers.user_controller import (
    login_user,
    register_user,
)
from backend.database.db_manager import create_tables
from backend.controllers.settings_controller import router as settings_router
from backend.controllers.personnel_controller import router as personnel_router
from backend.controllers.reports_controller import router as reports_router
from backend.controllers.attendance_controller import router as attendance_router, create_attendance_table, create_schedule_table


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: str
    username: str
    password: str
    phone1: Optional[str] = None
    phone2: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None


class ReservationPayload(BaseModel):
    event_date: str
    start_time: str
    end_time: str
    event_type: str
    salon: str
    client_name: str
    bride_name: Optional[str] = None
    groom_name: Optional[str] = None
    guests: Optional[int] = None
    tc_identity: Optional[str] = None
    phone: Optional[str] = None
    region: Optional[str] = None
    address: Optional[str] = None
    contract_no: Optional[str] = None
    contract_date: Optional[str] = None
    status: Optional[str] = None
    event_price: Optional[float] = None
    menu_price: Optional[float] = None
    deposit_percent: Optional[float] = None
    deposit_amount: Optional[float] = None
    installments: Optional[int] = None
    payment_type: Optional[str] = None
    tahsilatlar: Optional[str] = None
    menu_name: Optional[str] = None
    menu_detail: Optional[str] = None
    special_request: Optional[str] = None
    note: Optional[str] = None


def create_app() -> FastAPI:
    app = FastAPI(
        title="Düğün Salonu Backend API",
        version="1.0.0",
        description="REST API powering the React frontend.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(settings_router, prefix="/api/settings", tags=["settings"])
    app.include_router(personnel_router, prefix="/api/personnel", tags=["personnel"])
    app.include_router(reports_router, prefix="/api/reports", tags=["reports"])
    app.include_router(attendance_router, prefix="/api/attendance", tags=["attendance"])

    @app.on_event("startup")
    def _startup():
        create_tables()
        create_attendance_table()
        create_schedule_table()

    @app.get("/api/health")
    def health_check():
        return {"status": "ok"}

    @app.post("/api/login")
    def login(payload: LoginRequest):
        success, message, user = login_user(payload.username, payload.password)
        if not success or not user:
            raise HTTPException(status_code=401, detail=message)
        return {"message": message, "user": user}

    @app.post("/api/register", status_code=201)
    def register(payload: RegisterRequest):
        data = {
            "name": payload.name,
            "email": payload.email,
            "phone1": payload.phone1 or "",
            "phone2": payload.phone2 or "",
            "address": payload.address or "",
            "city": payload.city or "",
            "district": payload.district or "",
            "username": payload.username,
            "password": payload.password,
        }
        success, message = register_user(data)
        if not success:
            raise HTTPException(status_code=400, detail=message)
        return {"message": message}

    @app.get("/api/reservations")
    def reservations_for_date(date: str = Query(..., description="ISO date (YYYY-MM-DD)")):
        records = get_reservations_for_date(date)
        return {"items": records}

    @app.post("/api/reservations", status_code=201)
    def add_reservation(payload: ReservationPayload):
        payload_dict: Dict[str, Any] = payload.dict()
        success, message, info = create_reservation(payload_dict)
        if not success:
            raise HTTPException(status_code=400, detail=message)
        response = {"message": message, "reservation": info}
        return response

    @app.get("/api/reservations/unavailable")
    def unavailable_slots(
        date: str = Query(..., description="ISO date (YYYY-MM-DD)"),
        salon: str = Query(..., description="Salon adı"),
    ):
        data = get_unavailable_slots(date, salon)
        return data

    @app.get("/api/calendar")
    def calendar(
        year: int = Query(..., ge=2000, le=2100),
        month: int = Query(..., ge=1, le=12),
    ):
        data = get_calendar_data(year, month)
        return {"data": data}

    return app


app = create_app()
