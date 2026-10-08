"""
Planner & Reminder Creator Window with 1-Click Presets and Custom Time Picker.
"""

from datetime import datetime, timedelta
import customtkinter as ctk
from PIL import ImageTk
from typing import Callable, Optional
from src.database import Database
from src.theme import THEMES, DEFAULT_THEME
from src.book_graphics import generate_book_image


class ReminderWindow(ctk.CTkToplevel):
    """
    Planner-styled Reminder Creation Dialog.
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

        self.title("⏰ Set Planner Reminder")
        self.geometry("520x640")
        self.attributes("-topmost", True)
        self.configure(fg_color=self.theme["bg_primary"])

        # Center window
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - 520) // 2
        y = (screen_h - 640) // 2
        self.geometry(f"520x640+{x}+{y}")

        self._build_ui()

    def _build_ui(self):
        card = ctk.CTkFrame(
            self,
            fg_color=self.theme["bg_secondary"],
            corner_radius=16,
            border_width=2,
            border_color=self.theme["book_accent"]
        )
        card.pack(fill="both", expand=True, padx=14, pady=14)

        # 1. Header
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(12, 8))

        book_pil = generate_book_image(size=36, theme_name=self.theme_name, is_hovered=True)
        self.book_img = ImageTk.PhotoImage(book_pil)
        icon_lbl = ctk.CTkLabel(header, image=self.book_img, text="")
        icon_lbl.pack(side="left", padx=(0, 8))

        title_lbl = ctk.CTkLabel(
            header,
            text="PLANNER ALARM / REMINDER",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=self.theme["book_accent"]
        )
        title_lbl.pack(side="left")

        # 2. Reminder Title
        lbl_title = ctk.CTkLabel(
            card,
            text="Reminder Subject / Task:",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=self.theme["text_secondary"]
        )
        lbl_title.pack(anchor="w", padx=16, pady=(6, 2))

        self.title_entry = ctk.CTkEntry(
            card,
            placeholder_text="e.g. Team Meeting, Drink Water, Take Break...",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color=self.theme["bg_primary"],
            border_color=self.theme["bg_card"],
            height=36,
            corner_radius=8
        )
        self.title_entry.pack(fill="x", padx=16, pady=(0, 10))

        # 3. Quick Presets Section
        preset_lbl = ctk.CTkLabel(
            card,
            text="⚡ 1-Click Quick Presets:",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=self.theme["book_accent"]
        )
        preset_lbl.pack(anchor="w", padx=16, pady=(2, 4))

        preset_grid = ctk.CTkFrame(card, fg_color="transparent")
        preset_grid.pack(fill="x", padx=16, pady=(0, 12))

        presets = [
            ("⏱️ In 5 Min", 5),
            ("⏱️ In 15 Min", 15),
            ("⏱️ In 30 Min", 30),
            ("⏰ In 1 Hour", 60),
            ("🌙 Tonight 8 PM", "tonight_8pm"),
            ("🌅 Tomorrow 9 AM", "tomorrow_9am")
        ]

        for i, (label, val) in enumerate(presets):
            row = i // 3
            col = i % 3
            btn = ctk.CTkButton(
                preset_grid,
                text=label,
                font=ctk.CTkFont(size=11),
                fg_color=self.theme["bg_card"],
                hover_color=self.theme["book_cover"],
                height=30,
                corner_radius=8,
                command=lambda v=val: self._apply_preset(v)
            )
            btn.grid(row=row, column=col, padx=3, pady=3, sticky="ew")
            preset_grid.columnconfigure(col, weight=1)

        # 4. Custom Date & Time Picker Frame
        picker_box = ctk.CTkFrame(
            card,
            fg_color=self.theme["bg_primary"],
            corner_radius=10,
            border_width=1,
            border_color=self.theme["bg_card"]
        )
        picker_box.pack(fill="x", padx=16, pady=(0, 10))

        picker_title = ctk.CTkLabel(
            picker_box,
            text="📅 Exact Date & Time Schedule:",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=self.theme["text_primary"]
        )
        picker_title.pack(anchor="w", padx=12, pady=(8, 6))

        # Date Row
        date_row = ctk.CTkFrame(picker_box, fg_color="transparent")
        date_row.pack(fill="x", padx=12, pady=(0, 6))

        now = datetime.now()
        
        ctk.CTkLabel(date_row, text="Date:", font=ctk.CTkFont(size=11), width=45).pack(side="left")
        
        # Year, Month, Day Option Menus
        years = [str(now.year + i) for i in range(3)]
        self.year_menu = ctk.CTkOptionMenu(date_row, values=years, width=80, height=28, fg_color=self.theme["bg_card"])
        self.year_menu.set(str(now.year))
        self.year_menu.pack(side="left", padx=2)

        months = [f"{m:02d}" for m in range(1, 13)]
        self.month_menu = ctk.CTkOptionMenu(date_row, values=months, width=70, height=28, fg_color=self.theme["bg_card"])
        self.month_menu.set(f"{now.month:02d}")
        self.month_menu.pack(side="left", padx=2)

        days = [f"{d:02d}" for d in range(1, 32)]
        self.day_menu = ctk.CTkOptionMenu(date_row, values=days, width=70, height=28, fg_color=self.theme["bg_card"])
        self.day_menu.set(f"{now.day:02d}")
        self.day_menu.pack(side="left", padx=2)

        # Time Row
        time_row = ctk.CTkFrame(picker_box, fg_color="transparent")
        time_row.pack(fill="x", padx=12, pady=(0, 8))

        ctk.CTkLabel(time_row, text="Time:", font=ctk.CTkFont(size=11), width=45).pack(side="left")

        hours = [f"{h:02d}" for h in range(1, 13)]
        self.hour_menu = ctk.CTkOptionMenu(time_row, values=hours, width=70, height=28, fg_color=self.theme["bg_card"])
        curr_12hr = now.hour % 12 or 12
        self.hour_menu.set(f"{curr_12hr:02d}")
        self.hour_menu.pack(side="left", padx=2)

        minutes = [f"{m:02d}" for m in range(0, 60, 5)]
        self.minute_menu = ctk.CTkOptionMenu(time_row, values=minutes, width=70, height=28, fg_color=self.theme["bg_card"])
        # Round up to next 5 minutes
        next_min = ((now.minute // 5) + 1) * 5
        if next_min >= 60:
            next_min = 0
        self.minute_menu.set(f"{next_min:02d}")
        self.minute_menu.pack(side="left", padx=2)

        self.ampm_menu = ctk.CTkOptionMenu(time_row, values=["AM", "PM"], width=70, height=28, fg_color=self.theme["bg_card"])
        self.ampm_menu.set("PM" if now.hour >= 12 else "AM")
        self.ampm_menu.pack(side="left", padx=2)

        # Repeat Row
        repeat_row = ctk.CTkFrame(picker_box, fg_color="transparent")
        repeat_row.pack(fill="x", padx=12, pady=(0, 8))

        ctk.CTkLabel(repeat_row, text="Repeat:", font=ctk.CTkFont(size=11), width=50).pack(side="left")
        self.repeat_menu = ctk.CTkOptionMenu(
            repeat_row,
            values=["Once (No Repeat)", "Daily", "Weekly"],
            width=160,
            height=28,
            fg_color=self.theme["bg_card"]
        )
        self.repeat_menu.set("Once (No Repeat)")
        self.repeat_menu.pack(side="left", padx=2)

        # 5. Additional Description
        lbl_desc = ctk.CTkLabel(
            card,
            text="Optional Notes / Details:",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=self.theme["text_secondary"]
        )
        lbl_desc.pack(anchor="w", padx=16, pady=(4, 2))

        self.desc_entry = ctk.CTkTextbox(
            card,
            height=60,
            fg_color=self.theme["bg_primary"],
            border_color=self.theme["bg_card"],
            border_width=1,
            corner_radius=8,
            font=ctk.CTkFont(size=12)
        )
        self.desc_entry.pack(fill="x", padx=16, pady=(0, 12))

        # 6. Bottom Action Button
        btn_bar = ctk.CTkFrame(card, fg_color="transparent")
        btn_bar.pack(fill="x", padx=16, pady=(0, 10))

        cancel_btn = ctk.CTkButton(
            btn_bar,
            text="Cancel",
            width=80,
            height=34,
            fg_color=self.theme["bg_card"],
            hover_color=self.theme["bg_primary"],
            font=ctk.CTkFont(size=12),
            command=self.destroy
        )
        cancel_btn.pack(side="left")

        save_btn = ctk.CTkButton(
            btn_bar,
            text="🔔 Set Reminder",
            height=34,
            fg_color=self.theme["book_cover"],
            hover_color=self.theme["book_spine"],
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._save_reminder
        )
        save_btn.pack(side="right", expand=True, fill="x", padx=(10, 0))

    def _apply_preset(self, val):
        now = datetime.now()
        target_time = now

        if isinstance(val, int):
            target_time = now + timedelta(minutes=val)
        elif val == "tonight_8pm":
            target_time = now.replace(hour=20, minute=0, second=0, microsecond=0)
            if target_time <= now:
                target_time += timedelta(days=1)
        elif val == "tomorrow_9am":
            target_time = (now + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)

        # Update Pickers
        self.year_menu.set(str(target_time.year))
        self.month_menu.set(f"{target_time.month:02d}")
        self.day_menu.set(f"{target_time.day:02d}")

        hr12 = target_time.hour % 12 or 12
        self.hour_menu.set(f"{hr12:02d}")
        self.minute_menu.set(f"{target_time.minute:02d}")
        self.ampm_menu.set("PM" if target_time.hour >= 12 else "AM")

    def _save_reminder(self):
        title = self.title_entry.get().strip() or "Reminder"
        description = self.desc_entry.get("1.0", "end-1c").strip()

        # Build target datetime string
        try:
            year = int(self.year_menu.get())
            month = int(self.month_menu.get())
            day = int(self.day_menu.get())

            hr = int(self.hour_menu.get())
            if self.ampm_menu.get() == "PM" and hr < 12:
                hr += 12
            elif self.ampm_menu.get() == "AM" and hr == 12:
                hr = 0
                
            minute = int(self.minute_menu.get())
            target_dt = datetime(year, month, day, hr, minute, 0)
        except Exception:
            target_dt = datetime.now() + timedelta(minutes=10)

        repeat_raw = self.repeat_menu.get()
        repeat_map = {
            "Once (No Repeat)": "none",
            "Daily": "daily",
            "Weekly": "weekly"
        }
        repeat = repeat_map.get(repeat_raw, "none")

        self.db.add_reminder(
            title=title,
            remind_time=target_dt.strftime("%Y-%m-%d %H:%M:%S"),
            description=description,
            repeat_interval=repeat
        )

        if self.on_saved:
            self.on_saved()
        self.destroy()

