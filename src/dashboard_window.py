"""
Library Dashboard Window: Search, manage, filter, and organize Notes & Reminders.
"""

from datetime import datetime
import customtkinter as ctk
from PIL import ImageTk
from typing import Callable, Optional
from src.database import Database
from src.theme import THEMES, DEFAULT_THEME, NOTE_CATEGORIES
from src.book_graphics import generate_book_image
from src.notes_window import NotesWindow
from src.reminder_window import ReminderWindow


class DashboardWindow(ctk.CTkToplevel):
    """
    Main Library Dashboard and Archive Manager.
    """
    def __init__(
        self,
        master,
        db: Database,
        on_theme_changed: Optional[Callable] = None,
        on_change_size: Optional[Callable] = None,
        theme_name: str = DEFAULT_THEME
    ):
        super().__init__(master)
        self.db = db
        self.on_theme_changed = on_theme_changed
        self.on_change_size = on_change_size
        self.theme_name = self.db.get_setting("theme", theme_name)
        self.theme = THEMES.get(self.theme_name, THEMES[DEFAULT_THEME])

        self.title("📚 My Book Journal & Planner Hub")
        self.geometry("820x680")
        self.attributes("-topmost", True)
        self.configure(fg_color=self.theme["bg_primary"])

        # Center on screen
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - 820) // 2
        y = (screen_h - 680) // 2
        self.geometry(f"820x680+{x}+{y}")

        self.current_category = "All"
        self.active_tab = "notes"  # "notes", "reminders", "settings"

        self._build_ui()
        self._refresh_content()

    def _build_ui(self):
        # Outer Card
        card = ctk.CTkFrame(
            self,
            fg_color=self.theme["bg_secondary"],
            corner_radius=16,
            border_width=2,
            border_color=self.theme["book_accent"]
        )
        card.pack(fill="both", expand=True, padx=14, pady=14)

        # Header with Book Icon, Title, and Tab Switcher
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(12, 8))

        # Mini Book Icon
        book_pil = generate_book_image(size=40, theme_name=self.theme_name, is_hovered=True)
        self.book_img = ImageTk.PhotoImage(book_pil)
        icon_lbl = ctk.CTkLabel(header, image=self.book_img, text="")
        icon_lbl.pack(side="left", padx=(0, 10))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")

        title_lbl = ctk.CTkLabel(
            title_box,
            text="LIBRARY & PLANNER HUB",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=self.theme["book_accent"]
        )
        title_lbl.pack(anchor="w")

        sub_lbl = ctk.CTkLabel(
            title_box,
            text="Your personal floating notebook & schedule archive",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=self.theme["text_secondary"]
        )
        sub_lbl.pack(anchor="w")

        # Top Right New Action Button
        self.top_new_btn = ctk.CTkButton(
            header,
            text="➕ New Page",
            width=110,
            height=32,
            fg_color=self.theme["book_cover"],
            hover_color=self.theme["book_spine"],
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._on_click_new
        )
        self.top_new_btn.pack(side="right")

        # Tab Navigation Bar
        tab_bar = ctk.CTkFrame(card, fg_color=self.theme["bg_card"], corner_radius=10)
        tab_bar.pack(fill="x", padx=16, pady=(4, 10))

        self.tab_buttons = {}
        tabs = [
            ("notes", "📖 Journal Notes", self._show_notes_tab),
            ("reminders", "⏰ Planner Reminders", self._show_reminders_tab),
            ("settings", "⚙️ Book Settings", self._show_settings_tab),
        ]

        for tab_id, tab_label, cmd in tabs:
            btn = ctk.CTkButton(
                tab_bar,
                text=tab_label,
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                height=32,
                fg_color=self.theme["book_cover"] if tab_id == self.active_tab else "transparent",
                hover_color=self.theme["book_cover"],
                corner_radius=8,
                command=cmd
            )
            btn.pack(side="left", padx=4, pady=4)
            self.tab_buttons[tab_id] = btn

        # Search Bar & Filter Row
        self.filter_container = ctk.CTkFrame(card, fg_color="transparent")
        self.filter_container.pack(fill="x", padx=16, pady=(0, 8))

        self.search_entry = ctk.CTkEntry(
            self.filter_container,
            placeholder_text="🔍 Search titles, contents, or tags...",
            font=ctk.CTkFont(size=12),
            fg_color=self.theme["bg_primary"],
            border_color=self.theme["bg_card"],
            height=34,
            corner_radius=8
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.search_entry.bind("<KeyRelease>", lambda e: self._refresh_content())

        # Category Scrollable Filter (for notes tab)
        self.cat_filter_frame = ctk.CTkScrollableFrame(
            self.filter_container,
            fg_color="transparent",
            orientation="horizontal",
            height=34
        )
        self.cat_filter_frame.pack(side="right")

        self.cat_filter_btns = {}
        all_cats = [{"name": "All", "icon": "📚"}] + NOTE_CATEGORIES
        for c in all_cats:
            btn = ctk.CTkButton(
                self.cat_filter_frame,
                text=f"{c['icon']} {c['name']}",
                font=ctk.CTkFont(size=11),
                height=26,
                fg_color=self.theme["book_cover"] if c["name"] == self.current_category else self.theme["bg_primary"],
                hover_color=self.theme["book_cover"],
                corner_radius=13,
                command=lambda name=c["name"]: self._filter_category(name)
            )
            btn.pack(side="left", padx=2)
            self.cat_filter_btns[c["name"]] = btn

        # Main Scrollable Content Area
        self.content_scroll = ctk.CTkScrollableFrame(
            card,
            fg_color=self.theme["bg_primary"],
            corner_radius=12,
            border_width=1,
            border_color=self.theme["bg_card"]
        )
        self.content_scroll.pack(fill="both", expand=True, padx=16, pady=(0, 14))

    def _show_notes_tab(self):
        self.active_tab = "notes"
        self._update_tab_styles()
        self.top_new_btn.configure(text="➕ New Note", command=self._on_click_new)
        self.filter_container.pack(fill="x", padx=16, pady=(0, 8), before=self.content_scroll)
        self.cat_filter_frame.pack(side="right")
        self._refresh_content()

    def _show_reminders_tab(self):
        self.active_tab = "reminders"
        self._update_tab_styles()
        self.top_new_btn.configure(text="➕ New Reminder", command=self._on_click_new_reminder)
        self.filter_container.pack(fill="x", padx=16, pady=(0, 8), before=self.content_scroll)
        self.cat_filter_frame.pack_forget()
        self._refresh_content()

    def _show_settings_tab(self):
        self.active_tab = "settings"
        self._update_tab_styles()
        self.top_new_btn.configure(text="", width=0)
        self.filter_container.pack_forget()
        self._render_settings_view()

    def _update_tab_styles(self):
        for tab_id, btn in self.tab_buttons.items():
            if tab_id == self.active_tab:
                btn.configure(fg_color=self.theme["book_cover"])
            else:
                btn.configure(fg_color="transparent")

    def _filter_category(self, cat_name: str):
        self.current_category = cat_name
        for name, btn in self.cat_filter_btns.items():
            if name == cat_name:
                btn.configure(fg_color=self.theme["book_cover"])
            else:
                btn.configure(fg_color=self.theme["bg_primary"])
        self._refresh_content()

    def _refresh_content(self):
        # Clear existing children
        for widget in self.content_scroll.winfo_children():
            widget.destroy()

        if self.active_tab == "notes":
            self._render_notes_view()
        elif self.active_tab == "reminders":
            self._render_reminders_view()
        elif self.active_tab == "settings":
            self._render_settings_view()

    # ------------------ Notes View ------------------
    def _render_notes_view(self):
        query = self.search_entry.get().strip()
        notes = self.db.get_notes(search_query=query, category=self.current_category)

        if not notes:
            empty_frame = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
            empty_frame.pack(fill="both", expand=True, pady=40)
            ctk.CTkLabel(
                empty_frame,
                text="📖 No journal pages found.",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=self.theme["text_secondary"]
            ).pack()
            ctk.CTkLabel(
                empty_frame,
                text="Click '➕ New Note' above or on your floating book to create your first page!",
                font=ctk.CTkFont(size=11),
                text_color=self.theme["text_secondary"]
            ).pack(pady=4)
            return

        for note in notes:
            self._create_note_card(note)

    def _create_note_card(self, note: dict):
        card = ctk.CTkFrame(
            self.content_scroll,
            fg_color=self.theme["bg_secondary"],
            corner_radius=10,
            border_width=1,
            border_color=self.theme["bg_card"]
        )
        card.pack(fill="x", pady=4, padx=4)

        # Card header
        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=12, pady=(8, 2))

        # Pinned badge
        if note.get("is_pinned"):
            ctk.CTkLabel(
                hdr,
                text="📌 PINNED",
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=self.theme["book_accent"]
            ).pack(side="left", padx=(0, 6))

        # Title
        title_lbl = ctk.CTkLabel(
            hdr,
            text=note["title"],
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=self.theme["text_primary"],
            anchor="w"
        )
        title_lbl.pack(side="left", fill="x", expand=True)

        # Category Badge
        cat_badge = ctk.CTkLabel(
            hdr,
            text=note.get("category", "General"),
            font=ctk.CTkFont(size=10),
            fg_color=self.theme["bg_card"],
            corner_radius=6,
            padx=8,
            pady=2
        )
        cat_badge.pack(side="right", padx=(6, 0))

        # Snippet
        snippet = note["content"].strip().replace("\n", " ")
        if len(snippet) > 120:
            snippet = snippet[:120] + "..."
        if not snippet:
            snippet = "(Empty page)"

        body_lbl = ctk.CTkLabel(
            card,
            text=snippet,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=self.theme["text_secondary"],
            anchor="w",
            wraplength=700,
            justify="left"
        )
        body_lbl.pack(fill="x", padx=12, pady=(2, 6))

        # Bottom Actions Bar
        actions_bar = ctk.CTkFrame(card, fg_color="transparent")
        actions_bar.pack(fill="x", padx=12, pady=(0, 8))

        date_lbl = ctk.CTkLabel(
            actions_bar,
            text=f"Updated: {note.get('updated_at', '')}",
            font=ctk.CTkFont(size=10),
            text_color=self.theme["text_secondary"]
        )
        date_lbl.pack(side="left")

        # Edit button
        edit_btn = ctk.CTkButton(
            actions_bar,
            text="✏️ Edit",
            width=55,
            height=24,
            font=ctk.CTkFont(size=11),
            fg_color=self.theme["bg_card"],
            hover_color=self.theme["book_cover"],
            command=lambda nid=note["id"]: self._open_edit_note(nid)
        )
        edit_btn.pack(side="right", padx=(4, 0))

        # Delete button
        del_btn = ctk.CTkButton(
            actions_bar,
            text="🗑️",
            width=28,
            height=24,
            font=ctk.CTkFont(size=11),
            fg_color="transparent",
            hover_color=self.theme["danger"],
            command=lambda nid=note["id"]: self._delete_note(nid)
        )
        del_btn.pack(side="right")

    def _open_edit_note(self, note_id: int):
        NotesWindow(
            master=self,
            db=self.db,
            note_id=note_id,
            on_saved=self._refresh_content,
            theme_name=self.theme_name
        )

    def _delete_note(self, note_id: int):
        self.db.delete_note(note_id)
        self._refresh_content()

    def _on_click_new(self):
        NotesWindow(
            master=self,
            db=self.db,
            on_saved=self._refresh_content,
            theme_name=self.theme_name
        )

    # ------------------ Reminders View ------------------
    def _render_reminders_view(self):
        reminders = self.db.get_reminders(include_completed=True)

        if not reminders:
            empty_frame = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
            empty_frame.pack(fill="both", expand=True, pady=40)
            ctk.CTkLabel(
                empty_frame,
                text="⏰ No reminders scheduled.",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=self.theme["text_secondary"]
            ).pack()
            ctk.CTkLabel(
                empty_frame,
                text="Click '➕ New Reminder' to set countdowns and scheduled alarms!",
                font=ctk.CTkFont(size=11),
                text_color=self.theme["text_secondary"]
            ).pack(pady=4)
            return

        for rem in reminders:
            self._create_reminder_card(rem)

    def _create_reminder_card(self, rem: dict):
        is_done = bool(rem.get("is_completed", 0))
        card = ctk.CTkFrame(
            self.content_scroll,
            fg_color=self.theme["bg_secondary"] if not is_done else self.theme["bg_primary"],
            corner_radius=10,
            border_width=1,
            border_color=self.theme["bg_card"]
        )
        card.pack(fill="x", pady=4, padx=4)

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=12, pady=(8, 2))

        # Status icon
        status_icon = "✅" if is_done else "⏰"
        ctk.CTkLabel(hdr, text=status_icon, font=ctk.CTkFont(size=13)).pack(side="left", padx=(0, 6))

        title_lbl = ctk.CTkLabel(
            hdr,
            text=rem["title"],
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=self.theme["text_primary"] if not is_done else self.theme["text_secondary"],
            anchor="w"
        )
        title_lbl.pack(side="left", fill="x", expand=True)

        # Time badge
        time_badge = ctk.CTkLabel(
            hdr,
            text=f"📅 {rem['remind_time']}",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=self.theme["book_cover"] if not is_done else self.theme["bg_card"],
            text_color="#FFFFFF" if not is_done else self.theme["text_secondary"],
            corner_radius=6,
            padx=8,
            pady=2
        )
        time_badge.pack(side="right")

        # Description if any
        desc = rem.get("description", "").strip()
        if desc:
            ctk.CTkLabel(
                card,
                text=desc,
                font=ctk.CTkFont(size=11),
                text_color=self.theme["text_secondary"],
                anchor="w",
                justify="left"
            ).pack(fill="x", padx=12, pady=(2, 4))

        # Bottom Actions
        actions_bar = ctk.CTkFrame(card, fg_color="transparent")
        actions_bar.pack(fill="x", padx=12, pady=(4, 8))

        repeat_text = f"Repeat: {rem.get('repeat_interval', 'none').capitalize()}"
        ctk.CTkLabel(
            actions_bar,
            text=repeat_text,
            font=ctk.CTkFont(size=10),
            text_color=self.theme["text_secondary"]
        ).pack(side="left")

        if not is_done:
            done_btn = ctk.CTkButton(
                actions_bar,
                text="✓ Done",
                width=60,
                height=24,
                font=ctk.CTkFont(size=11),
                fg_color=self.theme["success"],
                hover_color=self.theme["book_spine"],
                command=lambda rid=rem["id"]: self._complete_reminder(rid)
            )
            done_btn.pack(side="right", padx=(4, 0))

            snooze_btn = ctk.CTkButton(
                actions_bar,
                text="💤 +10m",
                width=58,
                height=24,
                font=ctk.CTkFont(size=11),
                fg_color=self.theme["bg_card"],
                hover_color=self.theme["book_cover"],
                command=lambda rid=rem["id"]: self._snooze_reminder(rid)
            )
            snooze_btn.pack(side="right", padx=(4, 0))

        del_btn = ctk.CTkButton(
            actions_bar,
            text="🗑️",
            width=28,
            height=24,
            font=ctk.CTkFont(size=11),
            fg_color="transparent",
            hover_color=self.theme["danger"],
            command=lambda rid=rem["id"]: self._delete_reminder(rid)
        )
        del_btn.pack(side="right")

    def _complete_reminder(self, reminder_id: int):
        self.db.complete_reminder(reminder_id)
        self._refresh_content()

    def _snooze_reminder(self, reminder_id: int):
        self.db.snooze_reminder(reminder_id, minutes=10)
        self._refresh_content()

    def _delete_reminder(self, reminder_id: int):
        self.db.delete_reminder(reminder_id)
        self._refresh_content()

    def _on_click_new_reminder(self):
        ReminderWindow(
            master=self,
            db=self.db,
            on_saved=self._refresh_content,
            theme_name=self.theme_name
        )

    # ------------------ Settings View ------------------
    def _render_settings_view(self):
        box = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        box.pack(fill="both", expand=True, padx=16, pady=16)

        # 1. Book Theme Picker
        ctk.CTkLabel(
            box,
            text="🎨 Book Cover & Accent Style:",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=self.theme["book_accent"]
        ).pack(anchor="w", pady=(0, 6))

        theme_menu = ctk.CTkOptionMenu(
            box,
            values=list(THEMES.keys()),
            width=280,
            height=34,
            fg_color=self.theme["bg_card"],
            command=self._change_theme
        )
        theme_menu.set(self.theme_name)
        theme_menu.pack(anchor="w", pady=(0, 16))

        # 2. Book Widget Size Slider
        curr_size = int(self.db.get_setting("icon_size", 72))
        self.size_lbl = ctk.CTkLabel(
            box,
            text=f"📐 Floating Book Size: {curr_size}px",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=self.theme["book_accent"]
        )
        self.size_lbl.pack(anchor="w", pady=(0, 6))

        size_slider = ctk.CTkSlider(
            box,
            from_=40,
            to=140,
            number_of_steps=20,
            width=280,
            command=self._change_size
        )
        size_slider.set(curr_size)
        size_slider.pack(anchor="w", pady=(0, 6))

        # Quick size presets row
        preset_row = ctk.CTkFrame(box, fg_color="transparent")
        preset_row.pack(anchor="w", pady=(0, 16))

        for lbl, sz in [("Tiny (48px)", 48), ("Small (64px)", 64), ("Medium (80px)", 80), ("Large (100px)", 100), ("Huge (128px)", 128)]:
            ctk.CTkButton(
                preset_row,
                text=lbl,
                font=ctk.CTkFont(size=10),
                height=24,
                fg_color=self.theme["bg_card"],
                hover_color=self.theme["book_cover"],
                command=lambda s=sz, sl=size_slider: (sl.set(s), self._change_size(s))
            ).pack(side="left", padx=2)

        # 3. Floating Book Transparency / Opacity Slider
        curr_op = float(self.db.get_setting("opacity", 0.95))
        self.op_lbl = ctk.CTkLabel(
            box,
            text=f"✨ Floating Widget Opacity: {int(curr_op * 100)}%",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=self.theme["book_accent"]
        )
        self.op_lbl.pack(anchor="w", pady=(0, 6))

        op_slider = ctk.CTkSlider(
            box,
            from_=0.4,
            to=1.0,
            number_of_steps=12,
            width=280,
            command=self._change_opacity
        )
        op_slider.set(curr_op)
        op_slider.pack(anchor="w", pady=(0, 16))

        # 4. Reset Widget Position
        ctk.CTkLabel(
            box,
            text="📍 Floating Book Position:",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=self.theme["book_accent"]
        ).pack(anchor="w", pady=(0, 6))

        reset_pos_btn = ctk.CTkButton(
            box,
            text="Reset Book to Top-Right Corner",
            width=280,
            height=32,
            fg_color=self.theme["bg_card"],
            hover_color=self.theme["book_cover"],
            command=self._reset_position
        )
        reset_pos_btn.pack(anchor="w", pady=(0, 16))

    def _change_size(self, val: float):
        sz = int(val)
        self.size_lbl.configure(text=f"📐 Floating Book Size: {sz}px")
        self.db.set_setting("icon_size", sz)
        if self.on_change_size:
            self.on_change_size(sz)

    def _change_theme(self, new_theme: str):
        self.theme_name = new_theme
        self.theme = THEMES.get(new_theme, THEMES[DEFAULT_THEME])
        self.db.set_setting("theme", new_theme)
        if self.on_theme_changed:
            self.on_theme_changed(new_theme)
        self.destroy()

    def _change_opacity(self, val: float):
        self.op_lbl.configure(text=f"✨ Floating Widget Opacity: {int(val * 100)}%")
        self.db.set_setting("opacity", round(val, 2))
        if self.master and hasattr(self.master, "attributes"):
            try:
                self.master.attributes("-alpha", val)
            except Exception:
                pass

    def _reset_position(self):
        screen_w = self.winfo_screenwidth()
        self.db.set_setting("pos_x", screen_w - 120)
        self.db.set_setting("pos_y", 120)
        if self.master and hasattr(self.master, "geometry"):
            self.master.geometry(f"+{screen_w - 120}+120")

