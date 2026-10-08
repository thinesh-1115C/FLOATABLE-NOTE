"""
Main Application Entry Point for the Book-Shaped Notes & Reminders Desktop App.
"""

import sys
import threading
import customtkinter as ctk
import pystray
from PIL import Image
from src.database import Database
from src.theme import DEFAULT_THEME, THEMES
from src.book_graphics import generate_book_image
from src.floating_widget import FloatingBookWidget
from src.notes_window import NotesWindow
from src.reminder_window import ReminderWindow
from src.dashboard_window import DashboardWindow
from src.alarm_manager import AlarmService


class BookApp:
    """
    Main application coordinator managing the floating book widget,
    popups, background reminder alarm service, and system tray icon.
    """
    def __init__(self):
        # Set customtkinter appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Hidden root window
        self.root = ctk.CTk()
        self.root.withdraw()

        self.db = Database()
        self.theme_name = self.db.get_setting("theme", DEFAULT_THEME)

        # Active window references
        self.widget = None
        self.notes_win = None
        self.reminder_win = None
        self.dashboard_win = None
        self.tray_icon = None

        # Start background alarm service
        self.alarm_service = AlarmService(
            root=self.root,
            db=self.db,
            on_status_change=self._on_reminder_status_change
        )
        self.alarm_service.start()

        # Create the floating book widget
        self._init_floating_widget()

        # Setup system tray icon in background thread
        self._init_tray_icon()

    def _init_floating_widget(self):
        if self.widget:
            try:
                self.widget.destroy()
            except Exception:
                pass

        self.widget = FloatingBookWidget(
            master=self.root,
            db=self.db,
            on_take_note=self.open_notes,
            on_set_reminder=self.open_reminder,
            on_open_dashboard=self.open_dashboard,
            on_open_settings=lambda: self.open_dashboard(initial_tab="settings"),
            on_hide=self.hide_widget
        )

    def _init_tray_icon(self):
        icon_pil = generate_book_image(size=64, theme_name=self.theme_name)
        
        menu = pystray.Menu(
            pystray.MenuItem("📖 Show/Hide Book", self.toggle_widget, default=True),
            pystray.MenuItem("📝 Take Quick Note", lambda: self.root.after(0, self.open_notes)),
            pystray.MenuItem("⏰ Set Reminder", lambda: self.root.after(0, self.open_reminder)),
            pystray.MenuItem("📚 Open Library Hub", lambda: self.root.after(0, self.open_dashboard)),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("🚪 Exit App", self.quit_app)
        )

        self.tray_icon = pystray.Icon("BookNotesApp", icon_pil, "Book Notes & Reminders", menu)
        threading.Thread(target=self.tray_icon.run, daemon=True).start()

    def toggle_widget(self, icon=None, item=None):
        if self.widget and self.widget.winfo_exists():
            if self.widget.winfo_viewable():
                self.root.after(0, self.widget.withdraw)
            else:
                self.root.after(0, self.widget.deiconify)
        else:
            self.root.after(0, self._init_floating_widget)

    def hide_widget(self):
        if self.widget and self.widget.winfo_exists():
            self.widget.withdraw()

    def show_widget(self):
        if self.widget and self.widget.winfo_exists():
            self.widget.deiconify()

    def open_notes(self):
        if self.notes_win and self.notes_win.winfo_exists():
            self.notes_win.lift()
            self.notes_win.focus_force()
        else:
            self.notes_win = NotesWindow(
                master=self.root,
                db=self.db,
                on_saved=self._on_note_saved,
                theme_name=self.theme_name
            )

    def open_reminder(self):
        if self.reminder_win and self.reminder_win.winfo_exists():
            self.reminder_win.lift()
            self.reminder_win.focus_force()
        else:
            self.reminder_win = ReminderWindow(
                master=self.root,
                db=self.db,
                on_saved=self._on_reminder_saved,
                theme_name=self.theme_name
            )

    def open_dashboard(self, initial_tab: str = "notes"):
        if self.dashboard_win and self.dashboard_win.winfo_exists():
            self.dashboard_win.lift()
            self.dashboard_win.focus_force()
            if initial_tab == "settings":
                self.dashboard_win._show_settings_tab()
        else:
            self.dashboard_win = DashboardWindow(
                master=self.root,
                db=self.db,
                on_theme_changed=self._on_theme_changed,
                on_change_size=self._on_widget_size_changed,
                theme_name=self.theme_name
            )
            if initial_tab == "settings":
                self.dashboard_win._show_settings_tab()

    def _on_widget_size_changed(self, new_size: int):
        if self.widget and self.widget.winfo_exists():
            self.widget.set_icon_size(new_size)

    def _on_theme_changed(self, new_theme: str):
        self.theme_name = new_theme
        if self.widget and self.widget.winfo_exists():
            self.widget.update_theme(new_theme)
        if self.tray_icon:
            try:
                self.tray_icon.icon = generate_book_image(size=64, theme_name=new_theme)
            except Exception:
                pass

    def _on_note_saved(self):
        if self.dashboard_win and self.dashboard_win.winfo_exists():
            self.dashboard_win._refresh_content()

    def _on_reminder_saved(self):
        if self.dashboard_win and self.dashboard_win.winfo_exists():
            self.dashboard_win._refresh_content()

    def _on_reminder_status_change(self):
        if self.dashboard_win and self.dashboard_win.winfo_exists():
            self.dashboard_win._refresh_content()

    def quit_app(self, icon=None, item=None):
        self.alarm_service.stop()
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.after(0, self.root.destroy)
        sys.exit(0)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = BookApp()
    app.run()

