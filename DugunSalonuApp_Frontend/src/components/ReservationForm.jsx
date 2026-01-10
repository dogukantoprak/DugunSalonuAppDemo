import { useCallback, useEffect, useMemo, useState } from "react";
import DateInput from "./DateInput";
import { api } from "../api/client";
import { formatDisplayDate, normalizeToIsoDate } from "../api/date";

const EVENT_TYPES = ["Düğün", "Nişan", "Kına", "Toplantı", "Mezuniyet", "Diğer"];
const SALON_OPTIONS = ["Salon A", "Salon B", "Salon C"];
const STATUS_OPTIONS = ["Ön Rezervasyon", "Kesin Rezervasyon"];
const PAYMENT_TYPES = ["Nakit", "Kart", "Havale", "Çek"];
const MENU_OPTIONS = ["Klasik Menü", "Lüks Menü", "Özel Menü"];
const INSTALLMENT_OPTIONS = Array.from({ length: 12 }, (_, idx) => String(idx + 1));
const TIME_STEP_MINUTES = 15;
const START_SLOTS = buildTimeSlots({ startHour: 10, endHour: 24, includeEnd: false });
const END_SLOTS = buildTimeSlots({ startHour: 10, endHour: 24, includeEnd: true, startOffset: TIME_STEP_MINUTES });

const initialState = (defaultDate, initialData) => {
  const today = normalizeToIsoDate(defaultDate) || new Date().toISOString().slice(0, 10);
  return {
    event_date: normalizeToIsoDate(initialData?.event_date) || today,
    contract_date: normalizeToIsoDate(initialData?.contract_date || initialData?.event_date) || today,
    start_time: initialData?.start_time || "",
    end_time: initialData?.end_time || END_SLOTS[0],
    event_type: initialData?.event_type || EVENT_TYPES[0],
    guests: initialData?.guests ?? "",
    salon: initialData?.salon || SALON_OPTIONS[0],
    client_name: initialData?.client_name || "",
    bride_name: initialData?.bride_name || "",
    groom_name: initialData?.groom_name || "",
    tc_identity: initialData?.tc_identity || "",
    phone: initialData?.phone || "",
    address: initialData?.address || "",
    contract_no: initialData?.contract_no || "",
    status: initialData?.status || STATUS_OPTIONS[0],
    event_price: initialData?.event_price ?? "",
    menu_price: initialData?.menu_price ?? "",
    deposit_percent: initialData?.deposit_percent ?? "",
    deposit_amount: initialData?.deposit_amount ?? "",
    installments: initialData?.installments ? String(initialData.installments) : INSTALLMENT_OPTIONS[0],
    payment_type: initialData?.payment_type || PAYMENT_TYPES[0],
    tahsilatlar: initialData?.tahsilatlar || "",
    menu_name: initialData?.menu_name || MENU_OPTIONS[0],
    menu_detail: initialData?.menu_detail || "",
    special_request: initialData?.special_request || "",
    note: initialData?.note || "",
    region: initialData?.region || "",
  };
};

export default function ReservationForm({ defaultDate, onSubmit, onCancel, submitting, initialData }) {
  const [form, setForm] = useState(() => initialState(defaultDate, initialData));
  const isEditing = Boolean(initialData?.id);
  const [activeTab, setActiveTab] = useState("reservation");
  const [slotMessage, setSlotMessage] = useState(
    "Salon ve tarih seçimi yaptıktan sonra uygun 15 dakikalık saatleri görebilirsiniz.",
  );
  const [availableStarts, setAvailableStarts] = useState(START_SLOTS);
  const [loadingSlots, setLoadingSlots] = useState(false);

  useEffect(() => {
    const nextForm = initialState(defaultDate, initialData);
    setForm(nextForm);
    setActiveTab("reservation");
  }, [defaultDate, initialData]);

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
      if (form.start_time && !isEditing) {
        setForm((prev) => ({ ...prev, start_time: "" }));
      }
      return;
    }
    if (!form.start_time || (!availableStarts.includes(form.start_time) && !isEditing)) {
      setForm((prev) => ({ ...prev, start_time: availableStarts[0] }));
    }
  }, [availableStarts, form.start_time, isEditing]);

  const endOptions = useMemo(() => {
    if (!form.start_time) {
      return END_SLOTS;
    }
    const startMinutes = toMinutes(form.start_time);
    const filtered = END_SLOTS.filter((slot) => toMinutes(slot) > startMinutes);
    return filtered.length ? filtered : END_SLOTS;
  }, [form.start_time]);

  useEffect(() => {
    if (!form.end_time || (!endOptions.includes(form.end_time) && !isEditing)) {
      setForm((prev) => ({ ...prev, end_time: endOptions[0] }));
    }
  }, [endOptions, form.end_time, isEditing]);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleDateChange = useCallback((name, nextValue) => {
    setForm((prev) => ({ ...prev, [name]: normalizeToIsoDate(nextValue) || nextValue }));
  }, []);

  const handleTextareaChange = (event) => {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleAddCollection = () => {
    const stamp = formatDisplayDate(new Date());
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
    if (isEditing && initialData?.id !== undefined) {
      payload.id = initialData.id;
    }
    onSubmit(payload);
  };

  return (
    <div className="form-overlay">
      <div className="form-dialog large">
        <header>
          <div>
            <p className="muted">{isEditing ? "📝 Rezervasyonu Düzenle" : "📝 Yeni Rezervasyon Ekle"}</p>
            <h2>{isEditing ? "Bilgileri güncelleyin" : "Operasyon detaylarını doldurun"}</h2>
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
                  <DateInput
                    name="event_date"
                    value={form.event_date}
                    onChange={(value) => handleDateChange("event_date", value)}
                    required
                  />
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
                  Gelin
                  <input name="bride_name" value={form.bride_name} onChange={handleChange} />
                </label>
                <label>
                  Damat
                  <input name="groom_name" value={form.groom_name} onChange={handleChange} />
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
                  Memleket / Yöre
                  <input name="region" value={form.region || ""} onChange={handleChange} />
                </label>
                <label>
                  Sözleşme No
                  <input name="contract_no" value={form.contract_no} onChange={handleChange} />
                </label>
                <label>
                  Sözleşme Tarihi
                  <DateInput
                    name="contract_date"
                    value={form.contract_date}
                    onChange={(value) => handleDateChange("contract_date", value)}
                    allowEmpty
                  />
                </label>
              </div>

              <div className="full-width address-notes">
                <label className="address-field">
                  Adres
                  <textarea name="address" value={form.address} onChange={handleTextareaChange} rows={3} />
                </label>
                <label className="note-field">
                  Not
                  <textarea name="note" value={form.note || ""} onChange={handleTextareaChange} rows={3} />
                </label>
              </div>
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
                {submitting ? "Kaydediliyor..." : isEditing ? "Rezervasyonu Güncelle" : "Rezervasyonu Kaydet"}
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
