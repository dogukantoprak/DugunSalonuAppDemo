# main.py
from datetime import datetime
import platform

import customtkinter as ctk
from controllers.reservation_controller import clear_reservation_cache
from ui.login_page import LoginPage
from ui.register_page import RegisterPage
from ui.reservation_form_page import ReservationFormPage
from ui.dashboard_page import DashboardPage
from ui.personnel_page import PersonnelPage
from ui.reservation_page import ReservationPage

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.current_page = None
        self.current_page_name: str | None = None
        self.logged_in_user: dict | None = None
        self.pages: dict[str, ctk.CTkFrame] = {}
        self.transient_pages = {"login", "register"}
        self.is_fullscreen = False
        self.previous_geometry: str | None = None
        self.fullscreen_strategy = (
            "zoomed" if platform.system().lower() == "windows" else "fullscreen"
        )

        self.title("Düğün Salonu Yönetim Sistemi")
        self.set_window_geometry(500, 600)
        self.resizable(False, False)

        self.bind("<Escape>", self._exit_fullscreen_shortcut)

        self.show_login_page()

    def set_window_geometry(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        if not self.is_fullscreen:
            self.geometry(f"{width}x{height}+{x}+{y}")

    def enter_fullscreen(self):
        if self.is_fullscreen:
            return
        self.previous_geometry = self.geometry()

        if self.fullscreen_strategy == "fullscreen":
            self.attributes("-fullscreen", True)
        else:
            self.attributes("-fullscreen", False)
            try:
                self.state("zoomed")
            except Exception:
                self.attributes("-zoomed", True)

        self.is_fullscreen = True

    def exit_fullscreen(self):
        if not self.is_fullscreen:
            return

        if self.fullscreen_strategy == "fullscreen":
            self.attributes("-fullscreen", False)
        else:
            try:
                self.state("normal")
            except Exception:
                self.attributes("-zoomed", False)

        if self.previous_geometry:
            self.geometry(self.previous_geometry)
        self.previous_geometry = None
        self.is_fullscreen = False

    def _exit_fullscreen_shortcut(self, _event=None):
        self.exit_fullscreen()

    def hide_current_page(self):
        if not self.current_page:
            return
        name = self.current_page_name
        on_hide = getattr(self.current_page, "on_hide", None)
        if callable(on_hide):
            try:
                on_hide()
            except Exception:
                pass
        if name in self.transient_pages:
            self.current_page.destroy()
        else:
            self.current_page.pack_forget()
        self.current_page = None
        self.current_page_name = None

    def show_login_page(self):
        """Display the login page."""
        self.hide_current_page()
        self.exit_fullscreen()
        self.set_window_geometry(500, 600)
        self.resizable(False, False)
        self.logged_in_user = None

        login_page = LoginPage(
            self,
            on_login=self.show_dashboard,
            on_register=self.show_register_page,
        )
        login_page.pack(expand=True, fill="both")
        self.current_page = login_page
        self.current_page_name = "login"

    def show_register_page(self):
        """Display the registration page."""
        self.hide_current_page()
        self.exit_fullscreen()
        self.set_window_geometry(520, 720)
        self.resizable(False, False)

        register_page = RegisterPage(
            self,
            on_register_complete=lambda data: self.show_login_page(),
            on_back=self.show_login_page,
        )
        register_page.pack(expand=True, fill="both")
        self.current_page = register_page
        self.current_page_name = "register"

    def show_dashboard(self, user: dict | None = None):
        """Render dashboard after successful login."""
        if user:
            self.logged_in_user = user

        if not self.logged_in_user:
            self.show_login_page()
            return

        print(f"✅ Giriş yapan kullanıcı: {self.logged_in_user.get('username')}")

        self.hide_current_page()
        self.enter_fullscreen()
        self.resizable(True, True)

        open_reservations = lambda date=None: self.show_reservation_page(date)

        dashboard = self.pages.get("dashboard")
        if dashboard is None:
            dashboard = DashboardPage(
                self,
                user=self.logged_in_user,
                on_logout=self.logout,
                on_open_reservations=open_reservations,
                on_open_personnel=self.show_personnel_page,
                on_open_reports=None,
                on_open_settings=None,
            )
            self.pages["dashboard"] = dashboard
        else:
            dashboard.on_logout = self.logout
            dashboard.on_open_reservations = open_reservations
            dashboard.on_open_personnel = self.show_personnel_page

        dashboard.update_user(self.logged_in_user)

        dashboard.pack(expand=True, fill="both")
        on_show = getattr(dashboard, "on_show", None)
        if callable(on_show):
            try:
                on_show()
            except Exception:
                pass
        self.current_page = dashboard
        self.current_page_name = "dashboard"

    def show_reservation_page(self, highlight_date: str | None = None):
        """Display the reservation calendar page."""
        self.hide_current_page()
        self.enter_fullscreen()
        self.resizable(True, True)

        back_target = self.show_dashboard if self.logged_in_user else self.show_login_page

        reservation_page = self.pages.get("reservation")
        if reservation_page is None:
            reservation_page = ReservationPage(self, on_back=back_target)
            self.pages["reservation"] = reservation_page
        else:
            reservation_page.on_back = back_target

        reservation_page.add_reservation = self.show_reservation_form
        reservation_page.pack(expand=True, fill="both")

        if highlight_date:
            reservation_page.mark_dirty()
            try:
                target = datetime.strptime(highlight_date, "%Y-%m-%d")
                reservation_page.current_date = datetime(target.year, target.month, 1)
                reservation_page.month_var.set(reservation_page.month_labels[target.month - 1])
                reservation_page.year_var.set(str(target.year))
                reservation_page.refresh_data(target_date=target.date().isoformat())
            except ValueError:
                reservation_page.refresh_data()
        else:
            if reservation_page.needs_refresh:
                reservation_page.refresh_data()

        self.current_page = reservation_page
        self.current_page_name = "reservation"

    def show_personnel_page(self):
        """Display the personnel management page."""
        self.hide_current_page()
        self.enter_fullscreen()
        self.resizable(True, True)

        back_target = self.show_dashboard if self.logged_in_user else self.show_login_page

        personnel_page = self.pages.get("personnel")
        if personnel_page is None:
            personnel_page = PersonnelPage(self, on_back=back_target)
            self.pages["personnel"] = personnel_page
        else:
            personnel_page.on_back = back_target

        personnel_page.pack(expand=True, fill="both")
        self.current_page = personnel_page
        self.current_page_name = "personnel"

    def show_reservation_form(self, default_date: str | None = None):
        """Open reservation form page."""
        self.hide_current_page()
        self.enter_fullscreen()
        self.resizable(True, True)

        def back_action():
            self.show_reservation_page(default_date)

        form_page = self.pages.get("reservation_form")
        if form_page is None:
            form_page = ReservationFormPage(
                self,
                on_back=back_action,
                on_saved=self.on_reservation_saved,
                default_date=default_date,
            )
            self.pages["reservation_form"] = form_page

        form_page.on_back = back_action
        form_page.on_saved = self.on_reservation_saved
        form_page.prepare(default_date)
        form_page.pack(expand=True, fill="both")
        self.current_page = form_page
        self.current_page_name = "reservation_form"

    def on_reservation_saved(self, info: dict | None):
        """Handle navigation after saving a reservation."""
        target_date = None
        if info:
            target_date = info.get("event_date")

        reservation_page = self.pages.get("reservation")
        if reservation_page:
            reservation_page.mark_dirty()

        dashboard = self.pages.get("dashboard")
        if dashboard:
            dashboard.mark_dirty()

        self.show_reservation_page(target_date)

    def logout(self):
        """Clear current session and return to login page."""
        self.hide_current_page()
        for name in ("dashboard", "reservation", "reservation_form", "personnel"):
            page = self.pages.pop(name, None)
            if page:
                page.destroy()
        self.logged_in_user = None
        clear_reservation_cache()
        self.show_login_page()


if __name__ == "__main__":
    # --- CustomTkinter setup ---
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # --- Run app ---
    app = App()
    app.mainloop()
