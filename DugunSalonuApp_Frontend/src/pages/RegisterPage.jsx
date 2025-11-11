import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api/client";

const initialState = {
  name: "",
  email: "",
  username: "",
  password: "",
  phone1: "",
  city: "",
  district: "",
};

export default function RegisterPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState(initialState);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    setSuccess("");
    try {
      await api.register(form);
      setSuccess("Kayıt tamamlandı! Giriş sayfasına yönlendiriliyorsunuz.");
      setTimeout(() => navigate("/login", { replace: true }), 1500);
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="auth-layout">
      <section className="auth-card">
        <h1>Yeni Kullanıcı Oluştur</h1>
        <p className="auth-subtitle">Rezervasyon panelini kullanmak için bir hesap açın.</p>

        <form onSubmit={handleSubmit} className="form">
          <div className="form-grid">
            <label>
              Ad Soyad
              <input name="name" value={form.name} onChange={handleChange} required />
            </label>
            <label>
              E-posta
              <input name="email" type="email" value={form.email} onChange={handleChange} required />
            </label>
            <label>
              Kullanıcı Adı
              <input name="username" value={form.username} onChange={handleChange} required />
            </label>
            <label>
              Şifre
              <input
                name="password"
                type="password"
                value={form.password}
                onChange={handleChange}
                minLength={4}
                required
              />
            </label>
            <label>
              Telefon
              <input name="phone1" value={form.phone1} onChange={handleChange} />
            </label>
            <label>
              İl
              <input name="city" value={form.city} onChange={handleChange} />
            </label>
            <label>
              İlçe
              <input name="district" value={form.district} onChange={handleChange} />
            </label>
          </div>

          {error && <p className="form-error">{error}</p>}
          {success && <p className="form-success">{success}</p>}

          <button type="submit" disabled={submitting}>
            {submitting ? "Kaydediliyor..." : "Kaydı Tamamla"}
          </button>
        </form>

        <p className="auth-footer">
          Zaten hesabınız var mı? <Link to="/login">Giriş yapın</Link>
        </p>
      </section>
    </div>
  );
}
