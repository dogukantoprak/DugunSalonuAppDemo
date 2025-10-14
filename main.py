# main.py
from datetime import datetime

import customtkinter as ctk
from ui.login_page import LoginPage
from ui.register_page import RegisterPage
from ui.reservation_form_page import ReservationFormPage
from ui.reservation_page import ReservationPage

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window setup ---
        self.title("Düğün Salonu Yönetim Sistemi")
        self.set_window_geometry(500, 600)
        self.resizable(False, False)

        # --- Page management ---
        self.current_page = None
        self.show_login_page()

    # --- Utility: center window ---
    def set_window_geometry(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    # --- Page switching functions ---
    def show_login_page(self):
        """Display the login page."""
        self.clear_current_page()
        self.set_window_geometry(500, 600)
        self.resizable(False, False)
        self.current_page = LoginPage(
            self,
            on_login=self.open_dashboard,
            on_register=self.show_register_page
        )
        self.current_page.pack(expand=True, fill="both")

    def show_register_page(self):
        """Display the registration page."""
        self.clear_current_page()
        self.set_window_geometry(520, 720)
        self.resizable(False, False)
        self.current_page = RegisterPage(
            self,
            on_register_complete=lambda data: self.show_login_page(),
            on_back=self.show_login_page
        )
        self.current_page.pack(expand=True, fill="both")

    def open_dashboard(self, username):
        """When login is successful."""
        print(f"✅ Giriş yapan kullanıcı: {username}")
        self.show_reservation_page()

    def show_reservation_page(self, highlight_date: str | None = None):
        """Temporary navigation to reservation calendar until dashboard is ready."""
        self.clear_current_page()
        self.set_window_geometry(1100, 780)
        self.resizable(True, True)

        reservation_page = ReservationPage(self, on_back=self.show_login_page)
        reservation_page.add_reservation = self.show_reservation_form
        self.current_page = reservation_page
        reservation_page.pack(expand=True, fill="both")

        if highlight_date:
            try:
                target = datetime.strptime(highlight_date, "%Y-%m-%d")
                reservation_page.current_date = datetime(target.year, target.month, 1)
                reservation_page.month_var.set(reservation_page.month_labels[target.month - 1])
                reservation_page.year_var.set(str(target.year))
                reservation_page.refresh_data(target_date=target.date().isoformat())
            except ValueError:
                reservation_page.refresh_data()
        else:
            reservation_page.refresh_data()

    def show_reservation_form(self, default_date: str | None = None):
        """Open reservation form page."""
        self.clear_current_page()
        self.set_window_geometry(960, 760)
        self.resizable(True, True)

        form_page = ReservationFormPage(
            self,
            on_back=lambda: self.show_reservation_page(default_date),
            on_saved=self.on_reservation_saved,
            default_date=default_date,
        )
        self.current_page = form_page
        form_page.pack(expand=True, fill="both")

    def on_reservation_saved(self, info: dict | None):
        """Handle navigation after saving a reservation."""
        target_date = None
        if info:
            target_date = info.get("event_date")
        self.show_reservation_page(target_date)

    # --- Utility: clear current frame before showing new one ---
    def clear_current_page(self):
        if self.current_page:
            self.current_page.destroy()
            self.current_page = None


if __name__ == "__main__":
    # --- CustomTkinter setup ---
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # --- Run app ---
    app = App()
    app.mainloop()
