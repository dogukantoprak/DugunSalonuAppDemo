import { useEffect, useState } from "react";
import { api } from "../api/client";
import { useNavigate } from "react-router-dom";

interface StaffMember {
    id: number;
    name: string;
    role?: string;
    phone?: string;
    staff_type: "full_time" | "part_time";
    wage: number;
    is_active: boolean;
}

interface WeeklyStaff {
    id: number;
    name: string;
    role?: string;
    staff_type: string;
    attendance: Record<string, { status: string; notes: string; attendance_id: number }>;
    schedule: Record<string, { is_scheduled: boolean; notes: string; schedule_id: number }>;
}

const STATUS_COLORS: Record<string, string> = {
    present: "#22c55e",
    late: "#f59e0b",
    absent: "#ef4444",
};

const STATUS_LABELS: Record<string, string> = {
    present: "Geldi",
    late: "Geç",
    absent: "Gelmedi",
};

// Get Monday of current week
function getWeekStart(): Date {
    const now = new Date();
    const day = now.getDay();
    const diff = now.getDate() - day + (day === 0 ? -6 : 1);
    return new Date(now.setDate(diff));
}

function formatDate(date: Date): string {
    return date.toISOString().split("T")[0];
}

function getWeekDays(start: Date): Date[] {
    return Array.from({ length: 7 }, (_, i) => {
        const d = new Date(start);
        d.setDate(start.getDate() + i);
        return d;
    });
}

function getDayName(date: Date): string {
    return date.toLocaleDateString("tr-TR", { weekday: "short" });
}

