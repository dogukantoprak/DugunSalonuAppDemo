import { useMemo } from "react";

interface StatsCardsProps {
    calendarData: Record<string, Record<string, unknown[]>>;
    loading: boolean;
}

interface StatCardProps {
    icon: string;
    label: string;
    value: string | number;
    subtext?: string;
    color: string;
}

function StatCard({ icon, label, value, subtext, color }: StatCardProps) {
    return (
        <div className="stat-card" style={{ borderColor: color }}>
            <div className="stat-icon" style={{ background: color }}>
                {icon}
            </div>
            <div className="stat-content">
                <span className="stat-label">{label}</span>
                <span className="stat-value">{value}</span>
                {subtext && <span className="stat-subtext">{subtext}</span>}
            </div>
        </div>
    );
}

export default function StatsCards({ calendarData, loading }: StatsCardsProps) {
    const stats = useMemo(() => {
        if (loading || !calendarData) {
            return { thisMonth: 0, nextMonth: 0, total: 0, upcoming: 0 };
        }

        const today = new Date();
        const todayIso = today.toISOString().slice(0, 10);
        let thisMonth = 0;
        let nextMonth = 0;
        let total = 0;
        let upcoming = 0;

        Object.entries(calendarData).forEach(([monthKey, dayData]) => {
            const [year, month] = monthKey.split("-").map(Number);
            const isThisMonth = year === today.getFullYear() && month === today.getMonth() + 1;
            const isNextMonth =
                (year === today.getFullYear() && month === today.getMonth() + 2) ||
                (today.getMonth() === 11 && year === today.getFullYear() + 1 && month === 1);

            Object.entries(dayData).forEach(([dateKey, events]) => {
                const count = Array.isArray(events) ? events.length : 0;
                total += count;

                if (isThisMonth) {
                    thisMonth += count;
                }
                if (isNextMonth) {
                    nextMonth += count;
                }

                // Upcoming = today or future
                if (dateKey >= todayIso) {
                    upcoming += count;
                }
            });
        });

        return { thisMonth, nextMonth, total, upcoming };
    }, [calendarData, loading]);

    const monthNames = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"];
    const today = new Date();
    const thisMonthName = monthNames[today.getMonth()];
    const nextMonthName = monthNames[(today.getMonth() + 1) % 12];

    return (
        <div className="stats-grid">
            <StatCard
                icon="📅"
                label="Yaklaşan Etkinlikler"
                value={loading ? "..." : stats.upcoming}
                subtext="Bugün ve sonrası"
                color="rgba(59, 130, 246, 0.8)"
            />
            <StatCard
                icon="🎉"
                label={`${thisMonthName} Etkinlikleri`}
                value={loading ? "..." : stats.thisMonth}
                subtext="Bu ay toplam"
                color="rgba(16, 185, 129, 0.8)"
            />
            <StatCard
                icon="📆"
                label={`${nextMonthName} Etkinlikleri`}
                value={loading ? "..." : stats.nextMonth}
                subtext="Gelecek ay"
                color="rgba(245, 158, 11, 0.8)"
            />
            <StatCard
                icon="📊"
                label="3 Aylık Toplam"
                value={loading ? "..." : stats.total}
                subtext="Tüm etkinlikler"
                color="rgba(139, 92, 246, 0.8)"
            />
        </div>
    );
}
