import { useCallback, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import ReservationForm from "../components/ReservationForm";
import ReservationList from "../components/ReservationList";
import { api } from "../api/client";

export default function ReservationsPage({ user, onLogout }) {
  const today = useMemo(() => new Date().toISOString().slice(0, 10), []);
  const [searchParams, setSearchParams] = useSearchParams();
  const queryDate = searchParams.get("date");
  const [selectedDate, setSelectedDate] = useState(() => queryDate || today);
  const [reservations, setReservations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);

  const loadReservations = useCallback(
    async (date) => {
      setLoading(true);
      setError("");
      try {
        const payload = await api.getReservations(date);
        setReservations(payload.items || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    },
    [setReservations],
  );

  useEffect(() => {
    if (queryDate && queryDate !== selectedDate) {
      setSelectedDate(queryDate);
    }
  }, [queryDate, selectedDate]);

  useEffect(() => {
    if (selectedDate && queryDate !== selectedDate) {
      setSearchParams({ date: selectedDate });
    }
  }, [selectedDate, queryDate, setSearchParams]);

  useEffect(() => {
    loadReservations(selectedDate);
  }, [selectedDate, loadReservations]);

  const handleCreate = async (payload) => {
    setSaving(true);
    setError("");
    try {
      await api.createReservation(payload);
      setShowForm(false);
      await loadReservations(selectedDate);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div>
          <p className="muted">Hoş geldiniz</p>
          <h1>{user?.name || user?.username}</h1>
        </div>
        <div className="header-actions">
          <input
            type="date"
            value={selectedDate}
            onChange={(event) => setSelectedDate(event.target.value)}
          />
          <button onClick={() => setShowForm(true)}>Yeni Rezervasyon</button>
          <button className="ghost" onClick={onLogout}>
            Çıkış Yap
          </button>
        </div>
      </header>

      {error && <div className="alert error">{error}</div>}
      {loading ? <div className="loader">Rezervasyonlar yükleniyor...</div> : <ReservationList items={reservations} />}

      {showForm && (
        <ReservationForm
          defaultDate={selectedDate}
          onSubmit={handleCreate}
          onCancel={() => setShowForm(false)}
          submitting={saving}
        />
      )}
    </div>
  );
}
