

export default function MenuTab({ form, handleChange, handleTextareaChange, menuOptions }) {
    return (
        <div className="form-section">
            <div className="section-grid two-cols">
                <label>
                    Menü Seçimi
                    <select name="menu_name" value={form.menu_name} onChange={handleChange}>
                        {menuOptions && menuOptions.map((item) => (
                            <option key={item.id || item} value={item.name || item}>
                                {item.name || item}
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
    );
}


