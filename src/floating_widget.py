"""
Draggable, Resizable, Always-On-Top Floating Book Widget.
"""

import time
import customtkinter as ctk
from PIL import ImageTk
from typing import Callable, Optional
from src.database import Database
from src.theme import THEMES, DEFAULT_THEME, DEFAULT_OPACITY, DEFAULT_ICON_SIZE
from src.book_graphics import generate_book_image
from src.menu_overlay import BookMenuOverlay

MIN_ICON_SIZE = 40
MAX_ICON_SIZE = 160


class FloatingBookWidget(ctk.CTkToplevel):
    """
    A stylish floating Book widget that stays pinned above all other windows on Windows desktop.
    Supports buttery-smooth dragging anywhere across the screen without accidental menu popups
    and dynamic on-the-fly resizing (mouse wheel or slider).
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
        self.configure(fg_color=self.theme["bg_primary"])
        try:
            self.wm_attributes("-transparentcolor", self.theme["bg_primary"])
        except Exception:
            pass

        # Load icon size from settings
        self.icon_size = int(self.db.get_setting("icon_size", DEFAULT_ICON_SIZE))
        self.icon_size = max(MIN_ICON_SIZE, min(MAX_ICON_SIZE, self.icon_size))
        self.widget_size = self.icon_size + 16
        
        # Load saved position or default to top right
        screen_w = self.winfo_screenwidth()
        default_x = screen_w - self.widget_size - 40
        default_y = 120
        
        saved_x = int(self.db.get_setting("pos_x", default_x))
        saved_y = int(self.db.get_setting("pos_y", default_y))
        
        self.geometry(f"{self.widget_size}x{self.widget_size}+{saved_x}+{saved_y}")

        # Drag tracking offsets and timestamp
        self._offset_x = 0
        self._offset_y = 0
        self._press_screen_x = 0
        self._press_screen_y = 0
        self._press_time = 0.0
        self._drag_occurred = False
        self.is_hovered = False

        self._load_icons()
        self._build_ui()
        self._bind_events()

    def _load_icons(self):
        # Generate normal and hover book states at current icon size
        self.normal_pil = generate_book_image(
            size=self.icon_size,
            theme_name=self.theme_name,
            is_hovered=False
        )
        self.hover_pil = generate_book_image(
            size=self.icon_size,
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
            cursor="fleur"  # Move cursor to clearly show it is movable across the screen
        )
        self.book_label.place(relx=0.5, rely=0.5, anchor="center")

    def _bind_events(self):
        # Bind exclusively to the container and book label
        widgets_to_bind = (self.container, self.book_label)
        for w in widgets_to_bind:
            # Mouse Left Press / Drag / Release
            w.bind("<ButtonPress-1>", self._on_press)
            w.bind("<B1-Motion>", self._on_drag)
            w.bind("<ButtonRelease-1>", self._on_release)

            # Middle Mouse Drag Support
            w.bind("<ButtonPress-2>", self._on_press)
            w.bind("<B2-Motion>", self._on_drag)
            w.bind("<ButtonRelease-2>", self._on_release)
            
            # Mouse Right Click for quick menu
            w.bind("<Button-3>", self._on_right_click)
            
            # Hover glow effects
            w.bind("<Enter>", self._on_mouse_enter)
            w.bind("<Leave>", self._on_mouse_leave)
            
            # Mouse Wheel to Dynamically Resize on the fly!
            w.bind("<MouseWheel>", self._on_mouse_wheel)
            w.bind("<Button-4>", lambda e: self.adjust_size(6))
            w.bind("<Button-5>", lambda e: self.adjust_size(-6))

    def _on_mouse_enter(self, event):
        self.is_hovered = True
        self.book_label.configure(image=self.hover_img)
        self.attributes("-alpha", 1.0)
        return "break"

    def _on_mouse_leave(self, event):
        if not self._drag_occurred:
            self.is_hovered = False
            self.book_label.configure(image=self.normal_img)
            self.attributes("-alpha", float(self.db.get_setting("opacity", DEFAULT_OPACITY)))
        return "break"

    def _on_press(self, event):
        """Records initial click position and absolute window offset for jitter-free dragging."""
        self._offset_x = event.x_root - self.winfo_x()
        self._offset_y = event.y_root - self.winfo_y()
        self._press_screen_x = event.x_root
        self._press_screen_y = event.y_root
        self._press_time = time.time()
        self._drag_occurred = False
        self.attributes("-alpha", 1.0)
        return "break"

    def _on_drag(self, event):
        """Calculates exact absolute position without Tkinter winfo jitter."""
        dist = abs(event.x_root - self._press_screen_x) + abs(event.y_root - self._press_screen_y)
        
        # If user moved mouse more than 5 pixels, register as drag
        if dist > 5:
            self._drag_occurred = True

        new_x = event.x_root - self._offset_x
        new_y = event.y_root - self._offset_y
        
        # Position window directly at mouse cursor
        self.geometry(f"+{new_x}+{new_y}")
        return "break"

    def _on_release(self, event):
        dist = abs(event.x_root - self._press_screen_x) + abs(event.y_root - self._press_screen_y)
        elapsed = time.time() - self._press_time
        
        # Determine if this was a drag gesture vs a stationary click
        is_drag = self._drag_occurred or dist > 5 or elapsed > 0.35

        if is_drag:
            # User dragged and placed the logo: Save coordinates and DO NOT open options menu!
            self.db.set_setting("pos_x", self.winfo_x())
            self.db.set_setting("pos_y", self.winfo_y())
        else:
            # Quick stationary click: Open options menu
            self._toggle_menu()

        self._drag_occurred = False

        if not self.is_hovered:
            self.book_label.configure(image=self.normal_img)
            self.attributes("-alpha", float(self.db.get_setting("opacity", DEFAULT_OPACITY)))

        return "break"

    def _on_mouse_wheel(self, event):
        """Scroll wheel over the book dynamically adjusts its size in real-time."""
        if event.delta > 0:
            self.adjust_size(6)
        elif event.delta < 0:
            self.adjust_size(-6)
        return "break"

    def adjust_size(self, delta: int):
        new_size = self.icon_size + delta
        self.set_icon_size(new_size)

    def set_icon_size(self, new_size: int):
        """Resizes the book widget dynamically and updates screen geometry."""
        new_size = max(MIN_ICON_SIZE, min(MAX_ICON_SIZE, int(new_size)))
        if new_size == self.icon_size:
            return

        old_widget_size = self.widget_size
        self.icon_size = new_size
        self.widget_size = self.icon_size + 16

        # Adjust position slightly so resizing expands from the center
        cur_x = self.winfo_x() - (self.widget_size - old_widget_size) // 2
        cur_y = self.winfo_y() - (self.widget_size - old_widget_size) // 2

        # Re-render book images at new resolution
        self._load_icons()
        self.book_label.configure(image=self.hover_img if self.is_hovered else self.normal_img)

        self.geometry(f"{self.widget_size}x{self.widget_size}+{cur_x}+{cur_y}")
        
        # Save new size and position
        self.db.set_setting("icon_size", self.icon_size)
        self.db.set_setting("pos_x", cur_x)
        self.db.set_setting("pos_y", cur_y)

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
            on_change_size=self.set_icon_size,
            current_size=self.icon_size,
            theme_name=self.theme_name
        )

    def _on_right_click(self, event):
        self._toggle_menu()
        return "break"

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
