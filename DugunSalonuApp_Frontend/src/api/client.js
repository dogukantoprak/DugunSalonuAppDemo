import { normalizeToIsoDate } from "./date";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    let detail = "İstek başarısız oldu.";
    try {
      const payload = await response.json();
      detail = payload?.detail || payload?.message || detail;
    } catch {
      // ignore parse errors
    }
    throw new Error(detail);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

export const api = {
  login: (body) => request("/api/login", { method: "POST", body: JSON.stringify(body) }),
  register: (body) => request("/api/register", { method: "POST", body: JSON.stringify(body) }),
  getReservations: (date) => {
    const isoDate = normalizeToIsoDate(date);
    return request(`/api/reservations?date=${encodeURIComponent(isoDate || date)}`);
  },
  createReservation: (body) =>
    request("/api/reservations", {
      method: "POST",
      body: JSON.stringify(withIsoDates(body)),
    }),
  getCalendar: (year, month) => request(`/api/calendar?year=${year}&month=${month}`),
  getUnavailableSlots: (date, salon) =>
    request(
      `/api/reservations/unavailable?date=${encodeURIComponent(normalizeToIsoDate(date) || date)}&salon=${encodeURIComponent(
        salon,
      )}`,
    ),
  health: () => request("/api/health"),
};

function withIsoDates(body) {
  if (!body || typeof body !== "object") {
    return body;
  }
  const next = { ...body };
  if ("event_date" in next) {
    next.event_date = normalizeToIsoDate(next.event_date) || next.event_date;
  }
  if ("contract_date" in next) {
    next.contract_date = normalizeToIsoDate(next.contract_date) || next.contract_date;
  }
  return next;
}
