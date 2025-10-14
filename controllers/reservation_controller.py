# controllers/reservation_controller.py
from __future__ import annotations

from datetime import datetime
from threading import RLock
from typing import Any, Dict, List, Tuple

from models.reservation_model import (
    add_reservation,
    get_reservations_by_date,
    get_reservations_for_month,
)

TIME_SLOT_MINUTES = 15
DEFAULT_EVENT_DURATION_MINUTES = 60

_CACHE_LOCK = RLock()
_MONTH_CACHE: Dict[tuple[int, int], Dict[str, List[Dict[str, Any]]]] = {}
_DAY_CACHE: Dict[str, List[Dict[str, Any]]] = {}


def create_reservation(raw_data: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any] | None]:
    """Validate and persist a reservation payload."""
    try:
        payload = _prepare_payload(raw_data)
    except ValueError as exc:
        return False, str(exc), None

    conflict_error = _check_for_conflicts(payload)
    if conflict_error:
        return False, conflict_error, None

    try:
        reservation_id = add_reservation(payload)
    except Exception as exc:
        return False, f"Rezervasyon kaydedilemedi: {exc}", None

    _invalidate_cache_for_date(payload["event_date"])

    return True, "Rezervasyon başarıyla kaydedildi.", {
        "id": reservation_id,
        "event_date": payload["event_date"],
    }


def get_calendar_data(year: int, month: int) -> Dict[str, List[Dict[str, Any]]]:
    """Return reservations grouped by ISO date for a month."""
    key = (year, month)
    with _CACHE_LOCK:
        cached = _MONTH_CACHE.get(key)
        if cached is not None:
            return _clone_month_cache(cached)

    reservations = get_reservations_for_month(year, month)
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for res in reservations:
        grouped.setdefault(res["event_date"], []).append(_simplify_for_calendar(res))

    with _CACHE_LOCK:
        _MONTH_CACHE[key] = grouped
        for date_str in grouped.keys():
            _DAY_CACHE.pop(date_str, None)

    return _clone_month_cache(grouped)


def get_reservations_for_date(date_str: str) -> List[Dict[str, Any]]:
    """Return full reservation records for a given date (supports multiple formats)."""
    iso_date = _ensure_iso_date(date_str, "Rezervasyon tarihi")
    with _CACHE_LOCK:
        cached = _DAY_CACHE.get(iso_date)
        if cached is not None:
            return _clone_day_cache(cached)

    records = get_reservations_by_date(iso_date)

    with _CACHE_LOCK:
        _DAY_CACHE[iso_date] = records

    return _clone_day_cache(records)


