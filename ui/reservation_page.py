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
        self.selected_date: str | None = None
        self.event_data: dict[str, list[dict]] = {}
        self._needs_refresh = True
        self._last_target_date: str | None = None

        self.bulk_mode = False
        self.selected_ids: set[str] = set()
        self.active_row_id: str | None = None
        self._skip_outside_once = False
        self._global_click_registered = False

        self.panel_target_width = 320
        self.panel_animation_duration = 200
        self.panel_animation_steps = 12
        self._panel_slide_offset = float(self.panel_target_width)
        self._panel_anim_after_id = None
        self._panel_animating = False
        self.action_panel_visible = False
        self.action_panel_data: dict | None = None
        self._pending_panel_open: tuple[str, dict] | None = None

        self.row_widgets: dict[str, dict] = {}
        self.row_colors = ("#FFFFFF", "#F3F4F6")
        self.status_styles = {
            "iptal edildi": {"bg": "#FEE2E2", "border": "#F87171"},
            "iptal": {"bg": "#FEE2E2", "border": "#F87171"},
            "beklemede": {"bg": "#FEF3C7", "border": "#FACC15"},
            "onaylandi": {"bg": "#DCFCE7", "border": "#34D399"},
        }

        self.table_columns = [
            {"title": "Sira", "width": 70},
            {"title": "Rezervasyon Tarihi", "width": 160},
            {"title": "Salon Adi", "width": 180},
            {"title": "Musteri Adi / Soyadi", "width": 220},
            {"title": "Etkinlik Turu", "width": 150},
            {"title": "Durum", "width": 140, "weight": 1},
        ]

        self.month_labels = [
            "Ocak",
            "Subat",
            "Mart",
            "Nisan",
            "Mayis",
            "Haziran",
            "Temmuz",
            "Agustos",
            "Eylul",
            "Ekim",
            "Kasim",
            "Aralik",
        ]

        self._build_header()
        self._build_content()
        self._build_footer()

        self._set_selected_date(self.current_date.date().isoformat())
        self.refresh_data(target_date=self.selected_date)

    # ------------------------------------------------------------------
    # UI construction helpers
    # ------------------------------------------------------------------
    def _build_header(self):
        ctk.CTkLabel(self, text="Rezervasyonlar", font=("Arial", 28, "bold")).pack(pady=(20, 8))

        control_frame = ctk.CTkFrame(self, fg_color="transparent")
        control_frame.pack(pady=(0, 10))

        ctk.CTkButton(
            control_frame,
            text="Onceki Ay",
            width=120,
            fg_color="#374151",
            hover_color="#4B5563",
            command=self.prev_month,
        ).grid(row=0, column=0, padx=8)

        years = [str(y) for y in range(2020, 2031)]
        days = [str(d) for d in range(1, 32)]
        self.day_var = ctk.StringVar(value=str(self.current_date.day))
        self.month_var = ctk.StringVar(value=self.month_labels[self.current_date.month - 1])
        self.year_var = ctk.StringVar(value=str(self.current_date.year))

        ctk.CTkComboBox(
            control_frame,
            values=days,
            variable=self.day_var,
            width=80,
            command=lambda _: self.manual_date_change(),
        ).grid(row=0, column=1, padx=6)

        ctk.CTkComboBox(
            control_frame,
            values=self.month_labels,
            variable=self.month_var,
            width=140,
            command=lambda _: self.manual_date_change(),
        ).grid(row=0, column=2, padx=6)

        ctk.CTkComboBox(
            control_frame,
            values=years,
            variable=self.year_var,
            width=100,
            command=lambda _: self.manual_date_change(),
        ).grid(row=0, column=3, padx=6)

        ctk.CTkButton(
            control_frame,
            text="Sonraki Ay",
            width=120,
            fg_color="#374151",
            hover_color="#4B5563",
            command=self.next_month,
        ).grid(row=0, column=4, padx=8)

        self.list_header = ctk.CTkFrame(self, fg_color="transparent")
        self.list_header.pack(fill="x", padx=32, pady=(4, 0))

        self.date_label = ctk.CTkLabel(self.list_header, text="", font=("Arial", 16, "bold"))
        self.date_label.pack(side="left")

        self.bulk_container = ctk.CTkFrame(self.list_header, fg_color="transparent")
        self.bulk_container.pack(side="right")

        self.bulk_btn = ctk.CTkButton(
            self.bulk_container,
            text="Toplu Secim",
            width=130,
            fg_color="#4B5563",
            hover_color="#6B7280",
            command=self.toggle_bulk_mode,
        )
        self.bulk_btn.pack(side="right")

        self.bulk_actions_frame = ctk.CTkFrame(self.bulk_container, fg_color="transparent")
        self.bulk_edit_btn = ctk.CTkButton(
            self.bulk_actions_frame,
            text="Duzenle",
            width=90,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self._bulk_edit,
        )
        self.bulk_delete_btn = ctk.CTkButton(
            self.bulk_actions_frame,
            text="Sil",
            width=70,
            fg_color="#DC2626",
            hover_color="#B91C1C",
            command=self._bulk_delete,
        )

    def _build_content(self):
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=32, pady=(6, 10))
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        self.table_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            corner_radius=14,
            fg_color="#F8FAFC",
            border_width=1,
            border_color="#E5E7EB",
        )
        self.table_frame.grid(row=0, column=0, sticky="nsew")

        self.panel_container = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent",
            width=self.panel_target_width,
        )
        self.panel_container.grid(row=0, column=1, sticky="ns", padx=(20, 0), pady=10)
        self.panel_container.grid_propagate(False)

        self.action_panel = ctk.CTkFrame(
            self.panel_container,
            corner_radius=16,
            fg_color="#111827",
            width=self.panel_target_width,
        )
        self.action_panel.place(x=self.panel_target_width, y=0, relheight=1.0)

        self.panel_title_var = ctk.StringVar(value="Rezervasyon Detayi")
        self.panel_subtitle_var = ctk.StringVar(value="")
        self.panel_status_var = ctk.StringVar(value="")
        self.panel_salon_var = ctk.StringVar(value="-")
        self.panel_date_var = ctk.StringVar(value="-")
        self.panel_client_var = ctk.StringVar(value="-")
        self.panel_event_var = ctk.StringVar(value="-")
        self.panel_time_var = ctk.StringVar(value="-")
        self.panel_guest_var = ctk.StringVar(value="-")

        panel_inner = ctk.CTkFrame(self.action_panel, fg_color="transparent")
        panel_inner.pack(fill="both", expand=True, padx=18, pady=18)

        title_row = ctk.CTkFrame(panel_inner, fg_color="transparent")
        title_row.pack(fill="x")

        ctk.CTkLabel(
            title_row,
            textvariable=self.panel_title_var,
            font=("Arial", 20, "bold"),
            text_color="white",
        ).pack(side="left")

        self.panel_close_btn = ctk.CTkButton(
            title_row,
            text="x",
            width=32,
            height=32,
            fg_color="#1F2937",
            hover_color="#374151",
            text_color="#F8FAFC",
            font=("Arial", 18, "bold"),
            corner_radius=16,
            command=self.hide_action_panel,
        )
        self.panel_close_btn.pack(side="right")
        self.panel_close_btn.configure(cursor="hand2")

        ctk.CTkLabel(
            panel_inner,
            textvariable=self.panel_subtitle_var,
            font=("Arial", 13),
            text_color="#CBD5F5",
        ).pack(anchor="w", pady=(4, 10))

        self.panel_status_chip = ctk.CTkLabel(
            panel_inner,
            textvariable=self.panel_status_var,
            font=("Arial", 12, "bold"),
            text_color="#111827",
            fg_color="#F8FAFC",
            corner_radius=20,
            padx=14,
            pady=6,
        )
        self.panel_status_chip.pack(anchor="w", pady=(0, 18))

        info_items = (
            ("Salon Adi", self.panel_salon_var),
            ("Rezervasyon Tarihi", self.panel_date_var),
            ("Musteri", self.panel_client_var),
            ("Etkinlik Turu", self.panel_event_var),
            ("Saat", self.panel_time_var),
            ("Davetli Sayisi", self.panel_guest_var),
        )

        for label, var in info_items:
            wrapper = ctk.CTkFrame(panel_inner, fg_color="transparent")
            wrapper.pack(fill="x", pady=4)
            ctk.CTkLabel(wrapper, text=label, font=("Arial", 12, "bold"), text_color="#CBD5F5").pack(anchor="w")
            ctk.CTkLabel(wrapper, textvariable=var, font=("Arial", 13), text_color="white").pack(anchor="w")

        ctk.CTkLabel(panel_inner, text="Notlar", font=("Arial", 12, "bold"), text_color="#CBD5F5").pack(anchor="w", pady=(16, 4))
        self.panel_notes_label = ctk.CTkLabel(
            panel_inner,
            text="Not bulunmuyor.",
            font=("Arial", 12),
            text_color="white",
            justify="left",
            wraplength=260,
        )
        self.panel_notes_label.pack(anchor="w")

        button_row = ctk.CTkFrame(panel_inner, fg_color="transparent")
        button_row.pack(fill="x", pady=(28, 0))

        self.panel_edit_btn = ctk.CTkButton(
            button_row,
            text="Duzenle",
            width=120,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=lambda: self._edit_reservation(self.action_panel_data or {}),
        )
        self.panel_edit_btn.pack(side="left", padx=(0, 8))

        self.panel_delete_btn = ctk.CTkButton(
            button_row,
            text="Sil",
            width=100,
            fg_color="#DC2626",
            hover_color="#B91C1C",
            command=lambda: self._delete_reservation(self.action_panel_data or {}),
        )
        self.panel_delete_btn.pack(side="left")

        self.panel_container.grid_remove()

        self._register_global_click()

    def _build_footer(self):
        bottom_btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_btn_frame.pack(pady=(4, 18))

        self.add_btn = ctk.CTkButton(
            bottom_btn_frame,
            text="Yeni Rezervasyon Ekle",
            width=220,
            height=42,
            fg_color="#F97316",
            hover_color="#EA580C",
            command=self.open_add_reservation,
        )
        self.add_btn.grid(row=0, column=0, padx=10)

        self.back_btn = ctk.CTkButton(
            bottom_btn_frame,
            text="Cikis",
            width=130,
            height=42,
            fg_color="gray20",
            hover_color="#4B5563",
            command=self.handle_back,
        )
        self.back_btn.grid(row=0, column=1, padx=10)

    # ------------------------------------------------------------------
    # Data rendering
    # ------------------------------------------------------------------
    def show_reservations(self, date_str: str):
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        self.row_widgets.clear()
        if not self.bulk_mode:
            self.selected_ids.clear()
        self._deactivate_current_row()

        try:
            events = get_reservations_for_date(date_str)
        except Exception as exc:
            messagebox.showerror("Hata", f"Rezervasyonlar yuklenemedi:\n{exc}")
            self._render_table_header()
            self._render_empty_state("Rezervasyonlar yuklenirken hata olustu.")
            self.update_bulk_actions()
            return

        self._render_table_header()

        if not events:
            self._render_empty_state("Bu tarihte rezervasyon bulunmuyor.")
            self.update_bulk_actions()
            return

        for index, event in enumerate(events, start=1):
            self._render_row(index, event)

        self.update_bulk_actions()

    def _render_table_header(self):
        header = ctk.CTkFrame(self.table_frame, fg_color="#E2E8F0", corner_radius=10)
        header.pack(fill="x", padx=8, pady=(0, 8))

        for column_index, column in enumerate(self._get_columns()):
            header.grid_columnconfigure(column_index, weight=column.get("weight", 0))
            title = column.get("title", "")
            if not title:
                continue
            pad_left = 18 if column_index == 0 else 12
            ctk.CTkLabel(
                header,
                text=title,
                font=("Arial", 13, "bold"),
                text_color="#1F2937",
                anchor="w",
            ).grid(row=0, column=column_index, sticky="w", padx=(pad_left, 6), pady=10)

    def _render_row(self, index: int, data: dict):
        columns = self._get_columns()

        status_label = self._normalize_status(data.get("status"))
        style = self.status_styles.get(status_label.lower())

        base_color = style["bg"] if style else self.row_colors[(index - 1) % len(self.row_colors)]
        border_color = style["border"] if style else "#E5E7EB"

        row_id = str(data.get("id") or f"row-{index}")
        row_frame = ctk.CTkFrame(
            self.table_frame,
            fg_color=base_color,
            corner_radius=10,
            border_width=1,
            border_color=border_color,
        )
        row_frame.pack(fill="x", padx=8, pady=4)
        row_frame.grid_columnconfigure(len(columns) - 1, weight=columns[-1].get("weight", 0))
        row_frame.configure(cursor="hand2")

        row_info = {
            "frame": row_frame,
            "data": data,
            "base_color": base_color,
            "border_color": border_color,
            "hover_color": self._lighten_color(base_color, 0.08),
            "active": False,
            "hovered": False,
            "bulk_selected": False,
            "var": None,
        }

        current_column = 0
        bound_widgets: list = []

        if self.bulk_mode:
            var = ctk.BooleanVar(value=row_id in self.selected_ids)

            def on_check(rid=row_id, control_var=var):
                self._on_row_checked(rid, control_var)

            checkbox = ctk.CTkCheckBox(row_frame, text="", variable=var, command=on_check)
            checkbox.grid(row=0, column=current_column, padx=(20, 8), pady=14, sticky="w")
            row_info["var"] = var
            if var.get():
                row_info["bulk_selected"] = True
            bound_widgets.append(checkbox)
            current_column += 1

        values = [
            f"{index:02d}",
            self._format_date(data.get("event_date")),
            data.get("salon") or "-",
            data.get("client_name") or "-",
            data.get("event_type") or "-",
            status_label,
        ]

        for offset, value in enumerate(values):
            column_index = current_column + offset
            column = columns[column_index]
            pad_left = 20 if column_index == current_column else 14
            label = ctk.CTkLabel(
                row_frame,
                text=value,
                font=("Arial", 13),
                text_color="#111827",
                anchor="w",
            )
            sticky = "w" if column.get("weight", 0) == 0 else "ew"
            label.grid(row=0, column=column_index, sticky=sticky, padx=(pad_left, 8), pady=14)
            bound_widgets.append(label)

        self.row_widgets[row_id] = row_info
        self._configure_row_bindings(row_id, bound_widgets)
        self._refresh_row_visual(row_id)

    def _configure_row_bindings(self, row_id: str, children):
        entry = self.row_widgets.get(row_id)
        if not entry:
            return

        def handle_click(_event):
            self._handle_row_selection(row_id, entry["data"])

        def handle_enter(_event):
            self._on_row_hover(row_id, True)

        def handle_leave(_event):
            self._on_row_hover(row_id, False)

        entry["frame"].bind("<Button-1>", handle_click, add="+")
        entry["frame"].bind("<Enter>", handle_enter, add="+")
        entry["frame"].bind("<Leave>", handle_leave, add="+")

        for widget in children:
            widget.bind("<Button-1>", handle_click, add="+")
            widget.bind("<Enter>", handle_enter, add="+")
            widget.bind("<Leave>", handle_leave, add="+")

    def _render_empty_state(self, message: str):
        placeholder = ctk.CTkFrame(self.table_frame, fg_color="#FFFFFF", corner_radius=10)
        placeholder.pack(fill="x", padx=12, pady=12)
        ctk.CTkLabel(
            placeholder,
            text=message,
            font=("Arial", 13),
            text_color="#6B7280",
        ).pack(padx=16, pady=18)

    # ------------------------------------------------------------------
    # Row selection & bulk actions
    # ------------------------------------------------------------------
    def _handle_row_selection(self, row_id: str, data: dict):
        if self.bulk_mode:
            entry = self.row_widgets.get(row_id)
            if not entry or entry.get("var") is None:
                return
            new_value = not entry["var"].get()
            entry["var"].set(new_value)
            self._on_row_checked(row_id, entry["var"])
            return

        if self.action_panel_visible:
            if self.active_row_id == row_id:
                self._pending_panel_open = None
                self.hide_action_panel()
                return

            self._pending_panel_open = (row_id, data)
            self.hide_action_panel()
            return

        self._pending_panel_open = None
        self._skip_outside_once = True
        self._set_active_row(row_id, data)

    def _set_active_row(self, row_id: str, data: dict):
        if self.active_row_id and self.active_row_id in self.row_widgets:
            prev_entry = self.row_widgets[self.active_row_id]
            prev_entry["active"] = False
            self._refresh_row_visual(self.active_row_id)

        entry = self.row_widgets.get(row_id)
        if not entry:
            return

        entry["active"] = True
        entry["hovered"] = False
        self.active_row_id = row_id
        self._refresh_row_visual(row_id)
        self.show_action_panel(data)

    def _on_row_checked(self, row_id: str, var: ctk.BooleanVar):
        entry = self.row_widgets.get(row_id)
        if not entry:
            return

        if var.get():
            self.selected_ids.add(row_id)
            entry["bulk_selected"] = True
        else:
            self.selected_ids.discard(row_id)
            entry["bulk_selected"] = False

        self._refresh_row_visual(row_id)
        self.update_bulk_actions()

    def _on_row_hover(self, row_id: str, entering: bool):
        entry = self.row_widgets.get(row_id)
        if not entry or entry.get("active"):
            return
        if self.bulk_mode and entry.get("bulk_selected"):
            return
        entry["hovered"] = entering
        self._refresh_row_visual(row_id)

    def _refresh_row_visual(self, row_id: str):
        entry = self.row_widgets.get(row_id)
        if not entry:
            return

        if entry.get("active"):
            fg_color = "#DBEAFE"
            border_color = "#60A5FA"
        elif entry.get("bulk_selected"):
            fg_color = "#E0F2FE"
            border_color = "#38BDF8"
        elif entry.get("hovered"):
            fg_color = entry["hover_color"]
            border_color = entry["border_color"]
        else:
            fg_color = entry["base_color"]
            border_color = entry["border_color"]

        entry["frame"].configure(fg_color=fg_color, border_color=border_color)

    def _deactivate_current_row(self):
        if not self.active_row_id:
            return
        entry = self.row_widgets.get(self.active_row_id)
        if entry:
            entry["active"] = False
            entry["hovered"] = False
            self._refresh_row_visual(self.active_row_id)
        self.active_row_id = None

    def toggle_bulk_mode(self):
        self.bulk_mode = not self.bulk_mode
        self.bulk_btn.configure(text="Secimi Kapat" if self.bulk_mode else "Toplu Secim")
        self.selected_ids.clear()
        self._deactivate_current_row()
        if self.action_panel_visible:
            self.hide_action_panel()
        if self.selected_date:
            self.show_reservations(self.selected_date)

    def update_bulk_actions(self):
        for child in self.bulk_actions_frame.winfo_children():
            child.pack_forget()

        if self.bulk_mode and self.selected_ids:
            self.bulk_actions_frame.pack(side="right", padx=(0, 10))
            self.bulk_edit_btn.pack(side="left", padx=4)
            self.bulk_delete_btn.pack(side="left", padx=4)
        else:
            self.bulk_actions_frame.pack_forget()

    # ------------------------------------------------------------------
    # Action panel behaviour
    # ------------------------------------------------------------------
    def show_action_panel(self, data: dict):
        self._skip_outside_once = True
        self.action_panel_data = data
        self.panel_title_var.set(data.get("client_name") or "Rezervasyon Detayi")
        subtitle_parts = [self._format_date(data.get("event_date")), data.get("salon") or "-"]
        self.panel_subtitle_var.set(" | ".join(part for part in subtitle_parts if part))
        status_label = self._normalize_status(data.get("status"))
        self.panel_status_var.set(status_label)
        self.panel_salon_var.set(data.get("salon") or "-")
        self.panel_date_var.set(self._format_date(data.get("event_date")))
        self.panel_client_var.set(data.get("client_name") or "-")
        self.panel_event_var.set(data.get("event_type") or "-")
        self.panel_time_var.set(self._format_time_range(data.get("start_time"), data.get("end_time")))
        guests = data.get("guests")
        self.panel_guest_var.set(str(guests) if guests is not None else "-")
        notes = data.get("special_request") or data.get("menu_detail") or data.get("tahsilatlar") or "Not bulunmuyor."
        self.panel_notes_label.configure(text=notes)

        if not self.action_panel_visible:
            self.panel_container.grid()
            self.action_panel_visible = True
            self._panel_slide_offset = float(self.panel_target_width)
            self.action_panel.place_configure(x=self._panel_slide_offset)
        self._animate_panel(opening=True)

    def hide_action_panel(self):
        if not self.action_panel_visible:
            return
        self._deactivate_current_row()
        self.action_panel_data = None
        self._skip_outside_once = False
        self._animate_panel(opening=False)

    def _animate_panel(self, opening: bool):
        if self._panel_anim_after_id is not None:
            self.after_cancel(self._panel_anim_after_id)
            self._panel_anim_after_id = None

        self._panel_animating = True
        total_steps = max(1, self.panel_animation_steps)
        step_distance = self.panel_target_width / total_steps
        step_time = max(10, self.panel_animation_duration // total_steps)

        def step():
            if opening:
                self._panel_slide_offset = max(0.0, self._panel_slide_offset - step_distance)
            else:
                self._panel_slide_offset = min(float(self.panel_target_width), self._panel_slide_offset + step_distance)

            self.action_panel.place_configure(x=self._panel_slide_offset)

            if (opening and self._panel_slide_offset > 0.0) or (not opening and self._panel_slide_offset < self.panel_target_width):
                self._panel_anim_after_id = self.after(step_time, step)
            else:
                self._panel_anim_after_id = None
                self._panel_animating = False
                if opening:
                    self.action_panel.place_configure(x=0)
                else:
                    self.panel_container.grid_remove()
                    self.action_panel_visible = False
                    self._panel_slide_offset = float(self.panel_target_width)
                    pending = self._pending_panel_open
                    self._pending_panel_open = None
                    if pending:
                        row_id, pending_data = pending
                        if row_id in self.row_widgets:
                            self._skip_outside_once = True
                            self._set_active_row(row_id, pending_data)

        step()

    # ------------------------------------------------------------------
    # Navigation & data refresh
    # ------------------------------------------------------------------
    def next_month(self):
        year = self.current_date.year + (1 if self.current_date.month == 12 else 0)
        month = 1 if self.current_date.month == 12 else self.current_date.month + 1
        day = min(int(self.day_var.get()), calendar.monthrange(year, month)[1])
        self.current_date = datetime(year, month, 1)
        self.month_var.set(self.month_labels[self.current_date.month - 1])
        self.year_var.set(str(year))
        self.day_var.set(str(day))
        self._set_selected_date(datetime(year, month, day).date().isoformat())
        self.show_reservations(self.selected_date)

    def prev_month(self):
        year = self.current_date.year - (1 if self.current_date.month == 1 else 0)
        month = 12 if self.current_date.month == 1 else self.current_date.month - 1
        day = min(int(self.day_var.get()), calendar.monthrange(year, month)[1])
        self.current_date = datetime(year, month, 1)
        self.month_var.set(self.month_labels[self.current_date.month - 1])
        self.year_var.set(str(year))
        self.day_var.set(str(day))
        self._set_selected_date(datetime(year, month, day).date().isoformat())
        self.show_reservations(self.selected_date)

    def manual_date_change(self):
        month_index = {name: idx + 1 for idx, name in enumerate(self.month_labels)}
        month = month_index.get(self.month_var.get(), self.current_date.month)
        year = int(self.year_var.get())
        max_day = calendar.monthrange(year, month)[1]
        try:
            day = max(1, min(int(self.day_var.get()), max_day))
        except ValueError:
            day = 1
        self.current_date = datetime(year, month, 1)
        self.day_var.set(str(day))
        self._set_selected_date(datetime(year, month, day).date().isoformat())
        self.show_reservations(self.selected_date)

    def open_add_reservation(self):
        if self.add_reservation:
            self.add_reservation(self.selected_date)

    def handle_back(self):
        if self.on_back:
            self.on_back()

    def refresh_month_data(self):
        try:
            self.event_data = get_calendar_data(self.current_date.year, self.current_date.month)
        except Exception:
            self.event_data = {}

    def refresh_data(self, target_date=None):
        self.refresh_month_data()
        if target_date:
            self._set_selected_date(target_date)
        if self.selected_date:
            self.show_reservations(self.selected_date)
        self._needs_refresh = False
        self._last_target_date = target_date or self.selected_date

    def mark_dirty(self):
        self._needs_refresh = True

    @property
    def needs_refresh(self):
        return self._needs_refresh

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _set_selected_date(self, iso_date: str | None):
        if not iso_date:
            return
        self.selected_date = iso_date
        try:
            dt = datetime.strptime(iso_date, "%Y-%m-%d")
        except ValueError:
            dt = datetime.now()
        self.day_var.set(str(dt.day))
        self.month_var.set(self.month_labels[dt.month - 1])
        self.year_var.set(str(dt.year))
        self.date_label.configure(text=f"{dt.strftime('%d.%m.%Y')} Tarihli Rezervasyonlar")

    def _get_columns(self):
        if self.bulk_mode:
            return [{"title": "", "width": 48}] + self.table_columns
        return list(self.table_columns)

    @staticmethod
    def _format_date(value):
        if not value:
            return "-"
        patterns = ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y")
        for pattern in patterns:
            try:
                parsed = datetime.strptime(str(value), pattern)
                return parsed.strftime("%d.%m.%Y")
            except ValueError:
                continue
        return str(value)

    @staticmethod
    def _format_time_range(start, end):
        start_str = start or "-"
        end_str = end or "-"
        if start_str == "-" and end_str == "-":
            return "-"
        return f"{start_str} - {end_str}"

    @staticmethod
    def _normalize_status(value: str | None):
        if not value:
            return "Durum Bilinmiyor"
        normalized = value.strip().lower()
        mapping = {
            "onaylandi": "Onaylandi",
            "beklemede": "Beklemede",
            "iptal edildi": "Iptal Edildi",
            "iptal": "Iptal Edildi",
        }
        return mapping.get(normalized, value)

    @staticmethod
    def _lighten_color(hex_color: str, factor: float = 0.1):
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            return '#FFFFFF'
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        r = int(r + (255 - r) * factor)
        g = int(g + (255 - g) * factor)
        b = int(b + (255 - b) * factor)
        return f"#{r:02X}{g:02X}{b:02X}"

    def _on_global_click(self, event):
        if not self.action_panel_visible:
            return
        if self._skip_outside_once:
            self._skip_outside_once = False
            return
        if self._is_widget_descendant(event.widget, self.action_panel):
            return
        self.hide_action_panel()

    @staticmethod
    def _is_widget_descendant(widget, ancestor):
        current = widget
        while current is not None:
            if current is ancestor:
                return True
            current = getattr(current, "master", None)
        return False

    def _register_global_click(self):
        if self._global_click_registered:
            return
        toplevel = self.winfo_toplevel()
        if toplevel is None:
            return
        toplevel.bind("<Button-1>", self._on_global_click, add="+")
        self._global_click_registered = True

    def _bulk_edit(self):
        if not self.selected_ids:
            messagebox.showinfo("Toplu Duzenle", "Lutfen en az bir rezervasyon secin.")
            return
        messagebox.showinfo("Toplu Duzenle", f"Secili {len(self.selected_ids)} rezervasyon icin duzenleme islemi planlanacak.")

    def _bulk_delete(self):
        if not self.selected_ids:
            messagebox.showinfo("Toplu Sil", "Lutfen en az bir rezervasyon secin.")
            return
        messagebox.showinfo("Toplu Sil", f"Secili {len(self.selected_ids)} rezervasyon silinecek (onay bekleniyor).")

    def _edit_reservation(self, data: dict):
        rid = data.get("id")
        client = data.get("client_name") or "-"
        messagebox.showinfo("Duzenle", f"Rezervasyon duzenleme (ID: {rid})\nMusteri: {client}")

    def _delete_reservation(self, data: dict):
        rid = data.get("id")
        client = data.get("client_name") or "-"
        messagebox.showinfo("Sil", f"Rezervasyon silme islemi (ID: {rid})\nMusteri: {client}")