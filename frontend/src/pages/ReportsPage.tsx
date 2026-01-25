import { useEffect, useState } from "react";
import { api } from "../api/client";
import { useNavigate } from "react-router-dom";

interface ProfitLoss {
    total_revenue: number;
    total_expenses: number;
    net_profit: number;
}

interface Expense {
    id: number;
    date: string;
    category: string;
    description: string;
    amount: number;
}

interface MonthlySummary {
    month: string;
    revenue: number;
    expenses: number;
    profit: number;
}

interface CategorySummary {
    category: string;
    total: number;
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

export default function ReportsPage() {
    const navigate = useNavigate();
    const [profitLoss, setProfitLoss] = useState<ProfitLoss | null>(null);
    const [expenses, setExpenses] = useState<Expense[]>([]);
    const [monthlySummary, setMonthlySummary] = useState<MonthlySummary[]>([]);
    const [categorySummary, setCategorySummary] = useState<CategorySummary[]>([]);
    const [loading, setLoading] = useState(true);
    const [showExpenseForm, setShowExpenseForm] = useState(false);

    const currentYear = new Date().getFullYear();
    const [selectedYear] = useState(currentYear);
    const [searchTerm, setSearchTerm] = useState("");
    const [selectedCategory, setSelectedCategory] = useState("all");

    // Date range for current month
    const now = new Date();
    const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split("T")[0];
    const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0).toISOString().split("T")[0];

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        setLoading(true);
        try {
            const [pl, exp, monthly, catSum] = await Promise.all([
                api.getProfitLoss(startOfMonth, endOfMonth),
                api.getExpenses(startOfMonth, endOfMonth),
                api.getMonthlySummary(selectedYear),
                api.getExpenseSummary(startOfMonth, endOfMonth),
            ]);
            setProfitLoss(pl);
            setExpenses(exp);
            setMonthlySummary(monthly);
            setCategorySummary(catSum);
        } catch (err) {
            console.error("Failed to fetch report data:", err);
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
            fetchData();
            setShowExpenseForm(false);
            (e.target as HTMLFormElement).reset();
        } catch (err: any) {
            alert(err.message);
        }
    };

    const handleDeleteExpense = async (id: number) => {
        if (!window.confirm("Bu gideri silmek istediğinize emin misiniz?")) return;
        try {
            await api.deleteExpense(id);
            fetchData();
        } catch (err: any) {
            alert(err.message);
        }
    };

    const formatCurrency = (amount: number) => {
        return new Intl.NumberFormat("tr-TR", { style: "currency", currency: "TRY" }).format(amount);
    };

    const maxRevenue = Math.max(...monthlySummary.map((m) => m.revenue), 1);

    const filteredExpenses = expenses.filter((exp) => {
        const matchesSearch =
            (exp.description || "").toLowerCase().includes(searchTerm.toLowerCase()) ||
            formatCurrency(exp.amount).includes(searchTerm);
        const matchesCategory = selectedCategory === "all" || exp.category === selectedCategory;
        return matchesSearch && matchesCategory;
    });

    if (loading) return <div className="loader">Raporlar yükleniyor...</div>;

    return (
        <div className="dashboard-shell" style={{ marginTop: "2rem" }}>
            <header className="page-header">
                <div>
                    <h1>📊 Finansal Raporlar</h1>
                    <p className="muted">İşletmenizin finansal durumunu anlık takip edin.</p>
                </div>
                <button className="secondary small" onClick={() => navigate("/")}>
                    ← Ana Sayfa
                </button>
            </header>

            {/* Summary Cards */}
            <div className="stats-grid">
                <div className="card stat-card glow-success">
                    <div className="stat-icon income-icon">💰</div>
                    <div className="stat-content">
                        <span className="stat-label">Toplam Gelir</span>
                        <span className="stat-value income-text">
                            {formatCurrency(profitLoss?.total_revenue || 0)}
                        </span>
                        <span className="stat-subtext">Bu ay</span>
                    </div>
                </div>

                <div className="card stat-card glow-danger">
                    <div className="stat-icon expense-icon">💸</div>
                    <div className="stat-content">
                        <span className="stat-label">Toplam Gider</span>
                        <span className="stat-value expense-text">
                            {formatCurrency(profitLoss?.total_expenses || 0)}
                        </span>
                        <span className="stat-subtext">Bu ay</span>
                    </div>
                </div>

                <div className={`card stat-card ${(profitLoss?.net_profit || 0) >= 0 ? "glow-success" : "glow-danger"}`}>
                    <div className={`stat-icon ${(profitLoss?.net_profit || 0) >= 0 ? "income-icon" : "expense-icon"}`}>
                        📈
                    </div>
                    <div className="stat-content">
                        <span className="stat-label">Net Kâr/Zarar</span>
                        <span className={`stat-value ${(profitLoss?.net_profit || 0) >= 0 ? "income-text" : "expense-text"}`}>
                            {formatCurrency(profitLoss?.net_profit || 0)}
                        </span>
                        <span className="stat-subtext">Bu ay</span>
                    </div>
                </div>
            </div>

            {/* Charts Section */}
            <div className="charts-grid fade-in">
                {/* Monthly Revenue Bar Chart */}
                <div className="card chart-card">
                    <h3>📅 Aylık Gelir ({selectedYear})</h3>
                    <div className="bar-chart">
                        {monthlySummary.map((m) => (
                            <div key={m.month} className="bar-item">
                                <div
                                    className="bar"
                                    style={{
                                        height: `${(m.revenue / maxRevenue) * 100}%`,
                                        background: "linear-gradient(to top, #3b82f6, #60a5fa)",
                                    }}
                                    title={`${m.month}: ${formatCurrency(m.revenue)}`}
                                />
                                <span className="bar-label">{m.month.substring(0, 3)}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Expense Category List */}
                <div className="card chart-card">
                    <h3>🍰 Gider Dağılımı (Bu Ay)</h3>
                    {categorySummary.length === 0 ? (
                        <div className="empty-state-small">
                            <p>Henüz gider kaydı yok.</p>
                        </div>
                    ) : (
                        <div className="category-list">
                            {categorySummary.map((cat) => (
                                <div key={cat.category} className="category-item">
                                    <div
                                        className="category-color"
                                        style={{ background: CATEGORY_COLORS[cat.category] || "#6b7280" }}
                                    />
                                    <div style={{ flex: 1 }}>
                                        <span className="category-name">
                                            {CATEGORIES.find((c) => c.value === cat.category)?.label || cat.category}
                                        </span>
                                        <div className="category-bar-bg">
                                            <div
                                                className="category-bar-fill"
                                                style={{
                                                    width: `${(cat.total / (profitLoss?.total_expenses || 1)) * 100}%`,
                                                    background: CATEGORY_COLORS[cat.category] || "#6b7280"
                                                }}
                                            ></div>
                                        </div>
                                    </div>
                                    <span className="category-value">{formatCurrency(cat.total)}</span>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            {/* Link to Expenses Page */}
            <div className="card fade-in delay-1" style={{ marginTop: "2rem", textAlign: "center" }}>
                <h3>💵 Gider Yönetimi</h3>
                <p className="muted" style={{ marginBottom: "1rem" }}>
                    Giderleri detaylı olarak yönetmek için Giderler sayfasına gidin.
                </p>
                <button className="primary" onClick={() => navigate("/expenses")}>
                    Giderler Sayfasına Git →
                </button>
            </div>
        </div>
    );
}
