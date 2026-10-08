"""
Draggable, Always-On-Top Floating Book Widget.
"""

import customtkinter as ctk
from PIL import ImageTk
from typing import Callable, Optional
from src.database import Database
from src.theme import THEMES, DEFAULT_THEME, DEFAULT_OPACITY, DEFAULT_ICON_SIZE
from src.book_graphics import generate_book_image
from src.menu_overlay import BookMenuOverlay


class FloatingBookWidget(ctk.CTkToplevel):
    """
    A stylish floating Book widget that stays pinned above all other windows on Windows desktop.
    """
    def __init__(
        self,
        master,
        db: Database,
        on_take_note: Callable,
        on_set_reminder: Callable,
        on_open_dashboard: Callable,
        on_open_settings: Callable,
        on_hide: Callable
    ):
        super().__init__(master)
        self.db = db
        self.on_take_note = on_take_note
        self.on_set_reminder = on_set_reminder
        self.on_open_dashboard = on_open_dashboard
        self.on_open_settings = on_open_settings
        self.on_hide = on_hide

        self.theme_name = self.db.get_setting("theme", DEFAULT_THEME)
        self.theme = THEMES.get(self.theme_name, THEMES[DEFAULT_THEME])
        
        # Window attributes
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", float(self.db.get_setting("opacity", DEFAULT_OPACITY)))
        
        # Transparent background styling
        # Note: on Windows, we use a dark background matching the theme or transparent key
        self.configure(fg_color=self.theme["bg_primary"])
        try:
            self.wm_attributes("-transparentcolor", self.theme["bg_primary"])
        except Exception:
            pass

        self.widget_size = DEFAULT_ICON_SIZE + 16
        
        # Load saved position or default to top right
        screen_w = self.winfo_screenwidth()
        default_x = screen_w - self.widget_size - 40
        default_y = 120
        
        saved_x = int(self.db.get_setting("pos_x", default_x))
        saved_y = int(self.db.get_setting("pos_y", default_y))
        
        # Clamp to screen bounds
        saved_x = max(10, min(screen_w - self.widget_size - 10, saved_x))
        saved_y = max(10, min(self.winfo_screenheight() - self.widget_size - 10, saved_y))
        
        self.geometry(f"{self.widget_size}x{self.widget_size}+{saved_x}+{saved_y}")

        # Drag state variables
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._drag_occurred = False
        self.is_hovered = False

        self._load_icons()
        self._build_ui()
        self._bind_events()

    def _load_icons(self):
        # Generate normal and hover book states
        self.normal_pil = generate_book_image(
            size=DEFAULT_ICON_SIZE,
            theme_name=self.theme_name,
            is_hovered=False
        )
        self.hover_pil = generate_book_image(
            size=DEFAULT_ICON_SIZE,
            theme_name=self.theme_name,
            is_hovered=True
        )
        self.normal_img = ImageTk.PhotoImage(self.normal_pil)
        self.hover_img = ImageTk.PhotoImage(self.hover_pil)

    def _build_ui(self):
        self.container = ctk.CTkFrame(
            self,
            fg_color="transparent",
            width=self.widget_size,
            height=self.widget_size
        )
        self.container.pack(fill="both", expand=True)

        self.book_label = ctk.CTkLabel(
            self.container,
            image=self.normal_img,
            text="",
            cursor="hand2"
        )
        self.book_label.place(relx=0.5, rely=0.5, anchor="center")

    def _bind_events(self):
        # Dragging & Clicking on book
        for w in (self, self.container, self.book_label):
            w.bind("<ButtonPress-1>", self._on_press)
            w.bind("<B1-Motion>", self._on_drag)
            w.bind("<ButtonRelease-1>", self._on_release)
            w.bind("<Button-3>", self._on_right_click)  # Right click context
            w.bind("<Enter>", self._on_mouse_enter)
            w.bind("<Leave>", self._on_mouse_leave)

    def _on_mouse_enter(self, event):
        self.is_hovered = True
        self.book_label.configure(image=self.hover_img)
        self.attributes("-alpha", 1.0)  # Full opacity on hover

    def _on_mouse_leave(self, event):
        self.is_hovered = False
        self.book_label.configure(image=self.normal_img)
        self.attributes("-alpha", float(self.db.get_setting("opacity", DEFAULT_OPACITY)))

    def _on_press(self, event):
        self._drag_start_x = event.x_root
        self._drag_start_y = event.y_root
        self._drag_occurred = False

    def _on_drag(self, event):
        dx = event.x_root - self._drag_start_x
        dy = event.y_root - self._drag_start_y
        
        # If moved more than 4 pixels, consider it a drag
        if abs(dx) > 4 or abs(dy) > 4:
            self._drag_occurred = True
            
        cur_x = self.winfo_x() + dx
        cur_y = self.winfo_y() + dy
        self.geometry(f"+{cur_x}+{cur_y}")
        
        self._drag_start_x = event.x_root
        self._drag_start_y = event.y_root

    def _on_release(self, event):
        if self._drag_occurred:
            # Save new position to DB
            self.db.set_setting("pos_x", self.winfo_x())
            self.db.set_setting("pos_y", self.winfo_y())
        else:
            # Click detected -> Open Book Menu Overlay
            self._toggle_menu()

    def _toggle_menu(self):
        BookMenuOverlay(
            master=self,
            anchor_x=self.winfo_x(),
            anchor_y=self.winfo_y(),
            on_take_note=self.on_take_note,
            on_set_reminder=self.on_set_reminder,
            on_open_dashboard=self.on_open_dashboard,
            on_open_settings=self.on_open_settings,
            on_hide_widget=self.on_hide,
            theme_name=self.theme_name
        )

    def _on_right_click(self, event):
        # Quick direct right-click menu
        self._toggle_menu()

    def update_theme(self, theme_name: str):
        self.theme_name = theme_name
        self.theme = THEMES.get(theme_name, THEMES[DEFAULT_THEME])
        self.configure(fg_color=self.theme["bg_primary"])
        try:
            self.wm_attributes("-transparentcolor", self.theme["bg_primary"])
        except Exception:
            pass
        self._load_icons()
        self.book_label.configure(image=self.normal_img)

