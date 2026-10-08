"""
Typable Date & Time Reminder Creator Window.
"""

from datetime import datetime, timedelta
import re
import customtkinter as ctk
from PIL import ImageTk
from typing import Callable, Optional
from src.database import Database
from src.theme import THEMES, DEFAULT_THEME
from src.book_graphics import generate_reminder_logo


def parse_smart_datetime(date_str: str, time_str: str) -> datetime:
    """
    Robust smart parser for typed date & time inputs.
    Supports formats like:
    - Dates: 2026-10-08, 08-10-2026, 08/10/2026, 10/8/2026, today, tomorrow
    - Times: 6:30 PM, 06:30pm, 18:30, 6:30, 9 AM, 14:00
    """
    now = datetime.now()
    d_clean = date_str.strip().lower()
    t_clean = time_str.strip()

    # 1. Parse Date
    target_date = now.date()
    if d_clean == "tomorrow":
        target_date = (now + timedelta(days=1)).date()
    elif d_clean in ("today", ""):
        target_date = now.date()
    else:
        # Try matching YYYY-MM-DD, DD-MM-YYYY, YYYY/MM/DD, DD/MM/YYYY
        matched_date = False
        date_patterns = [
            "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d", "%d/%m/%Y",
            "%m/%d/%Y", "%m-%d-%Y", "%Y.%m.%d", "%d.%m.%Y"
        ]
        for fmt in date_patterns:
            try:
                target_date = datetime.strptime(d_clean, fmt).date()
                matched_date = True
                break
            except ValueError:
                pass
        
        if not matched_date:
            target_date = now.date()

    # 2. Parse Time
    hour = now.hour
    minute = (now.minute + 10) % 60
    
    t_clean = t_clean.upper().replace(" ", "")
    
    # Check 12-hour format with AM/PM (e.g. 6:30PM, 06:30AM, 9PM)
    match_12 = re.match(r"^(\d{1,2})(?::(\d{1,2}))?(AM|PM)$", t_clean)
    if match_12:
        h = int(match_12.group(1))
        m = int(match_12.group(2) or 0)
        ampm = match_12.group(3)
        if ampm == "PM" and h < 12:
            h += 12
        elif ampm == "AM" and h == 12:
            h = 0
        hour, minute = h, m
    else:
        # Check 24-hour or plain format (e.g. 18:30, 6:30, 1830)
        match_24 = re.match(r"^(\d{1,2}):(\d{1,2})$", t_clean)
        if match_24:
            hour = int(match_24.group(1))
            minute = int(match_24.group(2))
        else:
            # Fallback to current time + 10 min
            future = now + timedelta(minutes=10)
            hour = future.hour
            minute = future.minute

    hour = max(0, min(23, hour))
    minute = max(0, min(59, minute))

    return datetime(target_date.year, target_date.month, target_date.day, hour, minute, 0)


