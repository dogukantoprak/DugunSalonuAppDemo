# ui/login_page.py
import customtkinter as ctk
from tkinter import messagebox
from controllers.user_controller import login_user

class LoginPage(ctk.CTkFrame):
    def __init__(self, master, on_login=None, on_register=None, on_forgot_password=None):
        super().__init__(master)
        self.master = master
        self.on_login = on_login
        self.on_register = on_register
        self.on_forgot_password = on_forgot_password

        # Frame yapılandırma - Ana frame'in tüm alanı kullanmasını sağla
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Form alanı - Responsive boyutlandırma
        form_frame = ctk.CTkFrame(self)
        form_frame.grid(row=0, column=0, sticky="nsew", padx=40, pady=50)
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=1)

        # Başlık - Daha iyi spacing
        title = ctk.CTkLabel(form_frame, text="Düğün Salonu Yönetim Girişi", font=("Arial", 24, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=(30, 20), sticky="ew")

        # Kullanıcı Adı - Daha geniş ve responsive
        self.username_entry = ctk.CTkEntry(form_frame, placeholder_text="Kullanıcı Adı", width=300, height=40)
        self.username_entry.grid(row=1, column=0, columnspan=2, pady=(20, 15), padx=30, sticky="ew")

        # Şifre - Daha geniş ve responsive
        self.password_entry = ctk.CTkEntry(form_frame, placeholder_text="Parola", show="*", width=300, height=40)
        self.password_entry.grid(row=2, column=0, columnspan=2, pady=15, padx=30, sticky="ew")

        # Giriş Butonu - Daha büyük ve belirgin
        login_button = ctk.CTkButton(form_frame, text="Giriş Yap", width=250, height=45, 
                                   font=("Arial", 16, "bold"), command=self.handle_login)
        login_button.grid(row=3, column=0, columnspan=2, pady=(25, 20), padx=30, sticky="ew")

        # Alt Butonlar - Daha iyi hizalama ve boyutlandırma
        register_button = ctk.CTkButton(form_frame, text="Kayıt Ol", fg_color="gray30", width=140, height=35,
                                        command=self.handle_register)
        register_button.grid(row=4, column=0, pady=(10, 30), padx=(30, 10), sticky="ew")

        forgot_button = ctk.CTkButton(form_frame, text="Şifremi Unuttum", fg_color="gray30", width=140, height=35,
                                      command=self.handle_forgot)
        forgot_button.grid(row=4, column=1, pady=(10, 30), padx=(10, 30), sticky="ew")

        # Klavye navigasyonu
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self.handle_login())
        
        # İlk odağı kullanıcı adı alanına ver
        self.username_entry.focus()

    # --- Buton İşlemleri ---
    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Uyarı", "Lütfen kullanıcı adı ve şifre girin.")
            return

        success, message, user = login_user(username, password)

        if success:
            messagebox.showinfo("Başarılı", message)
            if self.on_login:
                self.on_login(user)
        else:
            messagebox.showerror("Hata", message)

    def handle_register(self):
        if self.on_register:
            self.on_register()

    def handle_forgot(self):
        if self.on_forgot_password:
            self.on_forgot_password()
