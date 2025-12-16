# models/reservation_model.py
from datetime import date
from typing import Any, Dict, Iterable, List

from DugunSalonuApp_Backend.database.db_manager import execute_insert, fetch_all


RESERVATION_COLUMNS = [
    "id",
    "event_date",
    "start_time",
    "end_time",
    "event_type",
    "guests",
    "salon",
    "client_name",
    "bride_name",
    "groom_name",
    "tc_identity",
    "phone",
    "region",
    "address",
    "contract_no",
    "contract_date",
    "status",
    "event_price",
    "menu_price",
    "deposit_percent",
    "deposit_amount",
    "installments",
    "payment_type",
    "tahsilatlar",
    "menu_name",
    "menu_detail",
    "special_request",
    "note",
    "created_at",
    "updated_at",
]


def _rows_to_dicts(rows: Iterable[Iterable[Any]]) -> List[Dict[str, Any]]:
    return [dict(zip(RESERVATION_COLUMNS, row)) for row in rows]


def add_reservation(reservation: Dict[str, Any]) -> int:
    """Insert a reservation and return the created row id."""
    return execute_insert(
        """
        INSERT INTO reservations (
            event_date,
            start_time,
            end_time,
            event_type,
            guests,
            salon,
            client_name,
            bride_name,
            groom_name,
            tc_identity,
            phone,
            region,
            address,
            contract_no,
            contract_date,
            status,
            event_price,
            menu_price,
            deposit_percent,
            deposit_amount,
            installments,
            payment_type,
            tahsilatlar,
            menu_name,
            menu_detail,
            special_request,
            note
        )
        VALUES (
            :event_date,
            :start_time,
            :end_time,
            :event_type,
            :guests,
            :salon,
            :client_name,
            :bride_name,
            :groom_name,
            :tc_identity,
            :phone,
            :region,
            :address,
            :contract_no,
            :contract_date,
            :status,
            :event_price,
            :menu_price,
            :deposit_percent,
            :deposit_amount,
            :installments,
            :payment_type,
            :tahsilatlar,
            :menu_name,
            :menu_detail,
            :special_request,
            :note
        )
        """,
        reservation,
    )


def get_reservations_by_date(event_date: str) -> List[Dict[str, Any]]:
    """Return reservations for an ISO date (YYYY-MM-DD)."""
    rows = fetch_all(
        """
        SELECT
            id,
            event_date,
            start_time,
            end_time,
            event_type,
            guests,
            salon,
            client_name,
            bride_name,
            groom_name,
            tc_identity,
            phone,
            region,
            address,
            contract_no,
            contract_date,
            status,
            event_price,
            menu_price,
            deposit_percent,
            deposit_amount,
            installments,
            payment_type,
            tahsilatlar,
            menu_name,
            menu_detail,
            special_request,
            note,
            created_at,
            updated_at
        FROM reservations
        WHERE event_date = ?
        ORDER BY
            CASE WHEN start_time IS NULL OR start_time = '' THEN 1 ELSE 0 END,
            start_time,
            id
        """,
        (event_date,),
    )
    return _rows_to_dicts(rows)


def get_reservations_for_month(year: int, month: int) -> List[Dict[str, Any]]:
    """Return reservations between the first day of the month (inclusive) and the next month (exclusive)."""
    start = date(year, month, 1)
    if month == 12:
        end = date(year + 1, 1, 1)
    else:
        end = date(year, month + 1, 1)

    rows = fetch_all(
        """
        SELECT
            id,
            event_date,
            start_time,
            end_time,
            event_type,
            guests,
            salon,
            client_name,
            bride_name,
            groom_name,
            tc_identity,
            phone,
            region,
            address,
            contract_no,
            contract_date,
            status,
            event_price,
            menu_price,
            deposit_percent,
            deposit_amount,
            installments,
            payment_type,
            tahsilatlar,
            menu_name,
            menu_detail,
            special_request,
            note,
            created_at,
            updated_at
        FROM reservations
        WHERE event_date >= ?
          AND event_date < ?
        ORDER BY
            event_date,
            CASE WHEN start_time IS NULL OR start_time = '' THEN 1 ELSE 0 END,
            start_time,
            id
        """,
        (start.isoformat(), end.isoformat()),
    )
    return _rows_to_dicts(rows)