export default function PersonnelPage() {
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState<"list" | "planning">("list");
    const [staff, setStaff] = useState<StaffMember[]>([]);
    const [weeklyData, setWeeklyData] = useState<WeeklyStaff[]>([]);
    const [filter, setFilter] = useState<"all" | "full_time" | "part_time">("all");
    const [searchTerm, setSearchTerm] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [editingId, setEditingId] = useState<number | null>(null);
    const [editForm, setEditForm] = useState<Partial<StaffMember>>({});
    const [showForm, setShowForm] = useState(false);
    const [weekStart, setWeekStart] = useState<Date>(getWeekStart());

    const weekDays = getWeekDays(weekStart);
    const startDate = formatDate(weekDays[0]);
    const endDate = formatDate(weekDays[6]);

    useEffect(() => {
        fetchStaff();
    }, []);

    useEffect(() => {
        if (activeTab === "planning") {
            fetchWeeklyAttendance();
        }
    }, [activeTab, weekStart]);

    const fetchStaff = async () => {
        setLoading(true);
        try {
            const data = await api.getStaff();
            setStaff(data);
        } catch (err: any) {
            setError(err.message || "Personel listesi yüklenemedi.");
        } finally {
            setLoading(false);
        }
    };

    const fetchWeeklyAttendance = async () => {
        try {
            const data = await api.getWeeklyAttendance(startDate, endDate);
            setWeeklyData(data);
        } catch (err) {
            console.error("Weekly attendance error:", err);
        }
    };

    const handleEditClick = (member: StaffMember) => {
        setEditingId(member.id);
        setEditForm(member);
        setShowForm(true);
    };

    const handleCancelEdit = () => {
        setEditingId(null);
        setEditForm({});
        setShowForm(false);
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        const formData = new FormData(e.target as HTMLFormElement);
        const payload = {
            name: formData.get("name") as string,
            role: formData.get("role") as string,
            phone: formData.get("phone") as string,
            staff_type: formData.get("staff_type") as string,
            wage: Number(formData.get("wage")) || 0,
        };

        try {
            if (editingId) {
                await api.updateStaff(editingId, payload);
            } else {
                await api.addStaff(payload);
            }
            fetchStaff();
            handleCancelEdit();
            if (activeTab === "planning") fetchWeeklyAttendance();
        } catch (err: any) {
            alert(err.message);
        }
    };

    const handleDelete = async (id: number) => {
        if (!window.confirm("Bu personeli silmek istediğinize emin misiniz?")) return;
        try {
            await api.deleteStaff(id);
            if (activeTab === "list") fetchStaff();
            if (activeTab === "planning") fetchWeeklyAttendance();
        } catch (err: any) {
            alert(err.message);
        }
    };

    const handleAttendance = async (staffId: number, date: string, status: string) => {
        try {
            await api.recordAttendance({ staff_id: staffId, date, status });
            fetchWeeklyAttendance();
        } catch (err: any) {
            alert(err.message);
        }
    };

    const handleScheduleToggle = async (staffId: number, date: string, currentStatus: boolean) => {
        try {
            await api.updateSchedule({ staff_id: staffId, date, is_scheduled: !currentStatus });
            fetchWeeklyAttendance();
        } catch (err: any) {
            alert(err.message);
        }
    };

    const handleWeekChange = (direction: number) => {
        const newStart = new Date(weekStart);
        newStart.setDate(weekStart.getDate() + direction * 7);
        setWeekStart(newStart);
    };

    // Stats
    const fullTimeCount = staff.filter((s) => s.staff_type === "full_time").length;
    const partTimeCount = staff.filter((s) => s.staff_type === "part_time").length;

    // Filtered staff
    const filteredStaff = staff.filter((s) => {
        const matchesFilter = filter === "all" || s.staff_type === filter;
        const matchesSearch =
            s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            (s.role || "").toLowerCase().includes(searchTerm.toLowerCase());
        return matchesFilter && matchesSearch;
    });

    if (loading && !staff.length) return <div className="loader">Personel yükleniyor...</div>;

    return (
        <div className="dashboard-shell" style={{ marginTop: "2rem" }}>
            <header className="page-header">
                <div>
                    <h1>👥 Personel Yönetimi</h1>
                    <p className="muted">Ekibinizi ve çalışma durumlarını yönetin.</p>
                </div>
                <button className="secondary small" onClick={() => navigate("/")}>← Ana Sayfa</button>
            </header>

            {error && <div className="alert error">{error}</div>}

            {/* Stats Cards */}
            <div className="stats-grid" style={{ marginBottom: "1.5rem" }}>
                <div className="card stat-card">
                    <div className="stat-content">
                        <span className="stat-label">Toplam Personel</span>
                        <span className="stat-value">{staff.length}</span>
                    </div>
                </div>
                <div className="card stat-card">
                    <div className="stat-content">
                        <span className="stat-label">🏢 Kadrolu</span>
                        <span className="stat-value">{fullTimeCount}</span>
                    </div>
                </div>
                <div className="card stat-card">
                    <div className="stat-content">
                        <span className="stat-label">🕒 Part-Time</span>
                        <span className="stat-value">{partTimeCount}</span>
                    </div>
                </div>
            </div>

            {/* Tab Navigation */}
            <div className="form-tabs" style={{ marginBottom: "1rem" }}>
                <button
                    className={activeTab === "list" ? "active" : ""}
                    onClick={() => setActiveTab("list")}
                >
                    📋 Personel Listesi
                </button>
                <button
                    className={activeTab === "planning" ? "active" : ""}
                    onClick={() => setActiveTab("planning")}
                >
                    📅 Haftalık Planlama
                </button>
            </div>

            {activeTab === "list" && (
                <div className="fade-in">
                    {/* Filter & Actions Bar */}
                    <div className="actions-bar" style={{ marginBottom: "1.5rem" }}>
                        <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", alignItems: "center" }}>
                            <div className="search-wrapper" style={{ flex: 1, minWidth: "200px", position: "relative" }}>
                                <span style={{ position: "absolute", left: "12px", top: "50%", transform: "translateY(-50%)", opacity: 0.7 }}>🔍</span>
                                <input
                                    type="text"
                                    placeholder="Personel ara..."
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                    className="search-input"
                                    style={{
                                        width: "100%",
                                        padding: "0.75rem 0.75rem 0.75rem 2.5rem",
                                        borderRadius: "10px",
                                        border: "1px solid rgba(255,255,255,0.1)",
                                        background: "rgba(15,23,42,0.6)",
                                        color: "white"
                                    }}
                                />
                            </div>
                            <div className="filter-group">
                                <button className={`filter-btn ${filter === "all" ? "active" : ""}`} onClick={() => setFilter("all")}>
                                    Tümü
                                </button>
                                <button className={`filter-btn ${filter === "full_time" ? "active" : ""}`} onClick={() => setFilter("full_time")}>
                                    Kadrolu
                                </button>
                                <button className={`filter-btn ${filter === "part_time" ? "active" : ""}`} onClick={() => setFilter("part_time")}>
                                    Part-Time
                                </button>
                            </div>
                        </div>
                        <button className="primary" onClick={() => setShowForm(true)}>
                            + Yeni Personel
                        </button>
                    </div>

                    {/* Staff Grid */}
                    <div className="staff-grid">
                        {filteredStaff.length === 0 ? (
                            <div className="empty-state card">
                                <span className="emoji">👥</span>
                                <p>{searchTerm ? "Aramayla eşleşen personel bulunamadı." : "Bu filtrede gösterilecek personel bulunamadı."}</p>
                            </div>
                        ) : (
                            filteredStaff.map((member) => (
                                <div key={member.id} className="card staff-card fade-in">
                                    <div className="staff-avatar">
                                        {member.name.charAt(0).toUpperCase()}
                                    </div>
                                    <div className="staff-info">
                                        <h3>{member.name}</h3>
                                        <p className="role">{member.role || "Görevsiz"}</p>
                                        <div className="tags">
                                            <span className={`tag ${member.staff_type}`}>
                                                {member.staff_type === "full_time" ? "Kadrolu" : "Part-Time"}
                                            </span>
                                            {member.wage > 0 && (
                                                <span className="tag wage">
                                                    {member.wage} TL {member.staff_type === "full_time" ? "/ Ay" : "/ Gün"}
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                    <div className="staff-actions">
                                        <a href={`tel:${member.phone}`} className="icon-btn" title="Ara">📞</a>
                                        <button className="icon-btn" onClick={() => handleEditClick(member)} title="Düzenle">
                                            ✏️
                                        </button>
                                        <button className="icon-btn danger" onClick={() => handleDelete(member.id)} title="Sil">
                                            🗑️
                                        </button>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            )}

            {activeTab === "planning" && (
                <div className="card fade-in" style={{ marginBottom: "2rem" }}>
                    <div className="card-header">
                        <h3>📅 Haftalık Planlama ve Yoklama</h3>
                        <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
                            <button className="ghost small" onClick={() => handleWeekChange(-1)}>← Önceki</button>
                            <span style={{ fontWeight: 600, color: "#94a3b8" }}>
                                {weekDays[0].toLocaleDateString("tr-TR", { day: "numeric", month: "short" })} - {weekDays[6].toLocaleDateString("tr-TR", { day: "numeric", month: "short" })}
                            </span>
                            <button className="ghost small" onClick={() => handleWeekChange(1)}>Sonraki →</button>
                        </div>
                    </div>

                    <div style={{ overflowX: "auto" }}>
                        <table className="modern-table">
                            <thead>
                                <tr>
                                    <th style={{ minWidth: "200px" }}>Personel</th>
                                    {weekDays.map((day) => (
                                        <th key={day.toISOString()} style={{ textAlign: "center", minWidth: "120px" }}>
                                            {getDayName(day)}
                                            <br />
                                            <span style={{ fontSize: "0.8rem", opacity: 0.7 }}>{day.getDate()}</span>
                                        </th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {weeklyData.map((member) => (
                                    <tr key={member.id}>
                                        <td>
                                            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                                                <span className="staff-avatar" style={{ width: "32px", height: "32px", fontSize: "0.9rem" }}>
                                                    {member.name.charAt(0)}
                                                </span>
                                                <div>
                                                    <div style={{ fontWeight: 600 }}>{member.name}</div>
                                                    <div style={{ fontSize: "0.8rem", color: "#94a3b8" }}>{member.role || "-"}</div>
                                                </div>
                                            </div>
                                        </td>
                                        {weekDays.map((day) => {
                                            const dateStr = formatDate(day);
                                            const schedule = member.schedule?.[dateStr];
                                            const att = member.attendance?.[dateStr];
                                            const isScheduled = schedule?.is_scheduled;

                                            return (
                                                <td key={dateStr}>
                                                    <div style={{ display: "flex", flexDirection: "column", gap: "6px", alignItems: "center" }}>
                                                        {/* Row 1: Planning Toggle */}
                                                        <label
                                                            className="tag"
                                                            style={{
                                                                cursor: "pointer",
                                                                background: isScheduled ? "rgba(96, 165, 250, 0.2)" : "rgba(255, 255, 255, 0.05)",
                                                                color: isScheduled ? "#60a5fa" : "#64748b",
                                                                border: isScheduled ? "1px solid rgba(96, 165, 250, 0.3)" : "1px solid transparent",
                                                                fontSize: "0.75rem",
                                                                padding: "2px 8px",
                                                                display: "flex",
                                                                alignItems: "center",
                                                                gap: "4px"
                                                            }}
                                                        >
                                                            <input
                                                                type="checkbox"
                                                                checked={!!isScheduled}
                                                                onChange={() => handleScheduleToggle(member.id, dateStr, !!isScheduled)}
                                                                style={{ display: "none" }}
                                                            />
                                                            {isScheduled ? "Planlı" : "Boş"}
                                                        </label>

                                                        {/* Row 2: Attendance Buttons (only if scheduled) */}
                                                        {isScheduled && (
                                                            <div style={{ display: "flex", gap: "2px", justifyContent: "center" }}>
                                                                {["present", "late", "absent"].map((status) => (
                                                                    <button
                                                                        key={status}
                                                                        className="icon-btn"
                                                                        style={{
                                                                            background: att?.status === status ? STATUS_COLORS[status] : "transparent",
                                                                            padding: "4px",
                                                                            width: "24px",
                                                                            height: "24px",
                                                                            fontSize: "0.7rem",
                                                                            opacity: att?.status === status ? 1 : 0.4,
                                                                            border: att?.status === status ? "none" : "1px solid rgba(255,255,255,0.1)"
                                                                        }}
                                                                        onClick={() => handleAttendance(member.id, dateStr, status)}
                                                                        title={STATUS_LABELS[status]}
                                                                    >
                                                                        {status === "present" ? "✓" : status === "late" ? "⏰" : "✗"}
                                                                    </button>
                                                                ))}
                                                            </div>
                                                        )}
                                                    </div>
                                                </td>
                                            );
                                        })}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* Modal Form */}
            {showForm && (
                <div className="form-overlay" onClick={handleCancelEdit}>
                    <div className="form-dialog" onClick={(e) => e.stopPropagation()}>
                        <header>
                            <h3>{editingId ? "Personel Düzenle" : "Yeni Personel Ekle"}</h3>
                            <button className="icon-btn" onClick={handleCancelEdit}>✕</button>
                        </header>
                        <form onSubmit={handleSubmit}>
                            <div className="form-grid">
                                <label>
                                    Ad Soyad *
                                    <input name="name" placeholder="Örn: Ahmet Yılmaz" defaultValue={editForm.name} required />
                                </label>
                                <label>
                                    Görev
                                    <input name="role" placeholder="Örn: Garson, Aşçı" defaultValue={editForm.role} />
                                </label>
                                <label>
                                    Telefon
                                    <input name="phone" placeholder="05XX..." defaultValue={editForm.phone} />
                                </label>
                                <label>
                                    Çalışan Tipi *
                                    <select name="staff_type" defaultValue={editForm.staff_type || "full_time"} required>
                                        <option value="full_time">Kadrolu (Aylık Maaş)</option>
                                        <option value="part_time">Part-Time (Günlük Yevmiye)</option>
                                    </select>
                                </label>
                                <label>
                                    Ücret Bilgisi (TL)
                                    <input name="wage" type="number" placeholder="Miktar giriniz" defaultValue={editForm.wage} />
                                </label>
                            </div>
                            <div className="form-actions">
                                <button type="button" className="ghost" onClick={handleCancelEdit}>İptal</button>
                                <button type="submit" className="primary">{editingId ? "Güncelle" : "Kaydet"}</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
