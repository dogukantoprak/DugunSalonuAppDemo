import calendar
from datetime import datetime
from tkinter import messagebox

import customtkinter as ctk

from controllers.reservation_controller import get_calendar_data, get_reservations_for_date


class ReservationPage(ctk.CTkFrame):
    def __init__(self, master, on_back=None):
        super().__init__(master)
        self.master = master
        self.on_back = on_back
        self.add_reservation = None

        self.current_date = datetime.now()
        self.selected_date = None
        self.event_data = {}
        self._needs_refresh = True
        self._last_target_date: str | None = None

        self.month_labels = [
            "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
            "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"
        ]
        self.holidays = {(1, 1), (23, 4), (19, 5), (30, 8), (29, 10)}  # Türkiye özel günleri

        title = ctk.CTkLabel(self, text="Rezervasyon Takvimi", font=("Arial", 26, "bold"))
        title.pack(pady=(20, 10))

        control_frame = ctk.CTkFrame(self, fg_color="transparent")
        control_frame.pack(pady=(5, 8))

        ctk.CTkButton(
            control_frame,
            text="◀ Önceki Ay",
            width=110,
            fg_color="#374151",
            hover_color="#4B5563",
            command=self.prev_month
        ).grid(row=0, column=0, padx=8)

        years = [str(y) for y in range(2020, 2031)]
        self.month_var = ctk.StringVar(value=self.month_labels[self.current_date.month - 1])
        self.year_var = ctk.StringVar(value=str(self.current_date.year))

        ctk.CTkComboBox(
            control_frame,
            values=self.month_labels,
            variable=self.month_var,
            width=120,
            command=lambda _: self.manual_date_change()
        ).grid(row=0, column=1, padx=6)
        ctk.CTkComboBox(
            control_frame,
            values=years,
            variable=self.year_var,
            width=80,
            command=lambda _: self.manual_date_change()
        ).grid(row=0, column=2, padx=6)

        ctk.CTkButton(
            control_frame,
            text="Sonraki Ay ▶",
            width=110,
            fg_color="#374151",
            hover_color="#4B5563",
            command=self.next_month
        ).grid(row=0, column=3, padx=8)

        self.calendar_frame = ctk.CTkFrame(self, fg_color="#374151", corner_radius=12)
        self.calendar_frame.pack(padx=60, pady=(10, 12), fill="x")

        bottom_btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_btn_frame.pack(pady=(10, 8))

        self.add_btn = ctk.CTkButton(
            bottom_btn_frame,
            text="Yeni Rezervasyon Ekle",
            width=200,
            height=40,
            fg_color="#F97316",
            hover_color="#EA580C",
            command=self.open_add_reservation
        )
        self.add_btn.grid(row=0, column=0, padx=10, pady=4)

        self.back_btn = ctk.CTkButton(
            bottom_btn_frame,
            text="← Çıkış",
            width=120,
            height=40,
            fg_color="gray20",
            command=self.handle_back
        )
        self.back_btn.grid(row=0, column=1, padx=10, pady=4)

        self.reservation_frame = ctk.CTkFrame(self, corner_radius=10)
        self.reservation_frame.pack(pady=10, padx=40, fill="both", expand=False)

        self.res_label = ctk.CTkLabel(
            self.reservation_frame,
            text="Bir tarih seçiniz.",
            font=("Arial", 15)
        )
        self.res_label.pack(pady=12)

        self.refresh_month_data()
        self.draw_calendar(self.current_date)

    def draw_calendar(self, date):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        header = ctk.CTkLabel(
            self.calendar_frame,
            text=self._format_month_header(date),
            font=("Arial", 20, "bold")
        )
        header.pack(pady=(12, 6))

        cal_frame = ctk.CTkFrame(self.calendar_frame, fg_color="transparent")
        cal_frame.pack(pady=8)

        weekdays = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
        for col, day in enumerate(weekdays):
            ctk.CTkLabel(cal_frame, text=day, width=60, font=("Arial", 12, "bold")).grid(row=0, column=col, pady=4)

        today = datetime.now().date()
        cal = calendar.Calendar()
        month_days = cal.monthdayscalendar(date.year, date.month)
        cell_w, cell_h = 60, 48

        for row_idx, week in enumerate(month_days, start=1):
            for col_idx, day in enumerate(week):
                if day == 0:
                    ctk.CTkLabel(cal_frame, text="", width=cell_w, height=cell_h).grid(row=row_idx, column=col_idx)
                    continue

                current_day = datetime(date.year, date.month, day).date()
                date_str = current_day.isoformat()

                color = "#FFFFFF"
                text_color = "black"

                if current_day == today:
                    color = "#FACC15"
                elif (day, date.month) in self.holidays:
                    color = "#8B5CF6"
                    text_color = "white"
                elif date_str in self.event_data:
                    color = "#F97316"
                    text_color = "white"

                hover_map = {
                    "#FFFFFF": "#E5E7EB",
                    "#F97316": "#EA580C",
                    "#8B5CF6": "#7C3AED",
                    "#FACC15": "#EAB308"
                }
                hover_color = hover_map.get(color, "#E5E7EB")

                text = str(day)
                if date_str in self.event_data:
                    text += f"\n({len(self.event_data[date_str])})"

                ctk.CTkButton(
                    cal_frame,
                    text=text,
                    width=cell_w,
                    height=cell_h,
                    fg_color=color,
                    text_color=text_color,
                    corner_radius=8,
                    hover_color=hover_color,
                    command=lambda d=date_str: self.select_date(d)
                ).grid(row=row_idx, column=col_idx, padx=4, pady=4)

    def select_date(self, date_str):
        self.selected_date = date_str
        self.show_reservations(date_str)

    def show_reservations(self, date_str):
        for widget in self.reservation_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(
            self.reservation_frame,
            text=f"{date_str} Tarihli Organizasyon(lar):",
            font=("Arial", 16, "bold")
        ).pack(pady=(10, 8))

        try:
            events = get_reservations_for_date(date_str)
        except Exception as exc:
            messagebox.showerror("Hata", f"Rezervasyonlar yüklenemedi:\n{exc}")
            ctk.CTkLabel(
                self.reservation_frame,
                text="Rezervasyonlar yüklenirken hata oluştu.",
                font=("Arial", 14),
                text_color="red"
            ).pack(pady=12)
            return

        if not events:
            ctk.CTkLabel(
                self.reservation_frame,
                text="Bu tarihte rezervasyon bulunmuyor.",
                font=("Arial", 14),
                text_color="gray"
            ).pack(pady=12)
            return

        ctk.CTkLabel(
            self.reservation_frame,
            text=f"Toplam: {len(events)} organizasyon",
            font=("Arial", 13)
        ).pack(pady=(0, 8))

        for idx, ev in enumerate(events, start=1):
            card = ctk.CTkFrame(self.reservation_frame, fg_color="#111827", corner_radius=8)
            card.pack(fill="x", padx=12, pady=8)

            title_line = f"{idx}. {ev.get('event_type', '') or '-'} — {ev.get('client_name', '') or '-'}"
            ctk.CTkLabel(card, text=title_line, font=("Arial", 14, "bold")).pack(anchor="w", pady=(8, 4), padx=8)

            time_line = (
                f"Saat: {self._format_time(ev.get('start_time'))} → {self._format_time(ev.get('end_time'))}"
                f"   |   Davetli: {ev.get('guests') or '-'} kişi"
                f"   |   Salon: {ev.get('salon') or '-'}"
            )
            ctk.CTkLabel(card, text=time_line, font=("Arial", 12)).pack(anchor="w", padx=8, pady=(0, 6))

            status_line = f"Durum: {ev.get('status') or '-'}   |   Menü: {ev.get('menu_name') or '-'}"
            ctk.CTkLabel(card, text=status_line, font=("Arial", 12)).pack(anchor="w", padx=8, pady=(0, 4))

            pricing_parts = []
            if ev.get("event_price") is not None:
                pricing_parts.append(f"Etkinlik {self._format_currency(ev['event_price'])}")
            if ev.get("menu_price") is not None:
                pricing_parts.append(f"Menü {self._format_currency(ev['menu_price'])}")
            if ev.get("deposit_amount") is not None:
                pricing_parts.append(f"Kapora {self._format_currency(ev['deposit_amount'])}")
            if ev.get("deposit_percent") is not None:
                pricing_parts.append(self._format_percent(ev["deposit_percent"]))
            if pricing_parts:
                ctk.CTkLabel(card, text=" | ".join(pricing_parts), font=("Arial", 12)).pack(anchor="w", padx=8, pady=(0, 4))

            contact_parts = []
            if ev.get("phone"):
                contact_parts.append(f"Tel: {ev['phone']}")
            if ev.get("tc_identity"):
                contact_parts.append(f"TCKN: {ev['tc_identity']}")
            if contact_parts:
                ctk.CTkLabel(card, text=" | ".join(contact_parts), font=("Arial", 12)).pack(anchor="w", padx=8, pady=(0, 4))

            notes = ev.get("special_request") or ev.get("menu_detail") or ev.get("tahsilatlar")
            if notes:
                ctk.CTkLabel(card, text=f"Notlar: {notes}", font=("Arial", 12), wraplength=760).pack(anchor="w", padx=8, pady=(0, 8))

    def next_month(self):
        year = self.current_date.year + (1 if self.current_date.month == 12 else 0)
        month = 1 if self.current_date.month == 12 else self.current_date.month + 1
        self.current_date = datetime(year, month, 1)
        self.month_var.set(self.month_labels[self.current_date.month - 1])
        self.year_var.set(str(year))
        self.refresh_month_data()
        self.draw_calendar(self.current_date)

    def prev_month(self):
        year = self.current_date.year - (1 if self.current_date.month == 1 else 0)
        month = 12 if self.current_date.month == 1 else self.current_date.month - 1
        self.current_date = datetime(year, month, 1)
        self.month_var.set(self.month_labels[self.current_date.month - 1])
        self.year_var.set(str(year))
        self.refresh_month_data()
        self.draw_calendar(self.current_date)

    def manual_date_change(self):
        months_tr = {name: idx + 1 for idx, name in enumerate(self.month_labels)}
        month = months_tr[self.month_var.get()]
        year = int(self.year_var.get())
        self.current_date = datetime(year, month, 1)
        self.refresh_month_data()
        self.draw_calendar(self.current_date)

    def open_add_reservation(self):
        if self.add_reservation:
            self.add_reservation(self.selected_date)

    def handle_back(self):
        if self.on_back:
            self.on_back()

    def refresh_month_data(self):
        try:
            self.event_data = get_calendar_data(self.current_date.year, self.current_date.month)
        except Exception as exc:
            self.event_data = {}
            messagebox.showerror("Hata", f"Rezervasyon verileri alınamadı:\n{exc}")

    def refresh_data(self, target_date=None):
        self.refresh_month_data()
        self.draw_calendar(self.current_date)
        if target_date:
            self.selected_date = target_date
        if self.selected_date:
            self.show_reservations(self.selected_date)
        self._needs_refresh = False
        self._last_target_date = target_date or self.selected_date

    def mark_dirty(self):
        self._needs_refresh = True

    @property
    def needs_refresh(self):
        return self._needs_refresh

    @staticmethod
    def _format_time(value):
        return value if value else "-"

    @staticmethod
    def _format_currency(value):
        return f"₺{value:.2f}" if value is not None else ""

    @staticmethod
    def _format_percent(value):
        if value is None:
            return ""
        value_float = float(value)
        if abs(value_float - round(value_float)) < 1e-6:
            return f"%{int(round(value_float))} kapora"
        return f"%{value_float:.1f} kapora"

    @staticmethod
    def _format_month_header(target_date):
        return target_date.strftime("%B %Y")
