import { useEffect, useState } from "react";
import { api } from "../api/client";

interface Salon {
    id: number;
    name: string;
    capacity?: number;
    price_factor?: number;
    color?: string;
}

interface Menu {
    id: number;
    name: string;
    content?: string;
    price_per_person?: number;
}

interface EventType {
    id: number;
    name: string;
    default_duration?: number;
}

export default function SettingsPage() {
    const [activeTab, setActiveTab] = useState("salons");
    const [salons, setSalons] = useState<Salon[]>([]);
    const [menus, setMenus] = useState<Menu[]>([]);
    const [eventTypes, setEventTypes] = useState<EventType[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    useEffect(() => {
        fetchSettings();
    }, []);

    const fetchSettings = async () => {
        setLoading(true);
        try {
            const [salonsRes, menusRes, typesRes] = await Promise.all([
                api.getSalons(),
                api.getMenus(),
                api.getEventTypes(),
            ]);
            setSalons(salonsRes);
            setMenus(menusRes);
            setEventTypes(typesRes);
        } catch (err: any) {
            setError(err.message || "Ayarlar yüklenirken hata oluştu.");
        } finally {
            setLoading(false);
        }
    };

    const handleAddSalon = async (e: React.FormEvent) => {
        e.preventDefault();
        const formData = new FormData(e.target as HTMLFormElement);
        try {
            await api.addSalon({
                name: formData.get("name") as string,
                capacity: Number(formData.get("capacity")) || 0,
                price_factor: Number(formData.get("price_factor")) || 1.0,
            });
            fetchSettings();
            (e.target as HTMLFormElement).reset();
        } catch (err: any) {
            alert(err.message);
        }
    };

    const handleAddMenu = async (e: React.FormEvent) => {
        e.preventDefault();
        const formData = new FormData(e.target as HTMLFormElement);
        try {
            await api.addMenu({
                name: formData.get("name") as string,
                content: formData.get("content") as string,
                price_per_person: Number(formData.get("price_per_person")) || 0,
            });
            fetchSettings();
            (e.target as HTMLFormElement).reset();
        } catch (err: any) {
            alert(err.message);
        }
    };

    const handleDelete = async (type: string, id: number) => {
        if (!window.confirm("Silmek istediğinize emin misiniz?")) return;
        try {
            if (type === "salon") await api.deleteSalon(id);
            if (type === "menu") await api.deleteMenu(id);
            fetchSettings();
        } catch (err: any) {
            alert(err.message);
        }
    };

    if (loading && !salons.length) return <div className="loader">Ayarlar yükleniyor...</div>;

    return (
        <div className="dashboard-shell" style={{ marginTop: "2rem" }}>
            <header className="page-header">
                <div>
                    <h1>⚙️ Ayarlar</h1>
                    <p className="muted">Salonları, menüleri ve sistem tanımlarını yönetin.</p>
                </div>
            </header>

            {error && <div className="alert error">{error}</div>}

            <div className="tabs-container">
                <button
                    className={`tab-btn ${activeTab === "salons" ? "active" : ""}`}
                    onClick={() => setActiveTab("salons")}
                >
                    🏰 Salonlar
                </button>
                <button
                    className={`tab-btn ${activeTab === "menus" ? "active" : ""}`}
                    onClick={() => setActiveTab("menus")}
                >
                    🍽️ Menüler
                </button>
                <button
                    className={`tab-btn ${activeTab === "others" ? "active" : ""}`}
                    onClick={() => setActiveTab("others")}
                >
                    🧩 Diğer
                </button>
            </div>

            <div className="tab-content fade-in">
                {activeTab === "salons" && (
                    <div className="settings-section">
                        <div className="grid-container">
                            {salons.map((salon) => (
                                <div key={salon.id} className="card item-card">
                                    <div className="card-header">
                                        <h3>{salon.name}</h3>
                                        <button className="icon-btn danger" onClick={() => handleDelete("salon", salon.id)} title="Sil">
                                            🗑️
                                        </button>
                                    </div>
                                    <div className="card-body">
                                        <p><strong>Kapasite:</strong> {salon.capacity || "-"}</p>
                                        <p><strong>Fiyat Çarpanı:</strong> x{salon.price_factor}</p>
                                    </div>
                                </div>
                            ))}
                            <div className="card add-card">
                                <h3>+ Yeni Salon Ekle</h3>
                                <form onSubmit={handleAddSalon} className="compact-form">
                                    <input name="name" placeholder="Salon Adı" required />
                                    <div className="row">
                                        <input name="capacity" type="number" placeholder="Kapasite" />
                                        <input name="price_factor" type="number" step="0.1" placeholder="Çarpan (1.0)" />
                                    </div>
                                    <button type="submit" className="primary full-width">Ekle</button>
                                </form>
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === "menus" && (
                    <div className="settings-section">
                        <div className="grid-container">
                            {menus.map((menu) => (
                                <div key={menu.id} className="card item-card">
                                    <div className="card-header">
                                        <h3>{menu.name}</h3>
                                        <button className="icon-btn danger" onClick={() => handleDelete("menu", menu.id)} title="Sil">
                                            🗑️
                                        </button>
                                    </div>
                                    <div className="card-body">
                                        <p className="price-tag">{menu.price_per_person} TL <small>/ Kişi</small></p>
                                        <p className="description">{menu.content || "İçerik belirtilmedi."}</p>
                                    </div>
                                </div>
                            ))}
                            <div className="card add-card">
                                <h3>+ Yeni Menü Ekle</h3>
                                <form onSubmit={handleAddMenu} className="compact-form">
                                    <input name="name" placeholder="Menü Adı" required />
                                    <input name="price_per_person" type="number" placeholder="Kişi Başı Fiyat (TL)" />
                                    <textarea name="content" placeholder="Menü içeriği..." rows={3} />
                                    <button type="submit" className="primary full-width">Ekle</button>
                                </form>
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === "others" && (
                    <div className="settings-section empty-state">
                        <span className="emoji">🚧</span>
                        <h3>Yapım Aşamasında</h3>
                        <p>Etkinlik türleri ve diğer genel ayarlar çok yakında burada olacak.</p>
                    </div>
                )}
            </div>
        </div>
    );
}
