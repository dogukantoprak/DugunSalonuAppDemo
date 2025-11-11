export default function ReservationList({ items }) {
  if (!items.length) {
    return <div className="empty-state">Seçilen tarihte kayıtlı rezervasyon bulunmuyor.</div>;
  }

  return (
    <div className="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Saat</th>
            <th>Müşteri</th>
            <th>Salon</th>
            <th>Etkinlik</th>
            <th>Durum</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => {
            const statusLabel = item.status || "Belirsiz";
            const statusClass = statusLabel
              .toLowerCase()
              .normalize("NFD")
              .replace(/[\u0300-\u036f]/g, "")
              .replace(/\s+/g, "-");
            return (
              <tr key={item.id}>
                <td>
                  {item.start_time} - {item.end_time}
                </td>
                <td>{item.client_name || "—"}</td>
                <td>{item.salon || "—"}</td>
                <td>{item.event_type || "—"}</td>
                <td>
                  <span className={`status-badge status-${statusClass}`}>{statusLabel}</span>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
