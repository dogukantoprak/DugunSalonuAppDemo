import { useEffect, useMemo, useState } from "react";
import { api } from "../api/client";

const EVENT_TYPES = ["Düğün", "Nişan", "Kına", "Toplantı", "Mezuniyet", "Diğer"];
const SALON_OPTIONS = ["Salon A", "Salon B", "Salon C"];
const STATUS_OPTIONS = ["Ön Rezervasyon", "Kesin Rezervasyon"];
const PAYMENT_TYPES = ["Nakit", "Kart", "Havale", "Çek"];
const MENU_OPTIONS = ["Klasik Menü", "Lüks Menü", "Özel Menü"];
const INSTALLMENT_OPTIONS = Array.from({ length: 12 }, (_, idx) => String(idx + 1));
const TIME_STEP_MINUTES = 15;
const START_SLOTS = buildTimeSlots({ startHour: 10, endHour: 24, includeEnd: false });
const END_SLOTS = buildTimeSlots({ startHour: 10, endHour: 24, includeEnd: true, startOffset: TIME_STEP_MINUTES });

const initialState = (defaultDate) => {
  const today = defaultDate || new Date().toISOString().slice(0, 10);
  return {
    event_date: today,
    contract_date: today,
    start_time: "",
    end_time: END_SLOTS[0],
    event_type: EVENT_TYPES[0],
    guests: "",
    salon: SALON_OPTIONS[0],
    client_name: "",
    tc_identity: "",
    phone: "",
    address: "",
    contract_no: "",
    status: STATUS_OPTIONS[0],
    event_price: "",
    menu_price: "",
    deposit_percent: "",
    deposit_amount: "",
    installments: INSTALLMENT_OPTIONS[0],
    payment_type: PAYMENT_TYPES[0],
    tahsilatlar: "",
    menu_name: MENU_OPTIONS[0],
    menu_detail: "",
    special_request: "",
  };
};

