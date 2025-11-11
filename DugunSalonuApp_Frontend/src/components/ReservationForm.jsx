import { useEffect, useState } from "react";

const initialState = (defaultDate) => ({
  event_date: defaultDate,
  start_time: "18:00",
  end_time: "23:00",
  event_type: "Düğün",
  salon: "Salon A",
  client_name: "",
  guests: "",
  phone: "",
  status: "Ön Rezervasyon",
});

export default function ReservationForm({ defaultDate, onSubmit, onCancel, submitting }) {
  const [form, setForm] = useState(initialState(defaultDate));

  useEffect(() => {
    setForm((prev) => ({ ...prev, event_date: defaultDate }));
  }, [defaultDate]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    const payload = {
      ...form,
      guests: form.guests ? Number(form.guests) : null,
    };
    onSubmit(payload);
  };

  return (
    <div className="form-overlay">
      <div className="form-dialog">
        <header>
          <h2>Yeni Rezervasyon</h2>
          <button className="ghost" onClick={onCancel} type="button">
            Kapat
          </button>
        </header>
        <form onSubmit={handleSubmit} className="form-grid">
          <label>
            Tarih
            <input name="event_date" type="date" value={form.event_date} onChange={handleChange} required />
          </label>
          <label>
            Başlangıç Saati
            <input name="start_time" type="time" value={form.start_time} onChange={handleChange} required />
          </label>
          <label>
            Bitiş Saati
            <input name="end_time" type="time" value={form.end_time} onChange={handleChange} required />
          </label>
          <label>
            Salon
            <select name="salon" value={form.salon} onChange={handleChange}>
              <option value="Salon A">Salon A</option>
              <option value="Salon B">Salon B</option>
              <option value="Salon C">Salon C</option>
            </select>
          </label>
          <label>
            Etkinlik Türü
            <select name="event_type" value={form.event_type} onChange={handleChange}>
              <option value="Düğün">Düğün</option>
              <option value="Nişan">Nişan</option>
              <option value="Kına">Kına</option>
              <option value="Toplantı">Toplantı</option>
              <option value="Diğer">Diğer</option>
            </select>
          </label>
          <label>
            Rezervasyon Durumu
            <select name="status" value={form.status} onChange={handleChange}>
              <option value="Ön Rezervasyon">Ön Rezervasyon</option>
              <option value="Kesin Rezervasyon">Kesin Rezervasyon</option>
            </select>
          </label>
          <label>
            Müşteri Adı
            <input name="client_name" value={form.client_name} onChange={handleChange} required />
          </label>
          <label>
            Telefon
            <input name="phone" value={form.phone} onChange={handleChange} />
          </label>
          <label>
            Davetli Sayısı
            <input name="guests" value={form.guests} onChange={handleChange} inputMode="numeric" min="0" />
          </label>

          <div className="form-actions">
            <button className="ghost" type="button" onClick={onCancel}>
              Vazgeç
            </button>
            <button type="submit" disabled={submitting}>
              {submitting ? "Kaydediliyor..." : "Rezervasyonu Kaydet"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
