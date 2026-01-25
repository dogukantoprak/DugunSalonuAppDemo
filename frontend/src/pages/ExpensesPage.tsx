import { useEffect, useState } from "react";
import { api } from "../api/client";
import { useNavigate } from "react-router-dom";

interface Expense {
    id: number;
    date: string;
    category: string;
    description: string;
    amount: number;
}

const CATEGORIES = [
    { value: "staff", label: "Personel" },
    { value: "supplies", label: "Malzeme" },
    { value: "rent", label: "Kira" },
    { value: "marketing", label: "Pazarlama" },
    { value: "other", label: "Diğer" },
];

const CATEGORY_COLORS: Record<string, string> = {
    staff: "#3b82f6",
    supplies: "#10b981",
    rent: "#f59e0b",
    marketing: "#8b5cf6",
    other: "#6b7280",
};

export default function ExpensesPage() {
    const navigate = useNavigate();
    const [expenses, setExpenses] = useState<Expense[]>([]);
    const [loading, setLoading] = useState(true);
    const [showExpenseForm, setShowExpenseForm] = useState(false);
    const [editingExpense, setEditingExpense] = useState<Expense | null>(null);
    const [searchTerm, setSearchTerm] = useState("");
    const [selectedCategory, setSelectedCategory] = useState("all");

    // Date range for current month
    const now = new Date();
    const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split("T")[0];
    const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0).toISOString().split("T")[0];

    useEffect(() => {
        fetchExpenses();
    }, []);

    const fetchExpenses = async () => {
        setLoading(true);
        try {
            const data = await api.getExpenses(startOfMonth, endOfMonth);
            setExpenses(data);
        } catch (err) {
            console.error("Failed to fetch expenses:", err);
        } finally {
            setLoading(false);
        }
    };

    const handleAddExpense = async (e: React.FormEvent) => {
        e.preventDefault();
        const formData = new FormData(e.target as HTMLFormElement);
        try {
            await api.addExpense({
                date: formData.get("date") as string,
                category: formData.get("category") as string,
                description: formData.get("description") as string,
                amount: Number(formData.get("amount")) || 0,
            });
            fetchExpenses();
            setShowExpenseForm(false);
            setEditingExpense(null);
        } catch (err: any) {
            alert(err.message);
        }
    };

    const handleDeleteExpense = async (id: number) => {
        if (!window.confirm("Bu gideri silmek istediğinize emin misiniz?")) return;
        try {
            await api.deleteExpense(id);
            fetchExpenses();
        } catch (err: any) {
            alert(err.message);
        }
    };

    const formatCurrency = (amount: number) => {
        return new Intl.NumberFormat("tr-TR", { style: "currency", currency: "TRY" }).format(amount);
    };

    const totalExpenses = expenses.reduce((sum, exp) => sum + exp.amount, 0);

    const filteredExpenses = expenses.filter((exp) => {
        const matchesSearch =
            (exp.description || "").toLowerCase().includes(searchTerm.toLowerCase()) ||
            formatCurrency(exp.amount).includes(searchTerm);
        const matchesCategory = selectedCategory === "all" || exp.category === selectedCategory;
        return matchesSearch && matchesCategory;
    });

    if (loading) return <div className="loader">Giderler yükleniyor...</div>;

    return (
        <div className="dashboard-shell" style={{ marginTop: "2rem" }}>
            <header className="page-header">
                <div>
                    <h1>💵 Gider Yönetimi</h1>
                    <p className="muted">Harcamalarınızı detaylı olarak kaydedin ve takip edin.</p>
                </div>
                <button className="secondary small" onClick={() => navigate("/")}>
                    ← Ana Sayfa
                </button>
            </header>

            {/* Summary Stats */}
            <div className="stats-grid" style={{ marginBottom: "2rem" }}>
                <div className="card stat-card glow-danger">
                    <div className="stat-icon expense-icon">💸</div>
                    <div className="stat-content">
                        <span className="stat-label">Toplam Gider</span>
                        <span className="stat-value expense-text">
                            {formatCurrency(totalExpenses)}
                        </span>
                        <span className="stat-subtext">Bu ay ({expenses.length} kayıt)</span>
                    </div>
                </div>
            </div>

            {/* Main Card */}
            <div className="card fade-in">
                <div className="card-header">
                    <div>
                        <h3>📋 Gider Listesi</h3>
                    </div>
                    <button className="primary" onClick={() => { setEditingExpense(null); setShowExpenseForm(true); }}>
                        + Yeni Gider Ekle
                    </button>
                </div>

                {/* Filter Bar */}
                <div className="filter-bar" style={{ marginBottom: "1rem", display: "flex", gap: "1rem", flexWrap: "wrap", alignItems: "center" }}>
                    <div className="search-wrapper" style={{ flex: 1, minWidth: "200px", position: "relative" }}>
                        <span style={{ position: "absolute", left: "12px", top: "50%", transform: "translateY(-50%)", opacity: 0.7 }}>🔍</span>
                        <input
                            type="text"
                            placeholder="Gider ara..."
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
                    <select
                        value={selectedCategory}
                        onChange={(e) => setSelectedCategory(e.target.value)}
                        style={{ minWidth: "150px" }}
                    >
                        <option value="all">Tüm Kategoriler</option>
                        {CATEGORIES.map(c => (
                            <option key={c.value} value={c.value}>{c.label}</option>
                        ))}
                    </select>
                </div>

                {/* Modal Form */}
                {showExpenseForm && (
                    <div className="form-overlay" onClick={() => setShowExpenseForm(false)}>
                        <div className="form-dialog" onClick={(e) => e.stopPropagation()}>
                            <header>
                                <h3>{editingExpense ? "Gider Düzenle" : "Yeni Gider Ekle"}</h3>
                                <button className="icon-btn" onClick={() => setShowExpenseForm(false)}>✕</button>
                            </header>
                            <form onSubmit={handleAddExpense}>
                                <div className="form-grid">
                                    <label>
                                        Tarih *
                                        <input
                                            type="date"
                                            name="date"
                                            defaultValue={editingExpense?.date || new Date().toISOString().split("T")[0]}
                                            required
                                        />
                                    </label>
                                    <label>
                                        Kategori *
                                        <select name="category" defaultValue={editingExpense?.category || CATEGORIES[0].value} required>
                                            {CATEGORIES.map((c) => (
                                                <option key={c.value} value={c.value}>
                                                    {c.label}
                                                </option>
                                            ))}
                                        </select>
                                    </label>
                                    <label>
                                        Tutar (TL) *
                                        <input
                                            type="number"
                                            name="amount"
                                            placeholder="0.00"
                                            step="0.01"
                                            defaultValue={editingExpense?.amount || ""}
                                            required
                                        />
                                    </label>
                                    <label>
                                        Açıklama
                                        <input
                                            type="text"
                                            name="description"
                                            placeholder="Örn: Elektrik Faturası"
                                            defaultValue={editingExpense?.description || ""}
                                        />
                                    </label>
                                </div>
                                <div className="form-actions">
                                    <button type="button" className="ghost" onClick={() => setShowExpenseForm(false)}>İptal</button>
                                    <button type="submit" className="primary">💾 Kaydet</button>
                                </div>
                            </form>
                        </div>
                    </div>
                )}

                {/* Expense Table */}
                <div className="expense-list-container">
                    {filteredExpenses.length === 0 ? (
                        <div className="empty-state">
                            <span className="emoji">🧾</span>
                            <p>
                                {expenses.length === 0
                                    ? "Bu dönemde herhangi bir gider kaydı bulunamadı."
                                    : "Aramanızla eşleşen gider bulunamadı."}
                            </p>
                        </div>
                    ) : (
                        <table className="modern-table">
                            <thead>
                                <tr>
                                    <th>Tarih</th>
                                    <th>Kategori</th>
                                    <th>Açıklama</th>
                                    <th style={{ textAlign: "right" }}>Tutar</th>
                                    <th style={{ width: "50px" }}></th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredExpenses.map((exp) => (
                                    <tr key={exp.id}>
                                        <td>{new Date(exp.date).toLocaleDateString('tr-TR')}</td>
                                        <td>
                                            <span
                                                className="tag"
                                                style={{
                                                    background: CATEGORY_COLORS[exp.category] + "22",
                                                    color: CATEGORY_COLORS[exp.category],
                                                    border: `1px solid ${CATEGORY_COLORS[exp.category]}44`,
                                                    fontWeight: 600
                                                }}
                                            >
                                                {CATEGORIES.find((c) => c.value === exp.category)?.label || exp.category}
                                            </span>
                                        </td>
                                        <td className="muted">{exp.description || "-"}</td>
                                        <td style={{ fontWeight: 700, textAlign: "right", color: "#f87171" }}>
                                            -{formatCurrency(exp.amount)}
                                        </td>
                                        <td>
                                            <button
                                                className="icon-btn danger"
                                                onClick={() => handleDeleteExpense(exp.id)}
                                                title="Sil"
                                            >
                                                🗑️
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                            <tfoot>
                                <tr>
                                    <td colSpan={3} style={{ fontWeight: 700 }}>Toplam</td>
                                    <td style={{ fontWeight: 700, textAlign: "right", color: "#f87171" }}>
                                        -{formatCurrency(filteredExpenses.reduce((sum, e) => sum + e.amount, 0))}
                                    </td>
                                    <td></td>
                                </tr>
                            </tfoot>
                        </table>
                    )}
                </div>
            </div>
        </div>
    );
}
