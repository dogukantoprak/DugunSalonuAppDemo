import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api/client";

export default function LoginPage({ onLogin }) {
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", password: "" });
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      const payload = await api.login(form);
      onLogin?.(payload.user);
      navigate("/", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="auth-layout">
      <section className="auth-card">
        <h1>Düğün Salonu Yönetimi</h1>
        <p className="auth-subtitle">Rezervasyon panosuna erişmek için giriş yapın.</p>

        <form onSubmit={handleSubmit} className="form">
          <label>
            Kullanıcı Adı
            <input
              type="text"
              name="username"
              value={form.username}
              onChange={handleChange}
              placeholder="örn. admin"
              required
            />
          </label>
          <label>
            Şifre
            <input
              type="password"
              name="password"
              value={form.password}
              onChange={handleChange}
              placeholder="******"
              required
            />
          </label>

          {error && <p className="form-error">{error}</p>}

          <button type="submit" disabled={submitting}>
            {submitting ? "Giriş yapılıyor..." : "Giriş Yap"}
          </button>
        </form>

        <p className="auth-footer">
          Hesabınız yok mu? <Link to="/register">Hemen kayıt olun</Link>
        </p>
      </section>
    </div>
  );
}
