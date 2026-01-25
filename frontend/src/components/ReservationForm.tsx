import { useCallback, useEffect, useMemo, useState } from "react";
import { api } from "../api/client";
import { formatDisplayDate, normalizeToIsoDate } from "../api/date";
import { generateContractPDF, exportToExcel } from "../utils";
import {
  ReservationTab,
  PricingTab,
  MenuTab,

  STATUS_OPTIONS,
  PAYMENT_TYPES,
  INSTALLMENT_OPTIONS,
} from "./form";

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
    event_type: initialData?.event_type || "", // Dynamic
    guests: initialData?.guests ?? "",
    salon: initialData?.salon || "", // Dynamic
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
    menu_name: initialData?.menu_name || "", // Dynamic
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

  const [salonOptions, setSalonOptions] = useState<any[]>([]);
  const [eventTypes, setEventTypes] = useState<any[]>([]);
  const [menuOptions, setMenuOptions] = useState<any[]>([]);

  useEffect(() => {
    Promise.all([api.getSalons(), api.getEventTypes(), api.getMenus()])
      .then(([salons, types, menus]) => {
        setSalonOptions(salons);
        setEventTypes(types);
        setMenuOptions(menus);

        // Update default selection if loaded and not editing
        if (!isEditing && !form.salon && salons.length > 0) {
          setForm((prev) => ({ ...prev, salon: salons[0].name }));
        }
        if (!isEditing && !form.event_type && types.length > 0) {
          setForm((prev) => ({ ...prev, event_type: types[0].name }));
        }
        if (!isEditing && !form.menu_name && menus.length > 0) {
          setForm((prev) => ({ ...prev, menu_name: menus[0].name }));
        }
      })
      .catch(console.error);
  }, [isEditing]);

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
      id: isEditing && initialData?.id !== undefined ? initialData.id : undefined,
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
            <ReservationTab
              form={form}
              handleChange={handleChange}
              handleDateChange={handleDateChange}
              handleTextareaChange={handleTextareaChange}
              availableStarts={availableStarts}
              endOptions={endOptions}
              loadingSlots={loadingSlots}
              slotMessage={slotMessage}
              salonOptions={salonOptions}
              eventTypes={eventTypes}
            />
          )}

          {activeTab === "pricing" && (
            <PricingTab
              form={form}
              handleChange={handleChange}
              handleTextareaChange={handleTextareaChange}
              handleAddCollection={handleAddCollection}
            />
          )}

          {activeTab === "menu" && (
            <MenuTab
              form={form}
              handleChange={handleChange}
              handleTextareaChange={handleTextareaChange}
              menuOptions={menuOptions}
            />
          )}

          <div className="form-footer">
            <div className="footer-actions">
              <button
                type="button"
                className="ghost"
                onClick={() => {
                  const reservation = {
                    ...form,
                    id: initialData?.id,
                    guests: toNumber(form.guests),
                    event_price: toNumber(form.event_price),
                    menu_price: toNumber(form.menu_price),
                    deposit_percent: toNumber(form.deposit_percent),
                    deposit_amount: toNumber(form.deposit_amount),
                    installments: form.installments ? Number(form.installments) : undefined,
                  };
                  generateContractPDF(reservation);
                }}
              >
                🖨️ Sözleşme Yazdır
              </button>
              <button
                type="button"
                className="ghost"
                onClick={() => {
                  const reservation = {
                    ...form,
                    id: initialData?.id,
                    guests: toNumber(form.guests),
                    event_price: toNumber(form.event_price),
                    menu_price: toNumber(form.menu_price),
                    deposit_percent: toNumber(form.deposit_percent),
                    deposit_amount: toNumber(form.deposit_amount),
                    installments: form.installments ? Number(form.installments) : undefined,
                  };
                  exportToExcel([reservation], `rezervasyon_${form.client_name?.replace(/\s+/g, "_") || "detay"}`);
                }}
              >
                📊 Excel'e Aktar
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
