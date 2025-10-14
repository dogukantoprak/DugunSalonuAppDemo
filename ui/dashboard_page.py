import customtkinter as ctk
from datetime import datetime
import calendar
from tkinter import messagebox

from controllers.reservation_controller import get_calendar_data

class DashboardPage(ctk.CTkFrame):
    def __init__(self, master, user=None, on_logout=None, on_open_reservations=None,
                 on_open_personnel=None, on_open_reports=None, on_open_settings=None):
        super().__init__(master)
        self.master = master
        self.user = user or {}
        self._month_cache = {}
        self._auto_refresh_ms = 10 * 60 * 1000  # 10 minutes
        self._auto_refresh_job = None
        self._calendar_dirty = True
        self._last_rendered_months = []
        self._last_rendered_today = None
        self._last_refresh_time = None
        self._is_visible = False

        # Callback fonksiyonlar
        self.on_logout = on_logout
        self.on_open_reservations = on_open_reservations
        self.on_open_personnel = on_open_personnel
        self.on_open_reports = on_open_reports
        self.on_open_settings = on_open_settings

        # Sayfa düzeni
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Üst Menü Bar
        self.top_bar = ctk.CTkFrame(self, height=50, fg_color="#1F2937")
        self.top_bar.grid(row=0, column=0, sticky="ew")
        self.top_bar.grid_columnconfigure((0,1,2,3,4), weight=1)

        ctk.CTkButton(self.top_bar, text="Rezervasyonlar", command=self.handle_reservations, width=140).grid(row=0, column=0, padx=10, pady=10)
        ctk.CTkButton(self.top_bar, text="Personel", command=self.handle_personnel, width=100).grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkButton(self.top_bar, text="Raporlar", command=self.handle_reports, width=100).grid(row=0, column=2, padx=10, pady=10)
        ctk.CTkButton(self.top_bar, text="Ayarlar", command=self.handle_settings, width=100).grid(row=0, column=3, padx=10, pady=10)
        ctk.CTkButton(self.top_bar, text="Çıkış Yap", fg_color="#B91C1C", hover_color="#DC2626",
                      command=self.handle_logout, width=100).grid(row=0, column=4, padx=10, pady=10)

        # Orta Alan
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=40)
        self.content_frame.grid_columnconfigure(0, weight=1)

        welcome_text = self._build_welcome_text()
        self.welcome_label = ctk.CTkLabel(self.content_frame, text=welcome_text,
                                          font=("Arial", 24, "bold"))
        self.welcome_label.pack(pady=(20, 10))

        info_label = ctk.CTkLabel(self.content_frame, text="Rezervasyon, personel ve rapor yönetimini buradan yapabilirsiniz.",
                                  font=("Arial", 16))
        info_label.pack(pady=(0, 20))

        date_label = ctk.CTkLabel(self.content_frame, text=f"Bugün: {datetime.now().strftime('%d %B %Y')}",
                                  font=("Arial", 14))
        date_label.pack(pady=(0, 30))

        # Takvim Alanı
        self.create_calendar_area()

    # ---------------------------------------------------
    # Takvim Alanı (3 Aylık Görünüm)
    # ---------------------------------------------------
    def create_calendar_area(self):
        calendar_frame = ctk.CTkFrame(self.content_frame)
        calendar_frame.pack(pady=20, fill="x")

        header = ctk.CTkLabel(calendar_frame, text="3 Aylık Rezervasyon Takvimi", font=("Arial", 18, "bold"))
        header.pack(pady=(10, 20))

        controls_frame = ctk.CTkFrame(calendar_frame, fg_color="transparent")
        controls_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.refresh_button = ctk.CTkButton(
            controls_frame,
            text="Takvimi Yenile",
            width=140,
            command=self.manual_refresh,
        )
        self.refresh_button.pack(side="left")

        self.refresh_status_label = ctk.CTkLabel(
            controls_frame,
            text="Son güncelleme: -",
            font=("Arial", 12),
        )
        self.refresh_status_label.pack(side="left", padx=(12, 0))

        months_frame = ctk.CTkFrame(calendar_frame)
        months_frame.pack(padx=10, pady=10, fill="x")
        self.months_frame = months_frame
        self.refresh_calendar(force=True)

        # Renk Efsanesi
        self.create_legend()

    def refresh_calendar(self, force=False):
        if not hasattr(self, "months_frame"):
            return
        today = datetime.now().date()
        month_dates = list(self._target_months(today, count=3))
        month_keys = [(month.year, month.month) for month in month_dates]
        self._prune_month_cache(month_keys)

        if (
            not force
            and not self._calendar_dirty
            and self._last_rendered_months == month_keys
            and self._last_rendered_today == today
        ):
            return

        for child in self.months_frame.winfo_children():
            child.destroy()

        for month_date in month_dates:
            month_events = self._get_month_events(month_date.year, month_date.month)
            self.add_month_calendar(self.months_frame, month_date, month_events)

        self._last_refresh_time = datetime.now()
        self._calendar_dirty = False
        self._last_rendered_months = month_keys
        self._last_rendered_today = today
        self._update_refresh_status()
        self._schedule_auto_refresh()

    def _get_month_events(self, year, month):
        key = (year, month)
        if key not in self._month_cache:
            try:
                self._month_cache[key] = get_calendar_data(year, month)
            except Exception as exc:
                self._month_cache[key] = {}
                messagebox.showerror("Hata", f"Rezervasyonlar yüklenemedi:\n{exc}")
        return self._month_cache[key]

    def _prune_month_cache(self, active_keys):
        for cache_key in list(self._month_cache.keys()):
            if cache_key not in active_keys:
                self._month_cache.pop(cache_key, None)

    def _target_months(self, base_date, count=3):
        month_start = datetime(base_date.year, base_date.month, 1)
        for _ in range(count):
            yield month_start
            year = month_start.year + (month_start.month // 12)
            month = month_start.month % 12 + 1
            month_start = datetime(year, month, 1)

    def _schedule_auto_refresh(self):
        self._cancel_auto_refresh()
        self._auto_refresh_job = self.after(self._auto_refresh_ms, self._auto_refresh)

    def _cancel_auto_refresh(self):
        if self._auto_refresh_job is not None:
            try:
                self.after_cancel(self._auto_refresh_job)
            except Exception:
                pass
            self._auto_refresh_job = None

    def _auto_refresh(self):
        self._auto_refresh_job = None
        self.mark_dirty(status_pending=False)
        if self._is_visible:
            self.refresh_calendar(force=True)
        else:
            self._schedule_auto_refresh()

    def create_legend(self):
        legend_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        legend_frame.pack(pady=(30, 10))

        legend_items = [
            ("Boş Gün", "#FFFFFF", "black"),
            ("Bayram / Özel Gün", "#8B5CF6", "white"),
            ("Etkinlikli Gün", "#F97316", "white"),
            ("Bugün", "#FACC15", "black")
        ]

        for text, color, tcolor in legend_items:
            item = ctk.CTkFrame(legend_frame, fg_color="transparent")
            item.pack(side="left", padx=12)

            color_box = ctk.CTkLabel(item, text="", width=16, height=16, fg_color=color, corner_radius=4)
            try:
                color_box.configure(border_width=1, border_color="#D1D5DB")
            except Exception:
                pass
            color_box.pack(side="left", padx=(0,8))
            label = ctk.CTkLabel(item, text=text, font=("Arial", 11))
            label.pack(side="left")

    def add_month_calendar(self, parent, date, events_by_date):
        month_name = date.strftime("%B %Y")
        frame = ctk.CTkFrame(parent, fg_color="#374151", corner_radius=10)
        frame.pack(side="left", padx=10, pady=10, fill="both", expand=True)

        label = ctk.CTkLabel(frame, text=month_name, font=("Arial", 17, "bold"))
        label.pack(pady=8)

        cal = calendar.Calendar()
        days_frame = ctk.CTkFrame(frame)
        days_frame.pack(padx=10, pady=10)

        weekdays = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
        for col, day in enumerate(weekdays):
            ctk.CTkLabel(days_frame, text=day, width=60, font=("Arial", 12, "bold")).grid(row=0, column=col, pady=4)

        holidays = {(1, 1), (23, 4), (19, 5), (30, 8), (29, 10)}
        today = datetime.now().date()

        row = 1
        for week in cal.monthdayscalendar(date.year, date.month):
            col = 0
            for day in week:
                if day == 0:
                    ctk.CTkLabel(days_frame, text="", width=60, height=50).grid(row=row, column=col)
                else:
                    current_day = datetime(date.year, date.month, day).date()
                    date_str = current_day.isoformat()
                    event_count = len(events_by_date.get(date_str, []))

                    base_color = "#FFFFFF"
                    text_color = "black"

                    if (current_day.day, current_day.month) in holidays:
                        base_color = "#8B5CF6"  # Bayram
                        text_color = "white"
                    elif current_day == today:
                        base_color = "#FACC15"  # Bugün (Sarı)
                        text_color = "black"
                    elif event_count:
                        base_color = "#F97316"  # Etkinlikli gün
                        text_color = "white"

                    hover_map = {
                        "#FFFFFF": "#E5E7EB",
                        "#8B5CF6": "#7C3AED",
                        "#F97316": "#EA580C",
                        "#FACC15": "#EAB308",
                    }
                    hover_color = hover_map.get(base_color, "#E5E7EB")

                    btn_text = str(day)
                    if event_count:
                        btn_text += f"\n({event_count})"

                    ctk.CTkButton(
                        days_frame,
                        text=btn_text,
                        width=60,
                        height=50,
                        fg_color=base_color,
                        text_color=text_color,
                        corner_radius=6,
                        hover_color=hover_color,
                        command=lambda d=date_str: self.open_reservations_for_date(d),
                    ).grid(row=row, column=col, padx=4, pady=4)

                col += 1
            row += 1

    def _build_welcome_text(self):
        name = self.user.get("name") or self.user.get("username") or ""
        if name:
            return f"Hoş Geldiniz, {name}! 👋"
        return "Düğün Salonu Yönetim Paneline Hoş Geldiniz 👋"

    def update_user(self, user):
        self.user = user or {}
        if hasattr(self, "welcome_label"):
            self.welcome_label.configure(text=self._build_welcome_text())

    def mark_dirty(self, status_pending=True):
        self._calendar_dirty = True
        self._month_cache.clear()
        if status_pending:
            self._update_refresh_status(pending=True)

    def manual_refresh(self):
        self.mark_dirty(status_pending=False)
        self.refresh_calendar(force=True)

    def on_show(self):
        self._is_visible = True
        should_refresh = (
            self._calendar_dirty
            or self._last_refresh_time is None
            or self._last_rendered_today != datetime.now().date()
        )
        if should_refresh:
            self.refresh_calendar(force=self._calendar_dirty)
        else:
            self._update_refresh_status()

    def on_hide(self):
        self._is_visible = False

    def destroy(self):
        self._cancel_auto_refresh()
        super().destroy()

    def _update_refresh_status(self, pending=False):
        if not hasattr(self, "refresh_status_label"):
            return
        if pending:
            text = "Son güncelleme: bekleniyor..."
        elif self._last_refresh_time:
            text = f"Son güncelleme: {self._last_refresh_time.strftime('%H:%M:%S')}"
        else:
            text = "Son güncelleme: -"
        self.refresh_status_label.configure(text=text)

    def open_reservations_for_date(self, date_str=None):
        if not self.on_open_reservations:
            return
        try:
            if date_str is not None:
                self.on_open_reservations(date_str)
            else:
                self.on_open_reservations()
        except TypeError:
            self.on_open_reservations()

    # ---------------------------------------------------
    # Buton Fonksiyonları
    # ---------------------------------------------------
    def handle_logout(self):
        if self.on_logout:
            self.on_logout()

    def handle_reservations(self):
        print("Rezervasyonlar sayfası açılacak")
        self.open_reservations_for_date()

    def handle_personnel(self):
        print("Personel sayfası açılacak")
        if self.on_open_personnel:
            self.on_open_personnel()

    def handle_reports(self):
        print("Raporlar sayfası açılacak")
        if self.on_open_reports:
            self.on_open_reports()

    def handle_settings(self):
        print("Ayarlar sayfası açılacak")
        if self.on_open_settings:
            self.on_open_settings()
