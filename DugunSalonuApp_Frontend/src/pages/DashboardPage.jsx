import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";

const AUTO_REFRESH_MS = 10 * 60 * 1000;
const WEEKDAYS = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"];
const HOLIDAY_KEYS = new Set(["1-1", "23-4", "19-5", "30-8", "29-10"]);

function getTargetMonths(count = 3) {
  const today = new Date();
  const months = [];
  let year = today.getFullYear();
  let month = today.getMonth();

  for (let i = 0; i < count; i += 1) {
    months.push(new Date(year, month, 1));
    month += 1;
    if (month > 11) {
      month = 0;
      year += 1;
    }
  }

  return months;
}

function monthKey(date) {
  return `${date.getFullYear()}-${date.getMonth() + 1}`;
}

function formatIso(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function buildMonthCells(date) {
  const year = date.getFullYear();
  const month = date.getMonth();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const firstWeekday = (new Date(year, month, 1).getDay() + 6) % 7; // Monday = 0

  const cells = [];
  for (let i = 0; i < firstWeekday; i += 1) {
    cells.push(null);
  }
  for (let day = 1; day <= daysInMonth; day += 1) {
    cells.push(new Date(year, month, day));
  }
  while (cells.length % 7 !== 0) {
    cells.push(null);
  }
  return cells;
}

function isHoliday(date) {
  if (!date) {
    return false;
  }
  return HOLIDAY_KEYS.has(`${date.getDate()}-${date.getMonth() + 1}`);
}

export default function DashboardPage({ user, onLogout }) {
  const navigate = useNavigate();
  const [months, setMonths] = useState(() => getTargetMonths());
  const [calendarData, setCalendarData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [lastRefreshed, setLastRefreshed] = useState(null);

  const welcomeText = useMemo(() => {
    if (user?.name) {
      return `Hoş Geldiniz, ${user.name}! 👋`;
    }
    if (user?.username) {
      return `Hoş Geldiniz, ${user.username}! 👋`;
    }
    return "Düğün Salonu Yönetim Paneline Hoş Geldiniz 👋";
  }, [user]);

  const refreshCalendar = useCallback(async () => {
    setLoading(true);
    setError("");
    const targetMonths = getTargetMonths();
    setMonths(targetMonths);
    try {
      const payloads = await Promise.all(
        targetMonths.map((date) => api.getCalendar(date.getFullYear(), date.getMonth() + 1)),
      );
      const nextData = {};
      payloads.forEach((payload, index) => {
        nextData[monthKey(targetMonths[index])] = payload?.data || {};
      });
      setCalendarData(nextData);
      setLastRefreshed(new Date());
    } catch (err) {
      setError(err.message || "Takvim verileri alınamadı.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshCalendar();
    const timer = setInterval(() => {
      refreshCalendar();
    }, AUTO_REFRESH_MS);
    return () => clearInterval(timer);
  }, [refreshCalendar]);

  const todayLabel = useMemo(() => {
    return new Intl.DateTimeFormat("tr-TR", {
      day: "2-digit",
      month: "long",
      year: "numeric",
    }).format(new Date());
  }, []);

  const refreshStatus = loading
    ? "Son güncelleme: bekleniyor..."
    : lastRefreshed
      ? `Son güncelleme: ${lastRefreshed.toLocaleTimeString("tr-TR")}`
      : "Son güncelleme: -";

  const handleOpenReservations = useCallback(() => {
    navigate("/reservations");
  }, [navigate]);

  const handleDayClick = useCallback(
    (isoDate) => {
      if (!isoDate) {
        return;
      }
      navigate(`/reservations?date=${isoDate}`);
    },
    [navigate],
  );

  const handlePlaceholder = useCallback((section) => {
    window.alert(`${section} modülü çok yakında eklenecek.`);
  }, []);

  return (
    <div className="dashboard dashboard-main">
      <div className="dashboard-shell">
        <div className="dashboard-top-bar">
          <div className="nav-buttons">
            <button type="button" className="nav-btn" onClick={handleOpenReservations}>
              Rezervasyonlar
            </button>
            <button type="button" className="nav-btn" onClick={() => handlePlaceholder("Personel")}>
              Personel
            </button>
            <button type="button" className="nav-btn" onClick={() => handlePlaceholder("Raporlar")}>
              Raporlar
            </button>
            <button type="button" className="nav-btn" onClick={() => handlePlaceholder("Ayarlar")}>
              Ayarlar
            </button>
          </div>
          <button type="button" className="danger" onClick={onLogout}>
            Çıkış Yap
          </button>
        </div>

        <section className="dashboard-hero">
          <p className="muted">{welcomeText}</p>
          <h1>Operasyonların tek panelde</h1>
          <p className="hero-subtitle">Rezervasyonları, personeli ve raporlamayı buradan yönetebilirsiniz.</p>
          <p className="hero-date">Bugün: {todayLabel}</p>
        </section>

        <section className="calendar-card">
          <header className="calendar-header">
            <div>
              <h2>3 Aylık Rezervasyon Takvimi</h2>
              <p className="muted">Yoğun günleri ve boş slotları hızlıca görün.</p>
            </div>
            <div className="calendar-actions">
              <button type="button" onClick={refreshCalendar} disabled={loading}>
                {loading ? "Yükleniyor..." : "Takvimi Yenile"}
              </button>
              <span className="refresh-status">{refreshStatus}</span>
            </div>
          </header>

          {error && <div className="alert error">{error}</div>}

          {loading ? (
            <div className="loader">Takvim verileri yükleniyor...</div>
          ) : (
            <div className="calendar-months">
              {months.map((date) => (
                <MonthCalendar
                  key={monthKey(date)}
                  date={date}
                  eventsByDate={calendarData[monthKey(date)] || {}}
                  onDayClick={handleDayClick}
                />
              ))}
            </div>
          )}

          <Legend />
        </section>
      </div>
    </div>
  );
}

function MonthCalendar({ date, eventsByDate, onDayClick }) {
  const title = date.toLocaleDateString("tr-TR", {
    month: "long",
    year: "numeric",
  });
  const cells = useMemo(() => buildMonthCells(date), [date]);

  return (
    <div className="calendar-month">
      <h3>{title}</h3>
      <div className="calendar-weekdays">
        {WEEKDAYS.map((day) => (
          <span key={day}>{day}</span>
        ))}
      </div>
      <div className="calendar-grid">
        {cells.map((cell, index) => {
          if (!cell) {
            return <span key={`empty-${index}`} className="day-button empty" />;
          }
          const iso = formatIso(cell);
          const events = eventsByDate[iso] || [];
          const eventCount = events.length;
          const today = new Date();
          const isToday = cell.toDateString() === today.toDateString();
          const holiday = isHoliday(cell);

          const classNames = ["day-button"];
          if (holiday) {
            classNames.push("holiday");
          } else if (isToday) {
            classNames.push("today");
          } else if (eventCount) {
            classNames.push("busy");
          }

          const tooltip = eventCount
            ? events
                .map((event) => {
                  const range = [event.start, event.end].filter(Boolean).join(" - ");
                  return `${range || "Etkinlik"} • ${event.name || event.type || ""}`.trim();
                })
                .join("\n")
            : "";

          return (
            <button
              key={iso}
              type="button"
              className={classNames.join(" ")}
              onClick={() => onDayClick(iso)}
              title={tooltip}
            >
              <span>{cell.getDate()}</span>
              {eventCount > 0 && <small>({eventCount})</small>}
            </button>
          );
        })}
      </div>
    </div>
  );
}

function Legend() {
  const items = [
    { label: "Boş Gün", className: "" },
    { label: "Bayram / Özel Gün", className: "holiday" },
    { label: "Etkinlikli Gün", className: "busy" },
    { label: "Bugün", className: "today" },
  ];

  return (
    <div className="calendar-legend">
      {items.map((item) => (
        <div key={item.label} className="legend-item">
          <span className={`legend-swatch ${item.className}`} />
          <span>{item.label}</span>
        </div>
      ))}
    </div>
  );
}
