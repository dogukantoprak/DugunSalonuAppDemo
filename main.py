# main.py
import customtkinter as ctk
from ui.login_page import LoginPage
from ui.register_page import RegisterPage

# (Optional) import other pages later:
# from ui.dashboard_page import DashboardPage

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
        self.current_page = LoginPage(
            self,
            on_login=self.open_dashboard,
            on_register=self.show_register_page
        )
        self.current_page.pack(expand=True, fill="both")

    def show_register_page(self):
        """Display the registration page."""
        self.clear_current_page()
        self.current_page = RegisterPage(
            self,
            on_register_complete=lambda data: self.show_login_page(),
            on_back=self.show_login_page
        )
        self.current_page.pack(expand=True, fill="both")

    def open_dashboard(self, username):
        """When login is successful."""
        print(f"✅ Giriş yapan kullanıcı: {username}")
        # TODO: Replace with DashboardPage later
        # self.clear_current_page()
        # self.current_page = DashboardPage(self, username=username)
        # self.current_page.pack(expand=True, fill="both")

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
