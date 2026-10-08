"""
Compact Pure-Logo Floating Action Dock (Full 5 Option Logos).
"""

import customtkinter as ctk
from PIL import ImageTk
from typing import Callable, Optional
from src.theme import THEMES, DEFAULT_THEME
from src.book_graphics import (
    generate_note_logo,
    generate_reminder_logo,
    generate_library_logo,
    generate_settings_logo,
    generate_tray_logo
)

TRANSPARENT_BG = "#010101"


class BookMenuOverlay(ctk.CTkToplevel):
    """
    Compact floating dock displaying all 5 interactive circular option logos:
    - 📝 Take Note
    - ⏰ Set Reminder
    - 📚 Library Hub
    - ⚙️ Settings & Themes
    - 📌 Minimize to Tray
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
        on_change_size: Optional[Callable] = None,
        current_size: int = 72,
        theme_name: str = DEFAULT_THEME
    ):
        super().__init__(master)
        self.on_take_note = on_take_note
        self.on_set_reminder = on_set_reminder
        self.on_open_dashboard = on_open_dashboard
        self.on_open_settings = on_open_settings
        self.on_hide_widget = on_hide_widget
        self.on_change_size = on_change_size
        self.current_size = current_size
        self.theme_name = theme_name
        self.theme = THEMES.get(theme_name, THEMES[DEFAULT_THEME])

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(fg_color=TRANSPARENT_BG)
        
        # Transparent background so ONLY the logos are visible
        try:
            self.wm_attributes("-transparentcolor", TRANSPARENT_BG)
        except Exception:
            pass

        self.logo_size = 38
        self.spacing = 6
        self.num_logos = 5

        # Compact dock dimensions
        dock_w = self.num_logos * (self.logo_size + self.spacing) + 14
        dock_h = self.logo_size + 24

        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        # Place compact dock adjacent to the book
        if anchor_x + current_size + dock_w < screen_w:
            pos_x = anchor_x + current_size + 6
        elif anchor_x - dock_w > 0:
            pos_x = anchor_x - dock_w - 6
        else:
            pos_x = max(6, min(screen_w - dock_w - 6, anchor_x - (dock_w - current_size) // 2))

        pos_y = anchor_y + (current_size - dock_h) // 2
        pos_y = max(6, min(screen_h - dock_h - 6, pos_y))

        self.geometry(f"{dock_w}x{dock_h}+{pos_x}+{pos_y}")

        # Keep image references alive
        self._img_refs = []

        self._build_ui()

        # Close when clicking away
        self.bind("<FocusOut>", self._on_focus_out)
        self.after(100, self.focus_force)

    def _build_ui(self):
        self.container = ctk.CTkFrame(self, fg_color=TRANSPARENT_BG)
        self.container.pack(fill="both", expand=True)

        # Logos Row
        logos_row = ctk.CTkFrame(self.container, fg_color=TRANSPARENT_BG)
        logos_row.pack(anchor="center", pady=(2, 0))

        # Compact Tooltip Indicator
        self.tooltip_lbl = ctk.CTkLabel(
            self.container,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=self.theme["book_accent"],
            fg_color=TRANSPARENT_BG,
            height=16
        )
        self.tooltip_lbl.pack(anchor="center", pady=(1, 0))

        # All 5 Options
        options = [
            ("Take Note", generate_note_logo, self._act_note),
            ("Set Reminder", generate_reminder_logo, self._act_reminder),
            ("Library Hub", generate_library_logo, self._act_dashboard),
            ("Settings & Theme", generate_settings_logo, self._act_settings),
            ("Minimize to Tray", generate_tray_logo, self._act_hide),
        ]

        for title, logo_fn, cmd in options:
            normal_pil = logo_fn(size=self.logo_size, theme_name=self.theme_name, is_hovered=False)
            hover_pil = logo_fn(size=self.logo_size, theme_name=self.theme_name, is_hovered=True)

            normal_tk = ImageTk.PhotoImage(normal_pil)
            hover_tk = ImageTk.PhotoImage(hover_pil)
            self._img_refs.extend([normal_tk, hover_tk])

            # Standalone Circular Logo Icon
            logo_btn = ctk.CTkLabel(
                logos_row,
                image=normal_tk,
                text="",
                cursor="hand2",
                fg_color=TRANSPARENT_BG
            )
            logo_btn.pack(side="left", padx=self.spacing // 2)

            # Hover handlers
            def on_enter(e, btn=logo_btn, h_img=hover_tk, text=title):
                btn.configure(image=h_img)
                self.tooltip_lbl.configure(text=f"✨ {text}")

            def on_leave(e, btn=logo_btn, n_img=normal_tk):
                btn.configure(image=n_img)
                self.tooltip_lbl.configure(text="")

            logo_btn.bind("<Enter>", on_enter)
            logo_btn.bind("<Leave>", on_leave)
            logo_btn.bind("<Button-1>", lambda e, c=cmd: c())

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
        if event.widget == self:
            self.destroy()