export default function ReservationForm({ defaultDate, onSubmit, onCancel, submitting }) {
  const [form, setForm] = useState(() => initialState(defaultDate));
  const [activeTab, setActiveTab] = useState("reservation");
  const [slotMessage, setSlotMessage] = useState(
    "Salon ve tarih seçimi yaptıktan sonra uygun 15 dakikalık saatleri görebilirsiniz.",
  );
  const [availableStarts, setAvailableStarts] = useState(START_SLOTS);
  const [loadingSlots, setLoadingSlots] = useState(false);

  useEffect(() => {
    setForm((prev) => ({
      ...prev,
      event_date: defaultDate || prev.event_date,
      contract_date: defaultDate || prev.contract_date,
    }));
  }, [defaultDate]);

  useEffect(() => {
    let ignore = false;
    const { event_date: eventDate, salon } = form;

    if (!eventDate || !salon) {
      setAvailableStarts(START_SLOTS);
      setSlotMessage("Salon ve tarih seçimi yaptıktan sonra uygun 15 dakikalık saatleri görebilirsiniz.");
      setForm((prev) => {
        if (!prev.start_time || !START_SLOTS.includes(prev.start_time)) {
          return { ...prev, start_time: START_SLOTS[0] };
        }
        return prev;
      });
      return () => {
        ignore = true;
      };
    }

    setLoadingSlots(true);
    api
      .getUnavailableSlots(eventDate, salon)
      .then((data) => {
        if (ignore) {
          return;
        }
        const blocked = data?.blocked || [];
        const busyRanges = data?.ranges || [];
        const nextSlots = START_SLOTS.filter((slot) => !blocked.includes(slot));
        setAvailableStarts(nextSlots.length ? nextSlots : []);
        if (!nextSlots.length) {
          setSlotMessage(`${salon} salonunda seçilen tarih için uygun saat bulunmuyor.`);
        } else if (busyRanges.length) {
          setSlotMessage(`Dolu saat aralıkları: ${busyRanges.join(", ")}`);
        } else {
          setSlotMessage("");
        }
      })
      .catch((err) => {
        if (!ignore) {
          setAvailableStarts(START_SLOTS);
          setSlotMessage(err.message || "Uygun saatler alınamadı.");
        }
      })
      .finally(() => {
        if (!ignore) {
          setLoadingSlots(false);
        }
      });

    return () => {
      ignore = true;
    };
  }, [form.event_date, form.salon]);

  useEffect(() => {
    if (!availableStarts.length) {
      if (form.start_time) {
        setForm((prev) => ({ ...prev, start_time: "" }));
      }
      return;
    }
    if (!form.start_time || !availableStarts.includes(form.start_time)) {
      setForm((prev) => ({ ...prev, start_time: availableStarts[0] }));
    }
  }, [availableStarts, form.start_time]);

  const endOptions = useMemo(() => {
    if (!form.start_time) {
      return END_SLOTS;
    }
    const startMinutes = toMinutes(form.start_time);
    const filtered = END_SLOTS.filter((slot) => toMinutes(slot) > startMinutes);
    return filtered.length ? filtered : END_SLOTS;
  }, [form.start_time]);

  useEffect(() => {
    if (!form.end_time || !endOptions.includes(form.end_time)) {
      setForm((prev) => ({ ...prev, end_time: endOptions[0] }));
    }
  }, [endOptions, form.end_time]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleTextareaChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleAddCollection = () => {
    const stamp = new Date().toLocaleDateString("tr-TR");
    setForm((prev) => ({
      ...prev,
      tahsilatlar: `${prev.tahsilatlar}${prev.tahsilatlar ? "\n" : ""}${stamp} - `,
    }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    const payload = {
      ...form,
      guests: toNumber(form.guests),
      event_price: toNumber(form.event_price),
      menu_price: toNumber(form.menu_price),
      deposit_percent: toNumber(form.deposit_percent),
      deposit_amount: toNumber(form.deposit_amount),
      installments: form.installments ? Number(form.installments) : undefined,
    };
    onSubmit(payload);
  };

  return (
    <div className="form-overlay">
      <div className="form-dialog large">
        <header>
          <div>
            <p className="muted">📝 Yeni Rezervasyon Ekle</p>
            <h2>Operasyon detaylarını doldurun</h2>
          </div>
          <button className="ghost" onClick={onCancel} type="button">
            Kapat
          </button>
        </header>

        <div className="form-tabs">
          <button
            type="button"
            className={activeTab === "reservation" ? "active" : ""}
            onClick={() => setActiveTab("reservation")}
          >
            Rezervasyon Bilgileri
          </button>
          <button type="button" className={activeTab === "pricing" ? "active" : ""} onClick={() => setActiveTab("pricing")}>
            Fiyat Bilgileri
          </button>
          <button type="button" className={activeTab === "menu" ? "active" : ""} onClick={() => setActiveTab("menu")}>
            Menü Bilgileri
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          {activeTab === "reservation" && (
            <div className="form-section">
              <div className="section-grid">
                <label>
                  Tarih
                  <input name="event_date" type="date" value={form.event_date} onChange={handleChange} required />
                </label>
                <label>
                  Başlangıç Saati
                  <select
                    name="start_time"
                    value={form.start_time}
                    onChange={handleChange}
                    disabled={!availableStarts.length}
                  >
                    {availableStarts.length ? (
                      availableStarts.map((slot) => (
                        <option key={slot} value={slot}>
                          {slot}
                        </option>
                      ))
                    ) : (
                      <option value="">Uygun saat yok</option>
                    )}
                  </select>
                </label>
                <label>
                  Bitiş Saati
                  <select name="end_time" value={form.end_time} onChange={handleChange}>
                    {endOptions.map((slot) => (
                      <option key={slot} value={slot}>
                        {slot}
                      </option>
                    ))}
                  </select>
                </label>
                <div className="slot-hint">
                  {loadingSlots ? "Saatler hesaplanıyor..." : slotMessage || "Uygun saat seçebilirsiniz."}
                </div>
                <label>
                  Etkinlik Türü
                  <select name="event_type" value={form.event_type} onChange={handleChange}>
                    {EVENT_TYPES.map((item) => (
                      <option key={item} value={item}>
                        {item}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Davetli Sayısı
                  <input name="guests" value={form.guests} onChange={handleChange} inputMode="numeric" min="0" />
                </label>
                <label>
                  Salon
                  <select name="salon" value={form.salon} onChange={handleChange}>
                    {SALON_OPTIONS.map((item) => (
                      <option key={item} value={item}>
                        {item}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Rezervasyon Durumu
                  <select name="status" value={form.status} onChange={handleChange}>
                    {STATUS_OPTIONS.map((item) => (
                      <option key={item} value={item}>
                        {item}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Ad Soyad
                  <input name="client_name" value={form.client_name} onChange={handleChange} required />
                </label>
                <label>
                  TC Kimlik
                  <input name="tc_identity" value={form.tc_identity} onChange={handleChange} />
                </label>
                <label>
                  Telefon
                  <input name="phone" value={form.phone} onChange={handleChange} />
                </label>
                <label>
                  Sözleşme No
                  <input name="contract_no" value={form.contract_no} onChange={handleChange} />
                </label>
                <label>
                  Sözleşme Tarihi
                  <input name="contract_date" type="date" value={form.contract_date} onChange={handleChange} />
                </label>
              </div>

              <label className="full-width">
                Adres
                <textarea name="address" value={form.address} onChange={handleTextareaChange} rows={3} />
              </label>
            </div>
          )}

          {activeTab === "pricing" && (
            <div className="form-section">
              <div className="section-grid">
                <label>
                  Kişi Başı Etkinlik Ücreti
                  <input
                    name="event_price"
                    value={form.event_price}
                    onChange={handleChange}
                    inputMode="decimal"
                    type="number"
                    step="0.01"
                    min="0"
                  />
                </label>
                <label>
                  Kişi Başı Menü Ücreti
                  <input
                    name="menu_price"
                    value={form.menu_price}
                    onChange={handleChange}
                    inputMode="decimal"
                    type="number"
                    step="0.01"
                    min="0"
                  />
                </label>
                <label>
                  Kapora Yüzdesi
                  <input
                    name="deposit_percent"
                    value={form.deposit_percent}
                    onChange={handleChange}
                    inputMode="decimal"
                    type="number"
                    step="0.01"
                    min="0"
                    max="100"
                  />
                </label>
                <label>
                  Kapora Tutarı
                  <input
                    name="deposit_amount"
                    value={form.deposit_amount}
                    onChange={handleChange}
                    inputMode="decimal"
                    type="number"
                    step="0.01"
                    min="0"
                  />
                </label>
                <label>
                  Taksit Sayısı
                  <select name="installments" value={form.installments} onChange={handleChange}>
                    {INSTALLMENT_OPTIONS.map((item) => (
                      <option key={item} value={item}>
                        {item}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Ödeme Türü
                  <select name="payment_type" value={form.payment_type} onChange={handleChange}>
                    {PAYMENT_TYPES.map((item) => (
                      <option key={item} value={item}>
                        {item}
                      </option>
                    ))}
                  </select>
                </label>
              </div>

              <label className="full-width">
                Tahsilatlar
                <textarea name="tahsilatlar" value={form.tahsilatlar} onChange={handleTextareaChange} rows={4} />
              </label>
              <div className="form-actions left">
                <button type="button" onClick={handleAddCollection}>
                  + Tahsilat Ekle
                </button>
              </div>
            </div>
          )}

          {activeTab === "menu" && (
            <div className="form-section">
              <div className="section-grid two-cols">
                <label>
                  Menü Seçimi
                  <select name="menu_name" value={form.menu_name} onChange={handleChange}>
                    {MENU_OPTIONS.map((item) => (
                      <option key={item} value={item}>
                        {item}
                      </option>
                    ))}
                  </select>
                </label>
              </div>

              <label className="full-width">
                Menü Detayı
                <textarea name="menu_detail" value={form.menu_detail} onChange={handleTextareaChange} rows={4} />
              </label>
              <label className="full-width">
                Özel İstekler
                <textarea name="special_request" value={form.special_request} onChange={handleTextareaChange} rows={4} />
              </label>
            </div>
          )}

          <div className="form-footer">
            <div className="footer-actions">
              <button type="button" className="ghost" disabled>
                🖨️ Sözleşme Yazdır (yakında)
              </button>
              <button type="button" className="ghost" disabled>
                📊 Excel’e Aktar (yakında)
              </button>
            </div>
            <div className="footer-actions">
              <button className="ghost" type="button" onClick={onCancel}>
                Vazgeç
              </button>
              <button type="submit" disabled={submitting}>
                {submitting ? "Kaydediliyor..." : "Rezervasyonu Kaydet"}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}

function buildTimeSlots({ startHour, endHour, includeEnd, startOffset = 0 }) {
  const slots = [];
  const startMinutes = startHour * 60 + startOffset;
  const endMinutes = endHour * 60;
  for (let minutes = startMinutes; minutes < endMinutes; minutes += TIME_STEP_MINUTES) {
    slots.push(formatMinutes(minutes));
  }
  if (includeEnd) {
    slots.push(formatMinutes(endMinutes));
  }
  return slots;
}

function formatMinutes(totalMinutes) {
  const hours = Math.floor(totalMinutes / 60)
    .toString()
    .padStart(2, "0");
  const minutes = (totalMinutes % 60).toString().padStart(2, "0");
  return `${hours}:${minutes}`;
}

function toMinutes(value) {
  if (!value || !value.includes(":")) {
    return 0;
  }
  const [hour, minute] = value.split(":").map(Number);
  return hour * 60 + minute;
}

function toNumber(value) {
  if (value === undefined || value === null || value === "") {
    return undefined;
  }
  const normalized = String(value).replace(",", ".");
  const parsed = Number(normalized);
  return Number.isNaN(parsed) ? undefined : parsed;
}
