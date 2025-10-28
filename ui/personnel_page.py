import calendar
from collections import defaultdict
from datetime import date

import customtkinter as ctk
from tkcalendar import DateEntry
from tkinter import messagebox


class PersonnelPage(ctk.CTkFrame):
    def __init__(self, master, on_back=None):
        super().__init__(master)
        self.master = master
        self.on_back = on_back

        self.personnel_data: list[dict] = []
        self.assignment_data: list[dict] = []
        self.attendance_data: dict[str, str] = {}
        self._assignment_id = 0

        today = date.today()
        self.calendar_year = today.year
        self.calendar_month = today.month

        title = ctk.CTkLabel(self, text="Personel Yonetim Sayfasi", font=("Arial", 24, "bold"))
        title.pack(pady=(20, 10))

        self.tabview = ctk.CTkTabview(self, width=960, height=520)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=(0, 12))

        self._build_personnel_tab(self.tabview.add("Personel Listesi"))
        self._build_assignment_tab(self.tabview.add("Gorev Atama"))
        self._build_calendar_tab(self.tabview.add("Takvim Gorunumu"))
        self._build_attendance_tab(self.tabview.add("Geldi/Gelmedi"))
        self._build_reports_tab(self.tabview.add("Ucret Raporlari"))

        ctk.CTkButton(self, text="← Geri Don", fg_color="gray20", command=self._handle_back).pack(pady=(0, 16))

    # ------------------------------------------------------------------
    # Personel listesi
    # ------------------------------------------------------------------
    def _build_personnel_tab(self, tab):
        header = ctk.CTkFrame(tab, fg_color="transparent")
        header.pack(fill="x", pady=(12, 8), padx=16)

        ctk.CTkLabel(header, text="Kayitli Personeller", font=("Arial", 16, "bold")).pack(side="left")
        ctk.CTkButton(
            header,
            text="+ Yeni Personel",
            width=160,
            fg_color="#10B981",
            hover_color="#059669",
            command=self._toggle_add_form,
        ).pack(side="right")

        self.add_form = ctk.CTkFrame(tab, fg_color="#1F2937", corner_radius=12)
        self.add_form_visible = False
        self._build_personnel_form(self.add_form)

        self.personnel_table = ctk.CTkScrollableFrame(tab, width=900, height=340)
        self.personnel_table.pack(fill="both", expand=True, padx=16, pady=(6, 16))
        self._refresh_personnel_table()

    def _toggle_add_form(self):
        self.add_form_visible = not self.add_form_visible
        if self.add_form_visible:
            self.add_form.pack(fill="x", padx=16, pady=(0, 10))
        else:
            self.add_form.pack_forget()

    def _build_personnel_form(self, container):
        labels = ["Ad Soyad", "Gorev", "Ucret Tipi", "Durum", "Notlar"]
        for idx, label in enumerate(labels):
            ctk.CTkLabel(container, text=f"{label}:").grid(row=idx, column=0, padx=12, pady=6, sticky="w")

        self.name_entry = ctk.CTkEntry(container, width=260)
        self.name_entry.grid(row=0, column=1, padx=12, pady=6, sticky="w")

        self.role_box = ctk.CTkComboBox(container, values=["Garson", "DJ", "Temizlik", "Teknik", "Koordinator"], width=220)
        self.role_box.set("Garson")
        self.role_box.grid(row=1, column=1, padx=12, pady=6, sticky="w")

        self.salary_box = ctk.CTkComboBox(container, values=["Gunluk", "Saatlik", "Aylik"], width=220)
        self.salary_box.set("Gunluk")
        self.salary_box.grid(row=2, column=1, padx=12, pady=6, sticky="w")

        self.status_box = ctk.CTkComboBox(container, values=["Aktif", "Pasif", "Izinli"], width=220)
        self.status_box.set("Aktif")
        self.status_box.grid(row=3, column=1, padx=12, pady=6, sticky="w")

        self.note_box = ctk.CTkTextbox(container, width=360, height=60)
        self.note_box.grid(row=4, column=1, padx=12, pady=6, sticky="w")

        ctk.CTkButton(
            container,
            text="Kaydet",
            fg_color="#2563EB",
            hover_color="#1E40AF",
            command=self._save_personnel,
        ).grid(row=5, column=1, pady=(10, 12), sticky="w")

    def _save_personnel(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Uyari", "Ad soyad alanini doldurun.")
            return

        record = {
            "name": name,
            "role": self.role_box.get(),
            "salary": self.salary_box.get(),
            "status": self.status_box.get(),
            "notes": self.note_box.get("1.0", "end").strip(),
        }
        self.personnel_data.append(record)
        self.name_entry.delete(0, "end")
        self.note_box.delete("1.0", "end")
        self._toggle_add_form()
        self._refresh_personnel_table()
        self._refresh_assignment_person_selector()
        self._refresh_attendance_table()
        self._refresh_reports()

    def _refresh_personnel_table(self):
        for widget in self.personnel_table.winfo_children():
            widget.destroy()

        headers = ["Ad Soyad", "Gorev", "Ucret Tipi", "Durum", "Notlar", "Islemler"]
        for col, header in enumerate(headers):
            ctk.CTkLabel(self.personnel_table, text=header, font=("Arial", 13, "bold")).grid(
                row=0, column=col, padx=10, pady=6, sticky="w"
            )

        if not self.personnel_data:
            ctk.CTkLabel(self.personnel_table, text="Kayitli personel bulunmuyor.", text_color="gray70").grid(
                row=1, column=0, columnspan=len(headers), pady=12
            )
            return

        for idx, record in enumerate(self.personnel_data, start=1):
            ctk.CTkLabel(self.personnel_table, text=record["name"]).grid(row=idx, column=0, padx=10, pady=4, sticky="w")
            ctk.CTkLabel(self.personnel_table, text=record["role"]).grid(row=idx, column=1, padx=10, pady=4, sticky="w")
            ctk.CTkLabel(self.personnel_table, text=record["salary"]).grid(row=idx, column=2, padx=10, pady=4, sticky="w")
            ctk.CTkLabel(self.personnel_table, text=record["status"]).grid(row=idx, column=3, padx=10, pady=4, sticky="w")
            note_preview = (record["notes"] or "-")[:80]
            ctk.CTkLabel(self.personnel_table, text=note_preview).grid(row=idx, column=4, padx=10, pady=4, sticky="w")

            btn_frame = ctk.CTkFrame(self.personnel_table, fg_color="transparent")
            btn_frame.grid(row=idx, column=5, padx=10, pady=4, sticky="w")

            ctk.CTkButton(
                btn_frame,
                text="Sil",
                width=60,
                fg_color="#DC2626",
                hover_color="#B91C1C",
                command=lambda i=idx - 1: self._remove_personnel(i),
            ).pack(side="left")

    def _remove_personnel(self, index: int):
        try:
            record = self.personnel_data[index]
        except IndexError:
            return
        name = record["name"]
        if not messagebox.askyesno("Onay", f"{name} kaydini silmek istiyor musunuz?"):
            return

        self.personnel_data.pop(index)
        self.assignment_data = [item for item in self.assignment_data if item["person"] != name]
        self.attendance_data.pop(name, None)
        self._refresh_personnel_table()
        self._refresh_assignment_person_selector()
        self._refresh_assignment_table()
        self._refresh_calendar()
        self._refresh_attendance_table()
        self._refresh_reports()

    # ------------------------------------------------------------------
    # Gorev atama
    # ------------------------------------------------------------------
    def _build_assignment_tab(self, tab):
        form = ctk.CTkFrame(tab, corner_radius=12)
        form.pack(fill="x", padx=18, pady=(18, 10))

        ctk.CTkLabel(form, text="Personel:", width=120).grid(row=0, column=0, padx=10, pady=8, sticky="e")
        self.assignment_person_box = ctk.CTkComboBox(form, values=[], width=220)
        self.assignment_person_box.grid(row=0, column=1, padx=10, pady=8, sticky="w")

        ctk.CTkLabel(form, text="Gorev Tarihi:", width=120).grid(row=0, column=2, padx=10, pady=8, sticky="e")
        self.assignment_date = DateEntry(form, date_pattern="yyyy-mm-dd", width=18)
        self.assignment_date.grid(row=0, column=3, padx=10, pady=8, sticky="w")

        ctk.CTkLabel(form, text="Gorev:", width=120).grid(row=1, column=0, padx=10, pady=8, sticky="e")
        self.assignment_task = ctk.CTkEntry(form, width=220)
        self.assignment_task.grid(row=1, column=1, padx=10, pady=8, sticky="w")

        ctk.CTkLabel(form, text="Not:", width=120).grid(row=1, column=2, padx=10, pady=8, sticky="e")
        self.assignment_note = ctk.CTkEntry(form, width=220)
        self.assignment_note.grid(row=1, column=3, padx=10, pady=8, sticky="w")

        ctk.CTkButton(
            form,
            text="Gorev Ata",
            width=140,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self._save_assignment,
        ).grid(row=2, column=3, padx=10, pady=(10, 12), sticky="e")

        self.assignment_table = ctk.CTkScrollableFrame(tab, width=900, height=330)
        self.assignment_table.pack(fill="both", expand=True, padx=18, pady=(0, 16))
        self._refresh_assignment_table()

    def _save_assignment(self):
        person = self.assignment_person_box.get().strip()
        if not person:
            messagebox.showwarning("Uyari", "Once personel secin.")
            return

        if person not in {item["name"] for item in self.personnel_data}:
            messagebox.showwarning("Uyari", "Secilen personel listede bulunmuyor.")
            return

        task = self.assignment_task.get().strip() or "Genel gorev"
        note = self.assignment_note.get().strip()
        self._assignment_id += 1
        record = {
            "id": self._assignment_id,
            "person": person,
            "task": task,
            "note": note,
            "date": self.assignment_date.get_date(),
        }
        self.assignment_data.append(record)
        self.assignment_task.delete(0, "end")
        self.assignment_note.delete(0, "end")
        self._refresh_assignment_table()
        self._refresh_calendar()
        self._refresh_reports()

    def _refresh_assignment_table(self):
        for widget in self.assignment_table.winfo_children():
            widget.destroy()

        headers = ["Tarih", "Personel", "Gorev", "Not", "Islemler"]
        for col, header in enumerate(headers):
            ctk.CTkLabel(self.assignment_table, text=header, font=("Arial", 13, "bold")).grid(
                row=0, column=col, padx=10, pady=6, sticky="w"
            )

        if not self.assignment_data:
            ctk.CTkLabel(self.assignment_table, text="Atanmis gorev bulunmuyor.", text_color="gray70").grid(
                row=1, column=0, columnspan=len(headers), pady=12
            )
            return

        sorted_data = sorted(self.assignment_data, key=lambda item: (item["date"], item["person"]))
        for idx, record in enumerate(sorted_data, start=1):
            ctk.CTkLabel(self.assignment_table, text=record["date"].isoformat()).grid(
                row=idx, column=0, padx=10, pady=4, sticky="w"
            )
            ctk.CTkLabel(self.assignment_table, text=record["person"]).grid(
                row=idx, column=1, padx=10, pady=4, sticky="w"
            )
            ctk.CTkLabel(self.assignment_table, text=record["task"]).grid(
                row=idx, column=2, padx=10, pady=4, sticky="w"
            )
            note = record["note"] or "-"
            ctk.CTkLabel(self.assignment_table, text=note).grid(row=idx, column=3, padx=10, pady=4, sticky="w")

            btn = ctk.CTkButton(
                self.assignment_table,
                text="Sil",
                width=60,
                fg_color="#DC2626",
                hover_color="#B91C1C",
                command=lambda assignment_id=record["id"]: self._remove_assignment(assignment_id),
            )
            btn.grid(row=idx, column=4, padx=10, pady=4, sticky="w")

    def _remove_assignment(self, assignment_id: int):
        self.assignment_data = [item for item in self.assignment_data if item["id"] != assignment_id]
        self._refresh_assignment_table()
        self._refresh_calendar()
        self._refresh_reports()

    def _refresh_assignment_person_selector(self):
        names = [item["name"] for item in self.personnel_data]
        if not names:
            self.assignment_person_box.configure(values=[])
            self.assignment_person_box.set("")
        else:
            self.assignment_person_box.configure(values=names)
            if self.assignment_person_box.get() not in names:
                self.assignment_person_box.set(names[0])

    # ------------------------------------------------------------------
    # Takvim gorunumu
    # ------------------------------------------------------------------
    def _build_calendar_tab(self, tab):
        controls = ctk.CTkFrame(tab, fg_color="transparent")
        controls.pack(fill="x", padx=18, pady=(18, 6))

        ctk.CTkButton(controls, text="<<", width=40, command=lambda: self._shift_calendar(-1)).pack(side="left")
        self.calendar_label = ctk.CTkLabel(
            controls, text=self._calendar_title(), font=("Arial", 16, "bold")
        )
        self.calendar_label.pack(side="left", padx=12)
        ctk.CTkButton(controls, text=">>", width=40, command=lambda: self._shift_calendar(1)).pack(side="left")

        self.calendar_frame = ctk.CTkFrame(tab)
        self.calendar_frame.pack(fill="both", expand=True, padx=18, pady=(6, 18))
        self.calendar_frame.grid_columnconfigure(tuple(range(7)), weight=1)
        self._refresh_calendar()

    def _shift_calendar(self, delta: int):
        month = self.calendar_month + delta
        year = self.calendar_year
        if month < 1:
            month = 12
            year -= 1
        elif month > 12:
            month = 1
            year += 1
        self.calendar_month = month
        self.calendar_year = year
        self.calendar_label.configure(text=self._calendar_title())
        self._refresh_calendar()

    def _calendar_title(self):
        return f"{calendar.month_name[self.calendar_month]} {self.calendar_year}"

    def _refresh_calendar(self):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        headers = ["Pzt", "Sal", "Car", "Per", "Cum", "Cmt", "Paz"]
        for col, label in enumerate(headers):
            ctk.CTkLabel(self.calendar_frame, text=label, font=("Arial", 12, "bold")).grid(
                row=0, column=col, padx=4, pady=4
            )

        cal = calendar.Calendar(firstweekday=0)
        month_days = list(cal.itermonthdates(self.calendar_year, self.calendar_month))
        grouped_assignments = defaultdict(list)
        for item in self.assignment_data:
            grouped_assignments[item["date"]].append(item)

        row = 1
        col = 0
        for day in month_days:
            cell = ctk.CTkFrame(self.calendar_frame, fg_color="#1F2937", corner_radius=8)
            cell.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")
            cell.grid_rowconfigure(1, weight=1)

            in_month = day.month == self.calendar_month
            day_label = ctk.CTkLabel(
                cell,
                text=str(day.day),
                text_color="white" if in_month else "gray70",
                font=("Arial", 14, "bold"),
            )
            day_label.pack(anchor="w", padx=8, pady=(6, 2))

            assignments = grouped_assignments.get(day, [])
            if assignments:
                for ass in assignments[:4]:
                    text = f"- {ass['person']} ({ass['task']})"
                    ctk.CTkLabel(cell, text=text, anchor="w", justify="left", wraplength=140).pack(
                        anchor="w", padx=8, pady=1
                    )
                if len(assignments) > 4:
                    ctk.CTkLabel(cell, text=f"+{len(assignments) - 4} diger", text_color="#F97316").pack(
                        anchor="w", padx=8, pady=1
                    )
            else:
                ctk.CTkLabel(cell, text="Gorev yok", text_color="gray60").pack(anchor="w", padx=8, pady=1)

            col += 1
            if col == 7:
                col = 0
                row += 1

    # ------------------------------------------------------------------
    # Yoklama tablosu
    # ------------------------------------------------------------------
    def _build_attendance_tab(self, tab):
        search = ctk.CTkFrame(tab, fg_color="transparent")
        search.pack(fill="x", padx=18, pady=(18, 6))

        ctk.CTkLabel(search, text="Personel ara:").pack(side="left")
        self.search_var = ctk.StringVar()
        ctk.CTkEntry(search, textvariable=self.search_var, width=220).pack(side="left", padx=8)
        ctk.CTkButton(search, text="Ara", width=80, command=self._refresh_attendance_table).pack(side="left")

        self.attendance_table = ctk.CTkScrollableFrame(tab, width=900, height=360)
        self.attendance_table.pack(fill="both", expand=True, padx=18, pady=(6, 18))
        self._refresh_attendance_table()

    def _refresh_attendance_table(self):
        for widget in self.attendance_table.winfo_children():
            widget.destroy()

        headers = ["Personel", "Durum", "Islemler"]
        for col, header in enumerate(headers):
            ctk.CTkLabel(self.attendance_table, text=header, font=("Arial", 13, "bold")).grid(
                row=0, column=col, padx=10, pady=6, sticky="w"
            )

        query = self.search_var.get().lower().strip() if hasattr(self, "search_var") else ""
        filtered = [item for item in self.personnel_data if query in item["name"].lower()]

        if not filtered:
            ctk.CTkLabel(self.attendance_table, text="Eslesen personel yok.", text_color="gray70").grid(
                row=1, column=0, columnspan=len(headers), pady=12
            )
            return

        for idx, record in enumerate(filtered, start=1):
            name = record["name"]
            status = self.attendance_data.get(name, "-")
            ctk.CTkLabel(self.attendance_table, text=name).grid(row=idx, column=0, padx=10, pady=4, sticky="w")
            ctk.CTkLabel(self.attendance_table, text=status).grid(row=idx, column=1, padx=10, pady=4, sticky="w")

            btn_frame = ctk.CTkFrame(self.attendance_table, fg_color="transparent")
            btn_frame.grid(row=idx, column=2, padx=10, pady=4, sticky="w")
            ctk.CTkButton(
                btn_frame,
                text="Geldi",
                width=80,
                fg_color="#16A34A",
                hover_color="#15803D",
                command=lambda n=name: self._set_attendance(n, True),
            ).pack(side="left", padx=4)
            ctk.CTkButton(
                btn_frame,
                text="Gelmedi",
                width=80,
                fg_color="#DC2626",
                hover_color="#B91C1C",
                command=lambda n=name: self._set_attendance(n, False),
            ).pack(side="left", padx=4)

    def _set_attendance(self, name: str, present: bool):
        self.attendance_data[name] = "Geldi" if present else "Gelmedi"
        self._refresh_attendance_table()
        self._refresh_reports()

    # ------------------------------------------------------------------
    # Ucret raporu
    # ------------------------------------------------------------------
    def _build_reports_tab(self, tab):
        top = ctk.CTkFrame(tab, fg_color="transparent")
        top.pack(fill="x", padx=18, pady=(18, 6))
        ctk.CTkLabel(top, text="Aylik Ucret Ozeti", font=("Arial", 16, "bold")).pack(side="left")
        ctk.CTkButton(top, text="Raporu Yenile", width=140, command=self._refresh_reports).pack(side="right")

        self.report_table = ctk.CTkScrollableFrame(tab, width=900, height=360)
        self.report_table.pack(fill="both", expand=True, padx=18, pady=(6, 18))
        self._refresh_reports()

    def _refresh_reports(self):
        if not hasattr(self, "report_table"):
            return

        for widget in self.report_table.winfo_children():
            widget.destroy()

        headers = ["Personel", "Gorev Sayisi", "Ucret Tipi", "Tahmini Tutar", "Yoklama"]
        for col, header in enumerate(headers):
            ctk.CTkLabel(self.report_table, text=header, font=("Arial", 13, "bold")).grid(
                row=0, column=col, padx=10, pady=6, sticky="w"
            )

        if not self.personnel_data:
            ctk.CTkLabel(self.report_table, text="Gosterilecek veri yok.", text_color="gray70").grid(
                row=1, column=0, columnspan=len(headers), pady=12
            )
            return

        assignments_by_person = defaultdict(int)
        for item in self.assignment_data:
            assignments_by_person[item["person"]] += 1

        for idx, record in enumerate(self.personnel_data, start=1):
            count = assignments_by_person.get(record["name"], 0)
            rate = self._estimate_rate(record["salary"])
            total = count * rate
            attendance = self.attendance_data.get(record["name"], "-")

            ctk.CTkLabel(self.report_table, text=record["name"]).grid(row=idx, column=0, padx=10, pady=4, sticky="w")
            ctk.CTkLabel(self.report_table, text=str(count)).grid(row=idx, column=1, padx=10, pady=4, sticky="w")
            ctk.CTkLabel(self.report_table, text=record["salary"]).grid(row=idx, column=2, padx=10, pady=4, sticky="w")
            ctk.CTkLabel(self.report_table, text=f"{total:.2f} TL").grid(row=idx, column=3, padx=10, pady=4, sticky="w")
            ctk.CTkLabel(self.report_table, text=attendance).grid(row=idx, column=4, padx=10, pady=4, sticky="w")

    @staticmethod
    def _estimate_rate(salary_type: str) -> float:
        rates = {"Gunluk": 1000.0, "Saatlik": 150.0, "Aylik": 25000.0}
        return rates.get(salary_type, 1000.0)

    # ------------------------------------------------------------------
    def _handle_back(self):
        if self.on_back:
            self.on_back()
