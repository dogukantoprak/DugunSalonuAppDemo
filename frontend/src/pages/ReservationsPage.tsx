import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import DateInput from "../components/DateInput";
import ReservationForm from "../components/ReservationForm";
import ReservationList from "../components/ReservationList";
import { api } from "../api/client";
import { isIsoDate, normalizeToIsoDate } from "../api/date";

export default function ReservationsPage({ user, onLogout }) {
  const today = useMemo(() => new Date().toISOString().slice(0, 10), []);
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const queryDate = searchParams.get("date");
  const normalizedQuery = normalizeToIsoDate(queryDate);
  const selectedDate = isIsoDate(normalizedQuery) ? normalizedQuery : today;
  const [reservations, setReservations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editingReservation, setEditingReservation] = useState(null);

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

  const handleSave = async (payload) => {
    if (editingReservation) {
      setSaving(true);
      setError("");
      try {
        const updated = { ...editingReservation, ...payload };
        setReservations((prev) => prev.map((item) => (item.id === editingReservation.id ? updated : item)));
        setEditingReservation(null);
        setShowForm(false);
      } catch (err) {
        setError(err.message);
      } finally {
        setSaving(false);
      }
      return;
    }
    await handleCreate(payload);
  };

  const handleDeleteReservation = useCallback((reservation) => {
    if (!reservation?.id) {
      return;
    }
    const confirmed = window.confirm("Bu rezervasyonu silmek istediğinize emin misiniz?");
    if (!confirmed) {
      return;
    }
    setReservations((prev) => prev.filter((item) => item.id !== reservation.id));
  }, []);

  const handleEditReservation = useCallback((reservation) => {
    setEditingReservation(reservation);
    setShowForm(true);
  }, []);

  const handleCancelForm = useCallback(() => {
    setEditingReservation(null);
    setShowForm(false);
  }, []);

  const handleOpenCreate = useCallback(() => {
    setEditingReservation(null);
    setShowForm(true);
  }, []);

  const handleGoBack = useCallback(() => {
    navigate("/");
  }, [navigate]);

  const handleDateChange = useCallback(
    (nextDate) => {
      const normalized = normalizeToIsoDate(nextDate);
      if (isIsoDate(normalized)) {
        setSearchParams({ date: normalized });
      }
    },
    [setSearchParams],
  );

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div>
          <p className="muted">Hoş geldiniz</p>
          <h1>{user?.name || user?.username}</h1>
        </div>
        <div className="header-actions">
          <DateInput value={selectedDate} onChange={handleDateChange} />
          <button onClick={handleOpenCreate}>Yeni Rezervasyon</button>
          <button className="ghost" onClick={handleGoBack}>
            Geri
          </button>
        </div>
      </header>

      {error && <div className="alert error">{error}</div>}
      {loading ? (
        <div className="loader">Rezervasyonlar yükleniyor...</div>
      ) : (
        <ReservationList items={reservations} onEdit={handleEditReservation} onDelete={handleDeleteReservation} />
      )}

      {showForm && (
        <ReservationForm
          defaultDate={selectedDate}
          onSubmit={handleSave}
          onCancel={handleCancelForm}
          submitting={saving}
          initialData={editingReservation}
        />
      )}
    </div>
  );
}
