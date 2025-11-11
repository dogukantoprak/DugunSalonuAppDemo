from __future__ import annotations

import re
import tkinter as tk
from datetime import date, datetime
from typing import Callable

import customtkinter as ctk
from tkcalendar import Calendar


class CTkDatePicker(ctk.CTkFrame):
    """CustomTkinter-friendly date picker with calendar popup."""

    def __init__(
        self,
        master,
        width: int = 150,
        date_pattern: str = "yyyy-mm-dd",
        command: Callable[[date], None] | None = None,
        button_text: str = "...",
        **kwargs,
    ):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(master, **kwargs)

        self._command = command
        self._pattern = date_pattern
        self._strftime_pattern = self._build_strftime_pattern(date_pattern)
        self._selected_date: date = datetime.now().date()
        self._text_var = tk.StringVar()
        self._picker_window: ctk.CTkToplevel | None = None
        self._calendar: Calendar | None = None

        self.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(self, textvariable=self._text_var, width=width)
        self.entry.grid(row=0, column=0, sticky="nsew")
        self.entry.bind("<FocusOut>", self._handle_entry_focus_out, add="+")

        self.button = ctk.CTkButton(self, text=button_text, width=36, command=self._open_picker)
        self.button.grid(row=0, column=1, padx=(4, 0))

        self.set_date(self._selected_date)

    def bind(self, sequence: str | None = None, func: Callable | None = None, add: str | None = None):  # type: ignore[override]
        if sequence == "<<DateEntrySelected>>":
            normalized_add = add if add in ("+", True) else "+"
            return super().bind(sequence, func, normalized_add)
        return self.entry.bind(sequence, func, add)

    def get(self) -> str:
        return self._text_var.get()

    def get_date(self) -> date:
        return self._selected_date

    def set_date(self, value: date | datetime | str):
        target = self._normalize_to_date(value)
        self._apply_date(target, fire_event=False)

    def focus_set(self):
        self.entry.focus_set()

    def destroy(self):
        self._close_picker()
        super().destroy()

    def _open_picker(self):
        if self._picker_window and self._picker_window.winfo_exists():
            self._picker_window.focus_force()
            return

        self._picker_window = ctk.CTkToplevel(self)
        self._picker_window.title("Tarih Seç")
        self._picker_window.resizable(False, False)
        self._picker_window.transient(self.winfo_toplevel())
        self._picker_window.protocol("WM_DELETE_WINDOW", self._close_picker)

        if self._selected_date:
            initial = self._selected_date
        else:
            initial = datetime.now().date()

        self._calendar = Calendar(
            self._picker_window,
            selectmode="day",
            date_pattern=self._pattern,
            year=initial.year,
            month=initial.month,
            day=initial.day,
        )
        self._calendar.pack(padx=12, pady=12)
        self._calendar.bind("<<CalendarSelected>>", self._on_calendar_select)

        self._picker_window.grab_set()
        self._picker_window.after(10, lambda: self._place_picker_window())

    def _place_picker_window(self):
        if not self._picker_window or not self._picker_window.winfo_exists():
            return
        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        self._picker_window.geometry(f"+{x}+{y}")
        self._picker_window.focus_force()

    def _close_picker(self):
        if self._picker_window and self._picker_window.winfo_exists():
            try:
                self._picker_window.grab_release()
            except tk.TclError:
                pass
            self._picker_window.destroy()
        self._picker_window = None
        self._calendar = None

    def _on_calendar_select(self, _event=None):
        if not self._calendar:
            return
        selected = self._calendar.selection_get()
        self._apply_date(selected)
        self._close_picker()

    def _apply_date(self, selected: date, fire_event: bool = True):
        self._selected_date = selected
        self._text_var.set(self._format_date(selected))
        if fire_event:
            self.event_generate("<<DateEntrySelected>>")
            if self._command:
                self._command(self._selected_date)

    def _handle_entry_focus_out(self, _event=None):
        self._sync_entry_value()

    def _sync_entry_value(self):
        text = self._text_var.get().strip()
        if not text:
            # Keep last selected date visible
            self._text_var.set(self._format_date(self._selected_date))
            return

        try:
            parsed = datetime.strptime(text, self._strftime_pattern).date()
        except ValueError:
            self._text_var.set(self._format_date(self._selected_date))
            return

        self._selected_date = parsed

    def _normalize_to_date(self, value: date | datetime | str) -> date:
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        if isinstance(value, str) and value.strip():
            try:
                return datetime.strptime(value.strip(), self._strftime_pattern).date()
            except ValueError:
                pass
        return datetime.now().date()

    def _format_date(self, value: date) -> str:
        return datetime.combine(value, datetime.min.time()).strftime(self._strftime_pattern)

    @staticmethod
    def _build_strftime_pattern(pattern: str) -> str:
        replacements = {
            "yyyy": "%Y",
            "yy": "%y",
            "mm": "%m",
            "dd": "%d",
        }
        result = pattern
        for token, fmt in replacements.items():
            result = re.sub(token, fmt, result, flags=re.IGNORECASE)
        return result
