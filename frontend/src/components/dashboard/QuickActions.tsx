import { useNavigate } from "react-router-dom";

export default function QuickActions() {
    const navigate = useNavigate();
    const today = new Date().toISOString().slice(0, 10);

    const actions = [
        {
            icon: "➕",
            label: "Yeni Rezervasyon",
            action: () => navigate(`/reservations?date=${today}&new=true`),
            primary: true,
        },
        {
            icon: "📋",
            label: "Bugünün Etkinlikleri",
            action: () => navigate(`/reservations?date=${today}`),
            primary: false,
        },
        {
            icon: "🔍",
            label: "Rezervasyon Ara",
            action: () => alert("Arama özelliği yakında eklenecek!"),
            primary: false,
        },
    ];

    return (
        <div className="quick-actions">
            <h3>Hızlı İşlemler</h3>
            <div className="quick-actions-grid">
                {actions.map((item) => (
                    <button
                        key={item.label}
                        type="button"
                        className={`quick-action-btn ${item.primary ? "primary" : ""}`}
                        onClick={item.action}
                    >
                        <span className="quick-action-icon">{item.icon}</span>
                        <span>{item.label}</span>
                    </button>
                ))}
            </div>
        </div>
    );
}