class ReminderWindow(ctk.CTkToplevel):
    """
    Compact Reminder Creator with DIRECTLY TYPABLE Date & Time inputs.
    """
    def __init__(
        self,
        master,
        db: Database,
        on_saved: Optional[Callable] = None,
        theme_name: str = DEFAULT_THEME
    ):
        super().__init__(master)
        self.db = db
        self.on_saved = on_saved
        self.theme_name = theme_name
        self.theme = THEMES.get(theme_name, THEMES[DEFAULT_THEME])

        self.title("⏰ Set Reminder")
        self.geometry("380x320")
        self.attributes("-topmost", True)
        self.resizable(False, False)
        self.configure(fg_color=self.theme["bg_primary"])

        # Center window
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - 380) // 2
        y = (screen_h - 320) // 2
        self.geometry(f"380x320+{x}+{y}")

        self._build_ui()

    def _build_ui(self):
        card = ctk.CTkFrame(
            self,
            fg_color=self.theme["bg_secondary"],
            corner_radius=12,
            border_width=2,
            border_color=self.theme["book_accent"]
        )
        card.pack(fill="both", expand=True, padx=6, pady=6)

        # 1. Header
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(6, 4))

        logo_pil = generate_reminder_logo(size=22, theme_name=self.theme_name, is_hovered=True)
        self.logo_img = ImageTk.PhotoImage(logo_pil)
        icon_lbl = ctk.CTkLabel(header, image=self.logo_img, text="")
        icon_lbl.pack(side="left", padx=(0, 6))

        title_lbl = ctk.CTkLabel(
            header,
            text="SET REMINDER (TYPE DATE & TIME)",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=self.theme["book_accent"]
        )
        title_lbl.pack(side="left")

        close_btn = ctk.CTkButton(
            header,
            text="✕",
            width=20,
            height=20,
            fg_color="transparent",
            hover_color=self.theme["danger"],
            text_color=self.theme["text_secondary"],
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.destroy
        )
        close_btn.pack(side="right")

        # 2. Reminder Task Subject
        self.title_entry = ctk.CTkEntry(
            card,
            placeholder_text="Enter task (e.g. Meeting, Call, Drink Water)...",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            fg_color=self.theme["bg_primary"],
            border_color=self.theme["bg_card"],
            height=32,
            corner_radius=6
        )
        self.title_entry.pack(fill="x", padx=10, pady=(2, 6))
        self.title_entry.focus_set()

        # 3. Quick 1-Click Presets (Updates typed fields automatically)
        preset_frame = ctk.CTkFrame(card, fg_color="transparent")
        preset_frame.pack(fill="x", padx=10, pady=(0, 6))

        presets = [
            ("+5m", 5),
            ("+15m", 15),
            ("+30m", 30),
            ("+1h", 60),
            ("Tomorrow 9am", "tomorrow_9am")
        ]

        for label, val in presets:
            btn = ctk.CTkButton(
                preset_frame,
                text=label,
                font=ctk.CTkFont(size=10),
                height=22,
                fg_color=self.theme["bg_card"],
                hover_color=self.theme["book_cover"],
                corner_radius=6,
                command=lambda v=val: self._apply_preset(v)
            )
            btn.pack(side="left", padx=1, expand=True, fill="x")

        # 4. TYPABLE Date & Time Entry Section
        inputs_box = ctk.CTkFrame(
            card,
            fg_color=self.theme["bg_primary"],
            corner_radius=8,
            border_width=1,
            border_color=self.theme["bg_card"]
        )
        inputs_box.pack(fill="x", padx=10, pady=(0, 6))

        now = datetime.now()
        default_date = now.strftime("%Y-%m-%d")
        default_time = (now + timedelta(minutes=15)).strftime("%I:%M %p")

        # Date Row (Typable)
        d_row = ctk.CTkFrame(inputs_box, fg_color="transparent")
        d_row.pack(fill="x", padx=8, pady=(6, 3))

        ctk.CTkLabel(
            d_row,
            text="📅 Type Date:",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=self.theme["book_accent"],
            width=85,
            anchor="w"
        ).pack(side="left")

        self.date_entry = ctk.CTkEntry(
            d_row,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            height=28,
            fg_color=self.theme["bg_secondary"],
            border_color=self.theme["bg_card"]
        )
        self.date_entry.insert(0, default_date)
        self.date_entry.pack(side="left", fill="x", expand=True, padx=(4, 0))

        # Time Row (Typable)
        t_row = ctk.CTkFrame(inputs_box, fg_color="transparent")
        t_row.pack(fill="x", padx=8, pady=(3, 6))

        ctk.CTkLabel(
            t_row,
            text="⏰ Type Time:",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=self.theme["book_accent"],
            width=85,
            anchor="w"
        ).pack(side="left")

        self.time_entry = ctk.CTkEntry(
            t_row,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            height=28,
            fg_color=self.theme["bg_secondary"],
            border_color=self.theme["bg_card"]
        )
        self.time_entry.insert(0, default_time)
        self.time_entry.pack(side="left", fill="x", expand=True, padx=(4, 0))

        # 5. Repeat & Enter Shortcut row
        rep_row = ctk.CTkFrame(card, fg_color="transparent")
        rep_row.pack(fill="x", padx=10, pady=(0, 6))

        ctk.CTkLabel(rep_row, text="Repeat:", font=ctk.CTkFont(size=10), width=45).pack(side="left")
        self.repeat_menu = ctk.CTkOptionMenu(
            rep_row,
            values=["Once", "Daily", "Weekly"],
            width=110,
            height=24,
            font=ctk.CTkFont(size=10),
            fg_color=self.theme["bg_card"]
        )
        self.repeat_menu.set("Once")
        self.repeat_menu.pack(side="left")

        hint_lbl = ctk.CTkLabel(
            rep_row,
            text="Press Enter to save",
            font=ctk.CTkFont(size=9),
            text_color=self.theme["text_secondary"]
        )
        hint_lbl.pack(side="right")

        # 6. Bottom Save Button
        save_btn = ctk.CTkButton(
            card,
            text="🔔 Set Reminder",
            height=30,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=self.theme["book_cover"],
            hover_color=self.theme["book_spine"],
            corner_radius=6,
            command=self._save_reminder
        )
        save_btn.pack(fill="x", padx=10, pady=(0, 6))

        # Enter key triggers save
        for entry in (self.title_entry, self.date_entry, self.time_entry):
            entry.bind("<Return>", lambda e: self._save_reminder())

    def _apply_preset(self, val):
        now = datetime.now()
        target_time = now

        if isinstance(val, int):
            target_time = now + timedelta(minutes=val)
        elif val == "tomorrow_9am":
            target_time = (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)

        # Update typed fields
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, target_time.strftime("%Y-%m-%d"))

        self.time_entry.delete(0, "end")
        self.time_entry.insert(0, target_time.strftime("%I:%M %p"))

    def _save_reminder(self):
        title = self.title_entry.get().strip() or "Reminder"
        date_str = self.date_entry.get().strip()
        time_str = self.time_entry.get().strip()

        target_dt = parse_smart_datetime(date_str, time_str)

        repeat_raw = self.repeat_menu.get()
        repeat_map = {"Once": "none", "Daily": "daily", "Weekly": "weekly"}
        repeat = repeat_map.get(repeat_raw, "none")

        self.db.add_reminder(
            title=title,
            remind_time=target_dt.strftime("%Y-%m-%d %H:%M:%S"),
            repeat_interval=repeat
        )

        if self.on_saved:
            self.on_saved()
        self.destroy()
