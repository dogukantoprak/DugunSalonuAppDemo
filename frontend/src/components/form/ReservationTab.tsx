import DateInput from "../DateInput";

const STATUS_OPTIONS = ["Ön Rezervasyon", "Kesin Rezervasyon"];

export default function ReservationTab({
    form,
    handleChange,
    handleDateChange,
    handleTextareaChange,
    availableStarts,
    endOptions,
    loadingSlots,
    slotMessage,
    salonOptions,
    eventTypes,
}) {
    return (
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
                        {eventTypes && eventTypes.map((item) => (
                            <option key={item.id || item} value={item.name || item}>
                                {item.name || item}
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
                        {salonOptions && salonOptions.map((item) => (
                            <option key={item.id || item} value={item.name || item}>
                                {item.name || item}
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
    );
}

export { STATUS_OPTIONS };
