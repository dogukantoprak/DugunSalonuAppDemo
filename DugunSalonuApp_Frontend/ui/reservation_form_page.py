from datetime import datetime

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

from DugunSalonuApp_Backend.controllers.reservation_controller import (
    create_reservation,
    get_unavailable_slots,
)
from .widgets import CTkDatePicker


class ReservationFormPage(ctk.CTkFrame):
    def __init__(self, master, on_back=None, on_saved=None, default_date=None):
        super().__init__(master)
        self.master = master
        self.on_back = on_back
        self.on_saved = on_saved
        self.default_date = default_date

        title = ctk.CTkLabel(self, text="📝 Yeni Rezervasyon Ekle", font=("Arial", 24, "bold"))
        title.pack(pady=(20, 10))

        # --- Sekmeler ---
        tabview = ctk.CTkTabview(self, width=900, height=450)
        tabview.pack(padx=20, pady=10, fill="both", expand=True)

        tab_res = tabview.add("Rezervasyon Bilgileri")
        tab_price = tabview.add("Fiyat Bilgileri")
        tab_menu = tabview.add("Menü Bilgileri")

        self.time_step_minutes = 15
        self.all_start_slots = self._build_time_slots(start_hour=10, end_hour=24, include_end=False)
        self.all_end_slots = self._build_time_slots(
            start_hour=10, end_hour=24, include_end=True, start_offset=self.time_step_minutes
        )
        self.slot_message = tk.StringVar()
        self.event_types = ["Düğün", "Nişan", "Kına", "Toplantı", "Mezuniyet", "Diğer"]
        self.salon_options = ["Salon A", "Salon B", "Salon C"]
        self.installment_options = [str(i) for i in range(1, 13)]
        self.payment_options = ["Nakit", "Kart", "Havale", "Çek"]
        self.menu_options = ["Klasik Menü", "Lüks Menü", "Özel Menü"]
        self.status_options = ["Ön Rezervasyon", "Kesin Rezervasyon"]

        self.build_reservation_tab(tab_res)
        self.build_price_tab(tab_price)
        self.build_menu_tab(tab_menu)
        self._setup_time_slot_watchers()
        self.prepare(default_date)

        # --- Alt Butonlar ---
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)

        ctk.CTkButton(btn_frame, text="🖨️ Sözleşme Yazdır", width=160, fg_color="#4B5563",
                      hover_color="#6B7280").grid(row=0, column=0, padx=8)
        ctk.CTkButton(btn_frame, text="📊 Excel’e Aktar", width=160, fg_color="#4B5563",
                      hover_color="#6B7280").grid(row=0, column=1, padx=8)
        ctk.CTkButton(btn_frame, text="💾 Kaydet", width=160, fg_color="#2563EB",
                      hover_color="#1E40AF", command=self.save_reservation).grid(row=0, column=2, padx=8)
        ctk.CTkButton(btn_frame, text="❌ Kapat", width=160, fg_color="gray20",
                      command=self.handle_back).grid(row=0, column=3, padx=8)

    # ====================================================
    # 🟠 SEKME 1: REZERVASYON BİLGİLERİ
    # ====================================================
    def build_reservation_tab(self, tab):
        tab.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Tarih
        ctk.CTkLabel(tab, text="Tarih:").grid(row=0, column=0, padx=20, pady=6, sticky="w")
        self.date_entry = CTkDatePicker(tab, width=160, date_pattern="dd/mm/yyyy", button_text="📅")
        self.date_entry.grid(row=0, column=1, padx=20, pady=6, sticky="w")

        # Başlama / Bitiş Saati
        ctk.CTkLabel(tab, text="Başlama Saati:").grid(row=1, column=0, padx=20, pady=6, sticky="w")
        self.start_time = ctk.CTkComboBox(
            tab,
            values=self.all_start_slots,
            width=150,
            command=self._on_start_time_change,
        )
        self.start_time.grid(row=1, column=1, padx=20, pady=6, sticky="w")

        ctk.CTkLabel(tab, text="Bitiş Saati:").grid(row=1, column=2, padx=20, pady=6, sticky="w")
        self.end_time = ctk.CTkComboBox(tab, values=self.all_end_slots, width=150)
        self.end_time.grid(row=1, column=3, padx=20, pady=6, sticky="w")

        ctk.CTkLabel(tab, textvariable=self.slot_message, text_color="#F97316").grid(
            row=2, column=0, columnspan=4, padx=20, pady=(0, 6), sticky="w"
        )

        # Etkinlik Türü
        ctk.CTkLabel(tab, text="Etkinlik Türü:").grid(row=3, column=0, padx=20, pady=6, sticky="w")
        self.type_box = ctk.CTkComboBox(tab, values=self.event_types)
        self.type_box.grid(row=3, column=1, padx=20, pady=6, sticky="w")

        # Davetli Sayısı
        ctk.CTkLabel(tab, text="Davetli Sayısı:").grid(row=3, column=2, padx=20, pady=6, sticky="w")
        self.guest_entry = ctk.CTkEntry(tab, width=120)
        self.guest_entry.grid(row=3, column=3, padx=20, pady=6, sticky="w")

        # Salon
        ctk.CTkLabel(tab, text="Salon Adı:").grid(row=4, column=0, padx=20, pady=6, sticky="w")
        self.salon_box = ctk.CTkComboBox(tab, values=self.salon_options, command=self._on_salon_change)
        self.salon_box.grid(row=4, column=1, padx=20, pady=6, sticky="w")

        # Kişisel Bilgiler
        ctk.CTkLabel(tab, text="Ad Soyad:").grid(row=5, column=0, padx=20, pady=6, sticky="w")
        self.name_entry = ctk.CTkEntry(tab, width=200)
        self.name_entry.grid(row=5, column=1, padx=20, pady=6, sticky="w")

        ctk.CTkLabel(tab, text="TC Kimlik:").grid(row=5, column=2, padx=20, pady=6, sticky="w")
        self.tc_entry = ctk.CTkEntry(tab, width=200)
        self.tc_entry.grid(row=5, column=3, padx=20, pady=6, sticky="w")

        ctk.CTkLabel(tab, text="Telefon:").grid(row=6, column=0, padx=20, pady=6, sticky="w")
        self.phone_entry = ctk.CTkEntry(tab, width=200)
        self.phone_entry.grid(row=6, column=1, padx=20, pady=6, sticky="w")

        ctk.CTkLabel(tab, text="Adres:").grid(row=7, column=0, padx=20, pady=6, sticky="nw")
        self.address_entry = ctk.CTkTextbox(tab, width=400, height=60)
        self.address_entry.grid(row=7, column=1, columnspan=3, padx=20, pady=6, sticky="w")

        # Sözleşme Bilgileri
        ctk.CTkLabel(tab, text="Sözleşme No:").grid(row=8, column=0, padx=20, pady=6, sticky="w")
        self.contract_no = ctk.CTkEntry(tab, width=120)
        self.contract_no.grid(row=8, column=1, padx=20, pady=6, sticky="w")

        ctk.CTkLabel(tab, text="Sözleşme Tarihi:").grid(row=8, column=2, padx=20, pady=6, sticky="w")
        self.contract_date = CTkDatePicker(tab, width=160, date_pattern="dd/mm/yyyy", button_text="📅")
        self.contract_date.grid(row=8, column=3, padx=20, pady=6, sticky="w")

        # Rezervasyon Türü
        ctk.CTkLabel(tab, text="Rezervasyon Durumu:").grid(row=9, column=0, padx=20, pady=6, sticky="w")
        self.status_box = ctk.CTkComboBox(tab, values=self.status_options, width=200)
        self.status_box.grid(row=9, column=1, padx=20, pady=6, sticky="w")

    # ====================================================
    # 🟡 SEKME 2: FİYAT BİLGİLERİ
    # ====================================================
    def build_price_tab(self, tab):
        tab.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkLabel(tab, text="Kişi Başı Etkinlik Ücreti:").grid(row=0, column=0, padx=20, pady=6, sticky="w")
        self.event_price = ctk.CTkEntry(tab, width=150)
        self.event_price.grid(row=0, column=1, padx=20, pady=6, sticky="w")

        ctk.CTkLabel(tab, text="Kişi Başı Menü Ücreti:").grid(row=0, column=2, padx=20, pady=6, sticky="w")
        self.menu_price = ctk.CTkEntry(tab, width=150)
        self.menu_price.grid(row=0, column=3, padx=20, pady=6, sticky="w")

        ctk.CTkLabel(tab, text="Kapora Yüzdesi:").grid(row=1, column=0, padx=20, pady=6, sticky="w")
        self.deposit_percent = ctk.CTkEntry(tab, width=80)
        self.deposit_percent.grid(row=1, column=1, padx=20, pady=6, sticky="w")

        ctk.CTkLabel(tab, text="Kapora Tutarı:").grid(row=1, column=2, padx=20, pady=6, sticky="w")
        self.deposit_amount = ctk.CTkEntry(tab, width=120)
        self.deposit_amount.grid(row=1, column=3, padx=20, pady=6, sticky="w")

        ctk.CTkLabel(tab, text="Taksit Sayısı:").grid(row=2, column=0, padx=20, pady=6, sticky="w")
        self.installments = ctk.CTkComboBox(tab, values=self.installment_options, width=80)
        self.installments.grid(row=2, column=1, padx=20, pady=6, sticky="w")

        ctk.CTkLabel(tab, text="Ödeme Türü:").grid(row=2, column=2, padx=20, pady=6, sticky="w")
        self.payment_type = ctk.CTkComboBox(tab, values=self.payment_options, width=120)
        self.payment_type.grid(row=2, column=3, padx=20, pady=6, sticky="w")

        # Tahsilat listesi (örnek placeholder)
        ctk.CTkLabel(tab, text="Tahsilatlar:").grid(row=3, column=0, padx=20, pady=6, sticky="nw")
        self.tahsilat_box = ctk.CTkTextbox(tab, width=500, height=120)
        self.tahsilat_box.grid(row=3, column=1, columnspan=3, padx=20, pady=6, sticky="w")

        ctk.CTkButton(tab, text="+ Tahsilat Ekle", width=150, fg_color="#10B981", hover_color="#059669").grid(
            row=4, column=3, padx=20, pady=10, sticky="e")

    # ====================================================
    # 🟢 SEKME 3: MENÜ BİLGİLERİ
    # ====================================================
    def build_menu_tab(self, tab):
        tab.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(tab, text="Menü Seçimi:").grid(row=0, column=0, padx=20, pady=6, sticky="w")
        self.menu_box = ctk.CTkComboBox(tab, values=self.menu_options, width=200)
        self.menu_box.grid(row=0, column=1, padx=20, pady=6, sticky="w")

        ctk.CTkLabel(tab, text="Menü Detayı:").grid(row=1, column=0, padx=20, pady=6, sticky="nw")
        self.menu_detail = ctk.CTkTextbox(tab, width=400, height=100)
        self.menu_detail.grid(row=1, column=1, padx=20, pady=6, sticky="w")

        ctk.CTkLabel(tab, text="Özel İstekler:").grid(row=2, column=0, padx=20, pady=6, sticky="nw")
        self.special_request = ctk.CTkTextbox(tab, width=400, height=100)
        self.special_request.grid(row=2, column=1, padx=20, pady=6, sticky="w")

    # ====================================================
    # 🔵 KAYDET VE GERİ DÖN
    # ====================================================
    def _build_time_slots(self, start_hour: int, end_hour: int, include_end: bool, start_offset: int = 0) -> list[str]:
        start_minutes = start_hour * 60 + start_offset
        end_minutes = end_hour * 60
        slots: list[str] = []
        current = start_minutes
        while current < end_minutes:
            slots.append(self._minutes_to_time(current))
            current += self.time_step_minutes
        if include_end and current == end_minutes:
            slots.append(self._minutes_to_time(current))
        return slots

    def _setup_time_slot_watchers(self):
        self.date_entry.bind("<<DateEntrySelected>>", self._on_date_change)
        self.date_entry.bind("<FocusOut>", self._on_date_change)

    def _on_date_change(self, _event=None):
        self._update_time_slots()

    def _on_salon_change(self, _value):
        self._update_time_slots()

    def _on_start_time_change(self, value):
        self._update_end_time_options(value)

    def _update_time_slots(self):
        date_value = self.date_entry.get()
        salon_value = self.salon_box.get()

        if not date_value or not salon_value:
            self._apply_start_time_values(self.all_start_slots, enable=True)
            self._set_slot_message("Salon ve tarih seçimi yaptıktan sonra uygun 15 dakikalık saatleri görebilirsiniz.")
            return

        try:
            slot_data = get_unavailable_slots(date_value, salon_value)
        except ValueError as exc:
            self._apply_start_time_values(self.all_start_slots, enable=True)
            self._set_slot_message(str(exc))
            return

        blocked = slot_data.get("blocked", [])
        busy_ranges = slot_data.get("ranges", [])
        available = [slot for slot in self.all_start_slots if slot not in blocked]
        if available:
            self._apply_start_time_values(available, enable=True)
            if busy_ranges:
                self._set_slot_message(f"Dolu saat aralıkları: {', '.join(busy_ranges)}")
            else:
                self._set_slot_message("")
        else:
            self._apply_start_time_values([], enable=False)
            self._set_slot_message(f"{salon_value} salonunda seçilen tarih için uygun saat bulunmuyor.")

        self._update_end_time_options(self.start_time.get())

    def _apply_start_time_values(self, values: list[str], enable: bool):
        display_values = values if values else ["—"]
        self.start_time.configure(values=display_values, state="normal" if enable else "disabled")

        current_value = self.start_time.get()
        if current_value not in display_values:
            if enable and display_values:
                self.start_time.set(display_values[0])
            elif not enable:
                self.start_time.set("—")
            else:
                self.start_time.set("")

    def _update_end_time_options(self, start_value: str | None):
        if not start_value or start_value == "—":
            self.end_time.configure(values=self.all_end_slots, state="normal")
            if self.end_time.get() not in self.all_end_slots:
                self.end_time.set(self.all_end_slots[0])
            return

        start_minutes = self._time_to_minutes(start_value)
        end_options = [slot for slot in self.all_end_slots if self._time_to_minutes(slot) > start_minutes]
        if not end_options:
            end_options = self.all_end_slots
        self.end_time.configure(values=end_options, state="normal")
        if self.end_time.get() not in end_options:
            self.end_time.set(end_options[0])

    def _set_slot_message(self, message: str):
        self.slot_message.set(message)

    @staticmethod
    def _time_to_minutes(value: str) -> int:
        hour, minute = value.split(":")
        return int(hour) * 60 + int(minute)

    @staticmethod
    def _minutes_to_time(total_minutes: int) -> str:
        hour = total_minutes // 60
        minute = total_minutes % 60
        return f"{hour:02d}:{minute:02d}"

    def save_reservation(self):
        form_data = {
            "event_date": self.date_entry.get(),
            "start_time": self.start_time.get(),
            "end_time": self.end_time.get(),
            "event_type": self.type_box.get(),
            "guests": self.guest_entry.get(),
            "salon": self.salon_box.get(),
            "client_name": self.name_entry.get(),
            "tc_identity": self.tc_entry.get(),
            "phone": self.phone_entry.get(),
            "address": self.address_entry.get("1.0", tk.END),
            "contract_no": self.contract_no.get(),
            "contract_date": self.contract_date.get(),
            "status": self.status_box.get(),
            "event_price": self.event_price.get(),
            "menu_price": self.menu_price.get(),
            "deposit_percent": self.deposit_percent.get(),
            "deposit_amount": self.deposit_amount.get(),
            "installments": self.installments.get(),
            "payment_type": self.payment_type.get(),
            "tahsilatlar": self.tahsilat_box.get("1.0", tk.END),
            "menu_name": self.menu_box.get(),
            "menu_detail": self.menu_detail.get("1.0", tk.END),
            "special_request": self.special_request.get("1.0", tk.END),
        }

        success, message, info = create_reservation(form_data)
        if success:
            messagebox.showinfo("Başarılı", message)
            if self.on_saved:
                self.on_saved(info)
            else:
                self.handle_back()
        else:
            messagebox.showerror("Hata", message)

    def handle_back(self):
        if self.on_back:
            self.on_back()

    def prepare(self, default_date=None):
        self.default_date = default_date

        target_date = datetime.now()
        if default_date:
            try:
                target_date = datetime.strptime(default_date, "%Y-%m-%d")
            except ValueError:
                target_date = datetime.now()

        self.date_entry.set_date(target_date)
        self.contract_date.set_date(target_date)

        for entry in (
            self.guest_entry,
            self.name_entry,
            self.tc_entry,
            self.phone_entry,
            self.contract_no,
            self.event_price,
            self.menu_price,
            self.deposit_percent,
            self.deposit_amount,
        ):
            entry.delete(0, tk.END)

        self.address_entry.delete("1.0", tk.END)
        self.tahsilat_box.delete("1.0", tk.END)
        self.menu_detail.delete("1.0", tk.END)
        self.special_request.delete("1.0", tk.END)

        self.type_box.set(self.event_types[0] if self.event_types else "")
        self.salon_box.set(self.salon_options[0] if self.salon_options else "")
        self.status_box.set(self.status_options[0] if self.status_options else "")
        self.installments.set(self.installment_options[0] if self.installment_options else "")
        self.payment_type.set(self.payment_options[0] if self.payment_options else "")
        self.menu_box.set(self.menu_options[0] if self.menu_options else "")

        self.start_time.set("")
        if self.all_end_slots:
            self.end_time.set(self.all_end_slots[0])
        else:
            self.end_time.set("")

        self.slot_message.set("")
        self._update_time_slots()
        self._update_end_time_options(self.start_time.get())
