"""
Alarm & Notification Manager: Background scheduler, sound player, and interactive alarm popups.
"""

import threading
import time
import winsound
from datetime import datetime
import customtkinter as ctk
from PIL import ImageTk
from typing import Callable, Optional
from src.database import Database
from src.theme import THEMES, DEFAULT_THEME
from src.book_graphics import generate_book_image


def play_chime():
    """Plays an elegant multi-tone notification chime in a non-blocking thread."""
    def _chime():
        try:
            # Elegant 3-chord arpeggio
            notes = [(523, 140), (659, 140), (784, 180), (1046, 320)]
            for freq, dur in notes:
                winsound.Beep(freq, dur)
                time.sleep(0.04)
        except Exception:
            try:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            except Exception:
                pass

    threading.Thread(target=_chime, daemon=True).start()


class AlarmDialog(ctk.CTkToplevel):
    """
    An always-on-top, book-themed alert dialog that pops up when a reminder is due.
    """
    def __init__(
        self,
        reminder_data: dict,
        db: Database,
        on_action: Optional[Callable] = None,
        theme_name: str = DEFAULT_THEME
    ):
        super().__init__()
        self.reminder = reminder_data
        self.db = db
        self.on_action = on_action
        self.theme_name = theme_name
        self.theme = THEMES.get(theme_name, THEMES[DEFAULT_THEME])

        self.title("📖 Book Reminder Due!")
        self.geometry("440x300")
        self.attributes("-topmost", True)
        self.resizable(False, False)
        self.configure(fg_color=self.theme["bg_primary"])

        # Center on screen
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - 440) // 2
        y = (screen_h - 300) // 2
        self.geometry(f"440x300+{x}+{y}")

        self._build_ui()
        play_chime()

    def _build_ui(self):
        # Outer parchment-styled container card
        card = ctk.CTkFrame(
            self,
            fg_color=self.theme["bg_secondary"],
            corner_radius=16,
            border_width=2,
            border_color=self.theme["book_accent"]
        )
        card.pack(fill="both", expand=True, padx=14, pady=14)

        # Header Row
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(14, 8))

        # Mini Book Icon
        book_pil = generate_book_image(size=42, theme_name=self.theme_name, is_hovered=True)
        self.book_img = ImageTk.PhotoImage(book_pil)
        icon_lbl = ctk.CTkLabel(header, image=self.book_img, text="")
        icon_lbl.pack(side="left", padx=(0, 10))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left", fill="x", expand=True)

        badge_lbl = ctk.CTkLabel(
            title_box,
            text="⏰ PLANNER REMINDER DUE",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=self.theme["book_accent"]
        )
        badge_lbl.pack(anchor="w")

        time_str = datetime.now().strftime("%I:%M %p • %b %d")
        time_lbl = ctk.CTkLabel(
            title_box,
            text=time_str,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=self.theme["text_secondary"]
        )
        time_lbl.pack(anchor="w")

        # Reminder Title & Details (Styled inside a book page frame)
        page_frame = ctk.CTkFrame(
            card,
            fg_color=self.theme["page_bg"],
            corner_radius=12,
            border_width=1,
            border_color=self.theme["page_lines"]
        )
        page_frame.pack(fill="both", expand=True, padx=16, pady=6)

        rem_title = ctk.CTkLabel(
            page_frame,
            text=self.reminder.get("title", "Reminder"),
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=self.theme["text_page"],
            wraplength=380,
            justify="left"
        )
        rem_title.pack(anchor="w", padx=14, pady=(10, 4))

        desc_text = self.reminder.get("description", "").strip()
        if desc_text:
            rem_desc = ctk.CTkLabel(
                page_frame,
                text=desc_text,
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=self.theme["text_page"],
                wraplength=380,
                justify="left"
            )
            rem_desc.pack(anchor="w", padx=14, pady=(0, 8))

        # Action Buttons
        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=(10, 14))

        # Snooze 5m
        snooze_btn = ctk.CTkButton(
            btn_row,
            text="💤 Snooze 5m",
            fg_color=self.theme["bg_card"],
            hover_color=self.theme["bg_primary"],
            text_color=self.theme["text_primary"],
            font=ctk.CTkFont(family="Segoe UI", size=12),
            height=34,
            corner_radius=8,
            command=self._on_snooze_5
        )
        snooze_btn.pack(side="left", expand=True, fill="x", padx=(0, 6))

        # Snooze 15m
        snooze_15_btn = ctk.CTkButton(
            btn_row,
            text="💤 15m",
            fg_color=self.theme["bg_card"],
            hover_color=self.theme["bg_primary"],
            text_color=self.theme["text_primary"],
            font=ctk.CTkFont(family="Segoe UI", size=12),
            height=34,
            width=60,
            corner_radius=8,
            command=self._on_snooze_15
        )
        snooze_15_btn.pack(side="left", padx=(0, 6))

        # Complete / Done Button
        done_btn = ctk.CTkButton(
            btn_row,
            text="✓ Mark Done",
            fg_color=self.theme["book_cover"],
            hover_color=self.theme["book_spine"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            height=34,
            corner_radius=8,
            command=self._on_complete
        )
        done_btn.pack(side="left", expand=True, fill="x")

    def _on_snooze_5(self):
        self.db.snooze_reminder(self.reminder["id"], minutes=5)
        if self.on_action:
            self.on_action()
        self.destroy()

    def _on_snooze_15(self):
        self.db.snooze_reminder(self.reminder["id"], minutes=15)
        if self.on_action:
            self.on_action()
        self.destroy()

    def _on_complete(self):
        self.db.complete_reminder(self.reminder["id"])
        if self.on_action:
            self.on_action()
        self.destroy()


class AlarmService:
    """
    Background worker that continually polls SQLite for due reminders
    and safely dispatches alert windows on the main thread.
    """
    def __init__(self, root: ctk.CTk, db: Database, on_status_change: Optional[Callable] = None):
        self.root = root
        self.db = db
        self.on_status_change = on_status_change
        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        self._active_alert_ids = set()

    def start(self):
        if not self.is_running:
            self.is_running = True
            self._thread = threading.Thread(target=self._poll_loop, daemon=True)
            self._thread.start()

    def stop(self):
        self.is_running = False

    def _poll_loop(self):
        while self.is_running:
            try:
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                pending = self.db.get_pending_due_reminders(now_str)
                
                for rem in pending:
                    rem_id = rem["id"]
                    if rem_id not in self._active_alert_ids:
                        self._active_alert_ids.add(rem_id)
                        # Schedule dialog popup on Tkinter main thread
                        self.root.after(0, self._show_alert, rem)
            except Exception as e:
                print(f"[AlarmService Error] {e}")
                
            time.sleep(2)  # Check every 2 seconds

    def _show_alert(self, reminder_data: dict):
        theme_name = self.db.get_setting("theme", DEFAULT_THEME)
        
        def _cleanup():
            self._active_alert_ids.discard(reminder_data["id"])
            if self.on_status_change:
                self.on_status_change()

        dialog = AlarmDialog(
            reminder_data=reminder_data,
            db=self.db,
            on_action=_cleanup,
            theme_name=theme_name
        )
        dialog.protocol("WM_DELETE_WINDOW", lambda: (_cleanup(), dialog.destroy()))

