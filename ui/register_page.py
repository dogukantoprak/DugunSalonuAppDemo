# ui/register_page.py
import customtkinter as ctk
from tkinter import messagebox
from controllers.user_controller import register_user  # ✅ backend function for saving user

class RegisterPage(ctk.CTkFrame):
    def __init__(self, master, on_register_complete=None, on_back=None):
        super().__init__(master)
        self.master = master
        self.on_register_complete = on_register_complete
        self.on_back = on_back

        # Sayfayı ortalamak için grid yapılandırması
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Ana form alanı (ortadaki çerçeve)
        form_frame = ctk.CTkFrame(self, corner_radius=12)
        form_frame.place(relx=0.5, rely=0.5, anchor="center")  # ✅ perfectly centered
        form_frame.grid_columnconfigure(0, weight=1)

        # Başlık
        title = ctk.CTkLabel(form_frame, text="Yeni Yönetici Kaydı", font=("Arial", 22, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=(20, 5))
        
        # --- Form Alanları ---
        self.name_entry = self.create_entry(form_frame, "Yönetici Adı", 1)
        self.email_entry = self.create_entry(form_frame, "E-posta", 2)
        self.phone1_entry = self.create_entry(form_frame, "Telefon 1", 3)
        self.phone2_entry = self.create_entry(form_frame, "Telefon 2 (Opsiyonel)", 4)
        self.address_entry = self.create_entry(form_frame, "Adres (Opsiyonel)", 5)
        self.city_entry = self.create_entry(form_frame, "İl", 6)
        self.district_entry = self.create_entry(form_frame, "İlçe", 7)
        self.username_entry = self.create_entry(form_frame, "Kullanıcı Adı", 8)
        self.password_entry = self.create_entry(form_frame, "Şifre", 9, show="*")

        # --- Butonlar ---
        register_button = ctk.CTkButton(form_frame, text="Kayıt Ol", width=200, command=self.handle_register)
        register_button.grid(row=10, column=0, columnspan=2, pady=(20, 5))

        back_button = ctk.CTkButton(form_frame, text="← Geri Dön", width=150, fg_color="gray20", command=self.handle_back)
        back_button.grid(row=11, column=0, columnspan=2, pady=(5, 20))

    # Ortak giriş alanı oluşturucu
    def create_entry(self, parent, placeholder, row, show=None):
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder, width=300, show=show)
        entry.grid(row=row, column=0, columnspan=2, pady=8, padx=20)
        return entry

    # Kayıt işlemi
    def handle_register(self):
        data = {
            "name": self.name_entry.get().strip(),
            "email": self.email_entry.get().strip(),
            "phone1": self.phone1_entry.get().strip(),
            "phone2": self.phone2_entry.get().strip(),  # Opsiyonel
            "address": self.address_entry.get().strip(),  # Opsiyonel
            "city": self.city_entry.get().strip(),
            "district": self.district_entry.get().strip(),
            "username": self.username_entry.get().strip(),
            "password": self.password_entry.get().strip()
        }

        # Zorunlu alanları kontrol et (phone2 ve address hariç)
        required_fields = {
            "name": "Yönetici Adı",
            "email": "E-posta", 
            "phone1": "Telefon 1",
            "city": "İl",
            "district": "İlçe",
            "username": "Kullanıcı Adı",
            "password": "Şifre"
        }
        
        missing_fields = [field_name for field, field_name in required_fields.items() if not data[field]]
        
        if missing_fields:
            messagebox.showwarning("Uyarı", f"Lütfen zorunlu alanları doldurun:\n• {chr(10).join(missing_fields)}")
            return

        # Email formatı kontrolü
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data["email"]):
            messagebox.showerror("Hata", "Geçerli bir email adresi girin!")
            return

        # Şifre uzunluk kontrolü
        if len(data["password"]) < 4:
            messagebox.showerror("Hata", "Şifre en az 4 karakter olmalı!")
            return

        # Kullanıcı adı uzunluk kontrolü
        if len(data["username"]) < 3:
            messagebox.showerror("Hata", "Kullanıcı adı en az 3 karakter olmalı!")
            return

        # Kullanıcı adı format kontrolü (sadece harf, rakam ve alt çizgi)
        if not re.match(r'^[a-zA-Z0-9_]+$', data["username"]):
            messagebox.showerror("Hata", "Kullanıcı adı sadece harf, rakam ve alt çizgi (_) içerebilir!")
            return

        success, message = register_user(data)  # ✅ Save to DB via controller

        if success:
            messagebox.showinfo("Başarılı", message)
            # Formu temizle
            self.clear_form()
            if self.on_register_complete:
                self.on_register_complete(data)
        else:
            messagebox.showerror("Hata", message)

    def clear_form(self):
        """Kayıt başarılı olduktan sonra formu temizle"""
        self.name_entry.delete(0, 'end')
        self.email_entry.delete(0, 'end')
        self.phone1_entry.delete(0, 'end')
        self.phone2_entry.delete(0, 'end')
        self.address_entry.delete(0, 'end')
        self.city_entry.delete(0, 'end')
        self.district_entry.delete(0, 'end')
        self.username_entry.delete(0, 'end')
        self.password_entry.delete(0, 'end')

    # Geri dönüş butonu
    def handle_back(self):
        if self.on_back:
            self.on_back()
