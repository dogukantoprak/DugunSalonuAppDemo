const PAYMENT_TYPES = ["Nakit", "Kart", "Havale", "Çek"];
const INSTALLMENT_OPTIONS = Array.from({ length: 12 }, (_, idx) => String(idx + 1));

export default function PricingTab({ form, handleChange, handleTextareaChange, handleAddCollection }) {
    return (
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
    );
}

export { PAYMENT_TYPES, INSTALLMENT_OPTIONS };
