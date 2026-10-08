"""
Popup Options Menu anchored adjacent to the Floating Book Widget.
"""

import customtkinter as ctk
from PIL import ImageTk
from typing import Callable, Optional
from src.theme import THEMES, DEFAULT_THEME
from src.book_graphics import generate_book_image


class BookMenuOverlay(ctk.CTkToplevel):
    """
    Sleek, book-ribbon styled popup menu displayed upon clicking the floating book.
    """
    def __init__(
        self,
        master,
        anchor_x: int,
        anchor_y: int,
        on_take_note: Callable,
        on_set_reminder: Callable,
        on_open_dashboard: Callable,
        on_open_settings: Callable,
        on_hide_widget: Callable,
        theme_name: str = DEFAULT_THEME
    ):
        super().__init__(master)
        self.on_take_note = on_take_note
        self.on_set_reminder = on_set_reminder
        self.on_open_dashboard = on_open_dashboard
        self.on_open_settings = on_open_settings
        self.on_hide_widget = on_hide_widget
        self.theme_name = theme_name
        self.theme = THEMES.get(theme_name, THEMES[DEFAULT_THEME])

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(fg_color=self.theme["bg_primary"])

        # Calculate coordinates ensuring it stays on-screen
        menu_w = 260
        menu_h = 320
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        pos_x = anchor_x + 85
        if pos_x + menu_w > screen_w:
            pos_x = anchor_x - menu_w - 10
        pos_y = anchor_y
        if pos_y + menu_h > screen_h:
            pos_y = screen_h - menu_h - 20
        if pos_y < 10:
            pos_y = 10

        self.geometry(f"{menu_w}x{menu_h}+{pos_x}+{pos_y}")
        self._build_ui()

        # Close when focus is lost
        self.bind("<FocusOut>", self._on_focus_out)
        self.after(100, self.focus_force)

    def _build_ui(self):
        # Card Container with Gold/Accent Border
        container = ctk.CTkFrame(
            self,
            fg_color=self.theme["bg_secondary"],
            corner_radius=14,
            border_width=2,
            border_color=self.theme["book_accent"]
        )
        container.pack(fill="both", expand=True, padx=2, pady=2)

        # Header Title
        header = ctk.CTkFrame(container, fg_color=self.theme["bg_card"], corner_radius=10)
        header.pack(fill="x", padx=10, pady=(10, 8))

        title_lbl = ctk.CTkLabel(
            header,
            text="📖 BOOK OPTIONS",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=self.theme["book_accent"]
        )
        title_lbl.pack(side="left", padx=10, pady=6)

        close_btn = ctk.CTkButton(
            header,
            text="✕",
            width=24,
            height=24,
            fg_color="transparent",
            hover_color=self.theme["danger"],
            text_color=self.theme["text_secondary"],
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.destroy
        )
        close_btn.pack(side="right", padx=6, pady=4)

        # Option Items
        options = [
            ("📝", "Take Quick Note", "Capture ideas in journal", self._act_note),
            ("⏰", "Set Reminder", "Planner alert & countdown", self._act_reminder),
            ("📚", "Library Dashboard", "Search all notes & alarms", self._act_dashboard),
            ("⚙️", "Settings & Theme", "Customize book cover", self._act_settings),
            ("📌", "Minimize to Tray", "Keep running in background", self._act_hide),
        ]

        for icon, title, subtitle, cmd in options:
            btn_frame = ctk.CTkFrame(
                container,
                fg_color=self.theme["bg_primary"],
                corner_radius=8,
                cursor="hand2"
            )
            btn_frame.pack(fill="x", padx=10, pady=3)

            # Left Icon
            icon_lbl = ctk.CTkLabel(
                btn_frame,
                text=icon,
                font=ctk.CTkFont(size=16),
                width=32
            )
            icon_lbl.pack(side="left", padx=(8, 4), pady=4)

            # Text Info
            text_box = ctk.CTkFrame(btn_frame, fg_color="transparent")
            text_box.pack(side="left", fill="both", expand=True, pady=4)

            t_lbl = ctk.CTkLabel(
                text_box,
                text=title,
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color=self.theme["text_primary"],
                anchor="w"
            )
            t_lbl.pack(anchor="w")

            s_lbl = ctk.CTkLabel(
                text_box,
                text=subtitle,
                font=ctk.CTkFont(family="Segoe UI", size=10),
                text_color=self.theme["text_secondary"],
                anchor="w"
            )
            s_lbl.pack(anchor="w")

            # Bind click events
            for widget in (btn_frame, icon_lbl, text_box, t_lbl, s_lbl):
                widget.bind("<Button-1>", lambda e, c=cmd: c())
                widget.bind("<Enter>", lambda e, f=btn_frame: f.configure(fg_color=self.theme["bg_card"]))
                widget.bind("<Leave>", lambda e, f=btn_frame: f.configure(fg_color=self.theme["bg_primary"]))

    def _act_note(self):
        self.destroy()
        self.on_take_note()

    def _act_reminder(self):
        self.destroy()
        self.on_set_reminder()

    def _act_dashboard(self):
        self.destroy()
        self.on_open_dashboard()

    def _act_settings(self):
        self.destroy()
        self.on_open_settings()

    def _act_hide(self):
        self.destroy()
        self.on_hide_widget()

    def _on_focus_out(self, event):
        # Close when clicking away
        if event.widget == self:
            self.destroy()

