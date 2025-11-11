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
  getReservations: (date) => request(`/api/reservations?date=${encodeURIComponent(date)}`),
  createReservation: (body) =>
    request("/api/reservations", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  getCalendar: (year, month) => request(`/api/calendar?year=${year}&month=${month}`),
  health: () => request("/api/health"),
};
