import { normalizeToIsoDate } from "./date";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

interface RequestOptions extends RequestInit {
  headers?: Record<string, string>;
}

interface LoginBody {
  username: string;
  password: string;
}

interface RegisterBody {
  name: string;
  email: string;
  username: string;
  password: string;
  phone1?: string;
  phone2?: string;
  address?: string;
  city?: string;
  district?: string;
}

export interface Reservation {
  id?: number;
  event_date: string;
  start_time: string;
  end_time: string;
  event_type: string;
  guests?: number;
  salon: string;
  client_name: string;
  bride_name?: string;
  groom_name?: string;
  tc_identity?: string;
  phone?: string;
  region?: string;
  address?: string;
  contract_no?: string;
  contract_date?: string;
  status?: string;
  event_price?: number;
  menu_price?: number;
  deposit_percent?: number;
  deposit_amount?: number;
  installments?: number;
  payment_type?: string;
  tahsilatlar?: string;
  menu_name?: string;
  menu_detail?: string;
  special_request?: string;
  note?: string;
}

interface UnavailableSlotsResponse {
  blocked: string[];
  ranges: string[];
}

interface CalendarResponse {
  data: Record<string, Array<{ id: number; type: string; name: string; start: string; end: string }>>;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
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
    return null as T;
  }

  return response.json() as Promise<T>;
}

export const api = {
  login: (body: LoginBody) =>
    request<{ message: string; user: Record<string, unknown> }>("/api/login", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  register: (body: RegisterBody) =>
    request<{ message: string }>("/api/register", { method: "POST", body: JSON.stringify(body) }),
  getReservations: (date: string) => {
    const isoDate = normalizeToIsoDate(date);
    return request<{ items: Reservation[] }>(`/api/reservations?date=${encodeURIComponent(isoDate || date)}`);
  },
  createReservation: (body: Partial<Reservation>) =>
    request<{ message: string; reservation: { id: number; event_date: string } }>("/api/reservations", {
      method: "POST",
      body: JSON.stringify(withIsoDates(body)),
    }),
  getCalendar: (year: number, month: number) =>
    request<CalendarResponse>(`/api/calendar?year=${year}&month=${month}`),
  getUnavailableSlots: (date: string, salon: string) =>
    request<UnavailableSlotsResponse>(
      `/api/reservations/unavailable?date=${encodeURIComponent(normalizeToIsoDate(date) || date)}&salon=${encodeURIComponent(salon)}`,
    ),
  health: () => request<{ status: string }>("/api/health"),

  // --- Settings API Methods ---
  getSalons: () => request<any[]>("/api/settings/salons"),
  addSalon: (data: any) =>
    request<any>("/api/settings/salons", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  deleteSalon: (id: number) => request<{ message: string }>(`/api/settings/salons/${id}`, { method: "DELETE" }),

  getMenus: () => request<any[]>("/api/settings/menus"),
  addMenu: (data: any) =>
    request<any>("/api/settings/menus", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  deleteMenu: (id: number) => request<{ message: string }>(`/api/settings/menus/${id}`, { method: "DELETE" }),

  getEventTypes: () => request<any[]>("/api/settings/event-types"),

  // --- Personnel API Methods ---
  getStaff: () => request<any[]>("/api/personnel/"),
  addStaff: (data: any) =>
    request<any>("/api/personnel/", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  updateStaff: (id: number, data: any) =>
    request<any>(`/api/personnel/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  deleteStaff: (id: number) => request<{ message: string }>(`/api/personnel/${id}`, { method: "DELETE" }),
  getStaffAssignments: (reservationId: number) => request<any[]>(`/api/personnel/assignments/${reservationId}`),
  assignStaff: (data: any) =>
    request<any>("/api/personnel/assignments", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // --- Reports API Methods ---
  getRevenue: (startDate?: string, endDate?: string) => {
    const params = new URLSearchParams();
    if (startDate) params.append("start_date", startDate);
    if (endDate) params.append("end_date", endDate);
    return request<any>(`/api/reports/revenue?${params.toString()}`);
  },
  getExpenses: (startDate?: string, endDate?: string, category?: string) => {
    const params = new URLSearchParams();
    if (startDate) params.append("start_date", startDate);
    if (endDate) params.append("end_date", endDate);
    if (category) params.append("category", category);
    return request<any[]>(`/api/reports/expenses?${params.toString()}`);
  },
  addExpense: (data: any) =>
    request<any>("/api/reports/expenses", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  deleteExpense: (id: number) =>
    request<{ message: string }>(`/api/reports/expenses/${id}`, { method: "DELETE" }),
  getProfitLoss: (startDate?: string, endDate?: string) => {
    const params = new URLSearchParams();
    if (startDate) params.append("start_date", startDate);
    if (endDate) params.append("end_date", endDate);
    return request<any>(`/api/reports/profit-loss?${params.toString()}`);
  },
  getMonthlySummary: (year: number) =>
    request<any[]>(`/api/reports/monthly-summary?year=${year}`),
  getExpenseSummary: (startDate?: string, endDate?: string) => {
    const params = new URLSearchParams();
    if (startDate) params.append("start_date", startDate);
    if (endDate) params.append("end_date", endDate);
    return request<any[]>(`/api/reports/expenses/summary?${params.toString()}`);
  },

  // --- Attendance API Methods ---
  getAttendance: (date?: string, staffId?: number) => {
    const params = new URLSearchParams();
    if (date) params.append("date", date);
    if (staffId) params.append("staff_id", String(staffId));
    return request<any[]>(`/api/attendance/?${params.toString()}`);
  },
  getWeeklyAttendance: (startDate: string, endDate: string) =>
    request<any[]>(`/api/attendance/weekly?start_date=${startDate}&end_date=${endDate}`),
  recordAttendance: (data: { staff_id: number; date: string; status: string; notes?: string }) =>
    request<any>("/api/attendance/", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  getAttendanceSummary: (startDate: string, endDate: string) =>
    request<any[]>(`/api/attendance/summary?start_date=${startDate}&end_date=${endDate}`),
  updateSchedule: (data: { staff_id: number; date: string; is_scheduled: boolean; notes?: string }) =>
    request<any>("/api/attendance/schedule", {
      method: "POST",
      body: JSON.stringify(data),
    }),
};

function withIsoDates<T extends Record<string, unknown>>(body: T): T {
  if (!body || typeof body !== "object") {
    return body;
  }
  const next = { ...body } as T;
  if ("event_date" in next) {
    (next as Record<string, unknown>).event_date =
      normalizeToIsoDate(next.event_date as string) || next.event_date;
  }
  if ("contract_date" in next) {
    (next as Record<string, unknown>).contract_date =
      normalizeToIsoDate(next.contract_date as string) || next.contract_date;
  }
  return next;
}