def get_unavailable_slots(event_date: str, salon: str | None) -> Dict[str, List[str]]:
    """Return occupied start times and summarized ranges for the given date and salon."""
    iso_date = _ensure_iso_date(event_date, "Rezervasyon tarihi")
    salon_clean = _clean_str(salon)
    if not salon_clean:
        return {"blocked": [], "ranges": []}

    reservations = get_reservations_for_date(iso_date)
    blocked_minutes: set[int] = set()
    busy_ranges: list[tuple[int, int]] = []
    target_salon = salon_clean.lower()
    for res in reservations:
        existing_salon = _clean_str(res.get("salon"))
        if not existing_salon or existing_salon.lower() != target_salon:
            continue

        start_minutes = _safe_time_to_minutes(res.get("start_time"))
        if start_minutes is None:
            continue
        end_minutes = _safe_time_to_minutes(res.get("end_time"))
        if end_minutes is None or end_minutes <= start_minutes:
            end_minutes = start_minutes + DEFAULT_EVENT_DURATION_MINUTES
        end_minutes = min(end_minutes, 24 * 60)

        busy_ranges.append((start_minutes, end_minutes))

        slot = (start_minutes // TIME_SLOT_MINUTES) * TIME_SLOT_MINUTES
        while slot < end_minutes:
            blocked_minutes.add(slot)
            slot += TIME_SLOT_MINUTES

    blocked = [_format_time(minutes) for minutes in sorted(blocked_minutes)]
    unique_ranges: Dict[tuple[int, int], None] = {}
    for start, end in sorted(busy_ranges):
        unique_ranges.setdefault((start, end), None)

    range_labels = [
        f"{_format_time(start)} - {_format_time(end)}" for start, end in unique_ranges.keys()
    ]
    return {"blocked": blocked, "ranges": range_labels}


def clear_reservation_cache():
    with _CACHE_LOCK:
        _MONTH_CACHE.clear()
        _DAY_CACHE.clear()


def _prepare_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    event_date_iso = _ensure_iso_date(data.get("event_date"), "Rezervasyon tarihi")
    if not event_date_iso:
        raise ValueError("Rezervasyon tarihi zorunludur.")

    start_time = _ensure_time(data.get("start_time"), "Başlangıç saati")
    end_time = _ensure_time(data.get("end_time"), "Bitiş saati")
    event_type = _clean_str(data.get("event_type"))
    salon = _clean_str(data.get("salon"))
    client_name = _clean_str(data.get("client_name"))

    if not event_type:
        raise ValueError("Etkinlik türü zorunludur.")
    if not client_name:
        raise ValueError("Ad soyad alanı zorunludur.")

    start_minutes = _time_to_minutes(start_time)
    end_minutes = _time_to_minutes(end_time)
    if end_minutes <= start_minutes:
        raise ValueError("Bitiş saati başlangıç saatinden sonra olmalıdır.")

    guests = _to_positive_int(data.get("guests"), "Davetli sayısı", allow_empty=True)
    installments = _to_positive_int(data.get("installments"), "Taksit sayısı", allow_zero=True, allow_empty=True)

    payload: Dict[str, Any] = {
        "event_date": event_date_iso,
        "start_time": start_time,
        "end_time": end_time,
        "event_type": event_type,
        "guests": guests,
        "salon": salon,
        "client_name": client_name,
        "tc_identity": _clean_str(data.get("tc_identity")),
        "phone": _clean_str(data.get("phone")),
        "address": _clean_str(data.get("address")),
        "contract_no": _clean_str(data.get("contract_no")),
        "contract_date": _ensure_iso_date(data.get("contract_date"), "Sözleşme tarihi", required=False),
        "status": _clean_str(data.get("status")),
        "event_price": _to_float(data.get("event_price"), "Kişi başı etkinlik ücreti"),
        "menu_price": _to_float(data.get("menu_price"), "Kişi başı menü ücreti"),
        "deposit_percent": _to_float(data.get("deposit_percent"), "Kapora yüzdesi"),
        "deposit_amount": _to_float(data.get("deposit_amount"), "Kapora tutarı"),
        "installments": installments,
        "payment_type": _clean_str(data.get("payment_type")),
        "tahsilatlar": _clean_text_block(data.get("tahsilatlar")),
        "menu_name": _clean_str(data.get("menu_name")),
        "menu_detail": _clean_text_block(data.get("menu_detail")),
        "special_request": _clean_text_block(data.get("special_request")),
    }

    # Soft validation for logical ranges
    if payload["deposit_percent"] is not None and not 0 <= payload["deposit_percent"] <= 100:
        raise ValueError("Kapora yüzdesi 0 ile 100 arasında olmalıdır.")

    return payload


def _simplify_for_calendar(reservation: Dict[str, Any]) -> Dict[str, Any]:
    """Format reservation data for calendar display."""
    return {
        "id": reservation["id"],
        "type": reservation.get("event_type"),
        "name": reservation.get("client_name"),
        "start": reservation.get("start_time"),
        "end": reservation.get("end_time"),
        "guests": reservation.get("guests"),
        "salon": reservation.get("salon"),
        "menu": reservation.get("menu_name"),
        "notes": reservation.get("special_request"),
    }


def _clone_month_cache(source: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
    return {day: [event.copy() for event in events] for day, events in source.items()}


def _clone_day_cache(source: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [item.copy() for item in source]


def _invalidate_cache_for_date(event_date_iso: str | None):
    if not event_date_iso:
        return
    with _CACHE_LOCK:
        _DAY_CACHE.pop(event_date_iso, None)
        try:
            parsed = datetime.strptime(event_date_iso, "%Y-%m-%d")
        except ValueError:
            return
        key = (parsed.year, parsed.month)
        _MONTH_CACHE.pop(key, None)


def _ensure_iso_date(value: Any, field_label: str, required: bool = True) -> str | None:
    value = _clean_str(value)
    if not value:
        if required:
            raise ValueError(f"{field_label} zorunludur.")
        return None

    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue
    raise ValueError(f"{field_label} geçerli bir tarih olmalıdır.")


def _clean_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def _clean_text_block(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None


def _to_positive_int(value: Any, field_label: str, allow_zero: bool = False, allow_empty: bool = False) -> int | None:
    text = _clean_str(value)
    if not text:
        if allow_empty:
            return None
        raise ValueError(f"{field_label} zorunludur.")
    try:
        number = int(text)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_label} sayısal olmalıdır.") from exc
    if number < 0 or (not allow_zero and number == 0):
        raise ValueError(f"{field_label} pozitif olmalıdır.")
    return number


def _to_float(value: Any, field_label: str | None = None) -> float | None:
    text = _clean_str(value)
    if not text:
        return None
    text = text.replace(",", ".")
    try:
        return float(text)
    except (TypeError, ValueError) as exc:
        if field_label:
            raise ValueError(f"{field_label} sayısal olmalıdır.") from exc
        raise ValueError("Sayısal alanlardan biri geçersiz.") from exc


def _check_for_conflicts(reservation: Dict[str, Any]) -> str | None:
    salon = _clean_str(reservation.get("salon"))
    if not salon:
        return None

    conflicts = _find_conflicts(
        reservation["event_date"],
        salon,
        reservation["start_time"],
        reservation["end_time"],
    )
    if not conflicts:
        return None

    conflict_slots = ", ".join(_describe_conflict(conf) for conf in conflicts)
    return (
        f"{salon} salonunda {reservation['start_time']} - {reservation['end_time']} saatleri için "
        f"başka bir rezervasyon bulundu ({conflict_slots})."
    )


def _find_conflicts(event_date: str, salon: str, start_time: str, end_time: str) -> List[Dict[str, Any]]:
    start_minutes = _time_to_minutes(start_time)
    end_minutes = _time_to_minutes(end_time)
    target_salon = salon.lower()

    reservations = get_reservations_by_date(event_date)
    conflicts: List[Dict[str, Any]] = []

    for reservation in reservations:
        res_salon = _clean_str(reservation.get("salon"))
        if not res_salon or res_salon.lower() != target_salon:
            continue

        existing_start = _safe_time_to_minutes(reservation.get("start_time"))
        existing_end = _safe_time_to_minutes(reservation.get("end_time"))

        if existing_start is None:
            conflicts.append(reservation)
            continue

        if existing_end is None or existing_end <= existing_start:
            existing_end = existing_start + DEFAULT_EVENT_DURATION_MINUTES
        existing_end = min(existing_end, 24 * 60)

        if _times_overlap(start_minutes, end_minutes, existing_start, existing_end):
            conflicts.append(reservation)

    return conflicts


def _ensure_time(value: Any, field_label: str) -> str:
    text = _clean_str(value)
    if not text:
        raise ValueError(f"{field_label} zorunludur.")

    parts = text.split(":")
    if len(parts) != 2:
        raise ValueError(f"{field_label} geçerli bir saat olmalıdır (SS:dd).")

    try:
        hour = int(parts[0])
        minute = int(parts[1])
    except ValueError as exc:
        raise ValueError(f"{field_label} sayısal olmalıdır.") from exc

    if hour < 0 or hour > 24 or minute < 0 or minute > 59 or (hour == 24 and minute != 0):
        raise ValueError(f"{field_label} geçerli bir saat olmalıdır.")

    if minute % TIME_SLOT_MINUTES != 0:
        raise ValueError(f"{field_label} 15 dakikalık aralıklarla seçilmelidir.")

    return f"{hour:02d}:{minute:02d}"


def _time_to_minutes(value: str) -> int:
    hour, minute = value.split(":")
    return int(hour) * 60 + int(minute)


def _safe_time_to_minutes(value: Any) -> int | None:
    text = _clean_str(value)
    if not text:
        return None

    parts = text.split(":")
    if len(parts) != 2:
        return None

    try:
        hour = int(parts[0])
        minute = int(parts[1])
    except ValueError:
        return None

    if hour < 0 or hour > 24 or minute < 0 or minute > 59 or (hour == 24 and minute != 0):
        return None

    return hour * 60 + minute


def _times_overlap(start_a: int, end_a: int, start_b: int, end_b: int) -> bool:
    return max(start_a, start_b) < min(end_a, end_b)


def _format_time(minutes: int) -> str:
    hour = minutes // 60
    minute = minutes % 60
    return f"{hour:02d}:{minute:02d}"


def _describe_conflict(reservation: Dict[str, Any]) -> str:
    start_minutes = _safe_time_to_minutes(reservation.get("start_time"))
    end_minutes = _safe_time_to_minutes(reservation.get("end_time"))

    if start_minutes is None:
        start_label = reservation.get("start_time") or "—"
        end_label = reservation.get("end_time") or "—"
        return f"{start_label} - {end_label}"

    if end_minutes is None or end_minutes <= start_minutes:
        end_minutes = start_minutes + DEFAULT_EVENT_DURATION_MINUTES
    end_minutes = min(end_minutes, 24 * 60)

    return f"{_format_time(start_minutes)} - {_format_time(end_minutes)}"
