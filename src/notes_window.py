"""
Journal & Quick Note Editor Window (Book-Styled Page Layout).
"""

import customtkinter as ctk
from PIL import ImageTk
from typing import Callable, Optional, Dict, Any
from src.database import Database
from src.theme import THEMES, DEFAULT_THEME, NOTE_CATEGORIES
from src.book_graphics import generate_book_image


class NotesWindow(ctk.CTkToplevel):
    """
    Book & Journal-styled quick note taking interface.
    """
    def __init__(
        self,
        master,
        db: Database,
        note_id: Optional[int] = None,
        on_saved: Optional[Callable] = None,
        theme_name: str = DEFAULT_THEME
    ):
        super().__init__(master)
        self.db = db
        self.note_id = note_id
        self.on_saved = on_saved
        self.theme_name = theme_name
        self.theme = THEMES.get(theme_name, THEMES[DEFAULT_THEME])

        self.title("📝 Quick Journal Page")
        self.geometry("560x620")
        self.attributes("-topmost", True)
        self.configure(fg_color=self.theme["bg_primary"])

        # Center window
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - 560) // 2
        y = (screen_h - 620) // 2
        self.geometry(f"560x620+{x}+{y}")

        self.selected_category = "General"
        self.selected_color = "#D4AF37"
        self.is_pinned = False

        self._build_ui()
        self._load_note_data()

    def _build_ui(self):
        # Outer Book Frame
        book_frame = ctk.CTkFrame(
            self,
            fg_color=self.theme["bg_secondary"],
            corner_radius=16,
            border_width=2,
            border_color=self.theme["book_accent"]
        )
        book_frame.pack(fill="both", expand=True, padx=14, pady=14)

        # 1. Top Header Bar
        header = ctk.CTkFrame(book_frame, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(12, 6))

        # Mini Book Icon
        book_pil = generate_book_image(size=36, theme_name=self.theme_name, is_hovered=False)
        self.book_img = ImageTk.PhotoImage(book_pil)
        icon_lbl = ctk.CTkLabel(header, image=self.book_img, text="")
        icon_lbl.pack(side="left", padx=(0, 8))

        title_lbl = ctk.CTkLabel(
            header,
            text="JOURNAL NOTE PAD",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=self.theme["book_accent"]
        )
        title_lbl.pack(side="left")

        # Top Right Actions: Pin & Close
        self.pin_btn = ctk.CTkButton(
            header,
            text="📌 Pin",
            width=64,
            height=28,
            fg_color=self.theme["bg_card"],
            hover_color=self.theme["book_accent"],
            font=ctk.CTkFont(size=11),
            command=self._toggle_pin
        )
        self.pin_btn.pack(side="right", padx=(6, 0))

        # 2. Note Title Entry
        self.title_entry = ctk.CTkEntry(
            book_frame,
            placeholder_text="Enter note title (e.g. Project Ideas, Grocery List...)",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            fg_color=self.theme["bg_primary"],
            border_color=self.theme["bg_card"],
            height=38,
            corner_radius=8
        )
        self.title_entry.pack(fill="x", padx=16, pady=(6, 8))

        # 3. Category Tags Selector Row
        tag_scroll = ctk.CTkScrollableFrame(
            book_frame,
            fg_color="transparent",
            orientation="horizontal",
            height=36
        )
        tag_scroll.pack(fill="x", padx=16, pady=(0, 8))

        self.category_buttons = {}
        for cat in NOTE_CATEGORIES:
            btn = ctk.CTkButton(
                tag_scroll,
                text=f"{cat['icon']} {cat['name']}",
                font=ctk.CTkFont(size=11),
                height=26,
                fg_color=self.theme["bg_card"] if cat["name"] != self.selected_category else self.theme["book_cover"],
                hover_color=self.theme["book_cover"],
                corner_radius=13,
                command=lambda c=cat["name"], col=cat["color"]: self._select_category(c, col)
            )
            btn.pack(side="left", padx=3)
            self.category_buttons[cat["name"]] = btn

        # 4. Parchment Page Text Editor
        page_box = ctk.CTkFrame(
            book_frame,
            fg_color=self.theme["page_bg"],
            corner_radius=12,
            border_width=1,
            border_color=self.theme["page_lines"]
        )
        page_box.pack(fill="both", expand=True, padx=16, pady=4)

        self.text_area = ctk.CTkTextbox(
            page_box,
            fg_color=self.theme["page_bg"],
            text_color=self.theme["text_page"],
            font=ctk.CTkFont(family="Georgia", size=13),
            wrap="word",
            corner_radius=10,
            border_width=0
        )
        self.text_area.pack(fill="both", expand=True, padx=8, pady=8)
        self.text_area.bind("<KeyRelease>", self._on_text_change)

        # 5. Bottom Status and Actions
        bottom_bar = ctk.CTkFrame(book_frame, fg_color="transparent")
        bottom_bar.pack(fill="x", padx=16, pady=(10, 12))

        self.status_lbl = ctk.CTkLabel(
            bottom_bar,
            text="0 words • 0 characters",
            font=ctk.CTkFont(size=11),
            text_color=self.theme["text_secondary"]
        )
        self.status_lbl.pack(side="left")

        # Copy button
        copy_btn = ctk.CTkButton(
            bottom_bar,
            text="📋 Copy",
            width=68,
            height=32,
            fg_color=self.theme["bg_card"],
            hover_color=self.theme["bg_primary"],
            font=ctk.CTkFont(size=11),
            command=self._copy_content
        )
        copy_btn.pack(side="left", padx=(12, 0))

        # Save Button
        save_btn = ctk.CTkButton(
            bottom_bar,
            text="💾 Save Page",
            width=100,
            height=32,
            fg_color=self.theme["book_cover"],
            hover_color=self.theme["book_spine"],
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._save_note
        )
        save_btn.pack(side="right")

    def _select_category(self, cat_name: str, color_hex: str):
        self.selected_category = cat_name
        self.selected_color = color_hex
        for name, btn in self.category_buttons.items():
            if name == cat_name:
                btn.configure(fg_color=self.theme["book_cover"])
            else:
                btn.configure(fg_color=self.theme["bg_card"])

    def _toggle_pin(self):
        self.is_pinned = not self.is_pinned
        if self.is_pinned:
            self.pin_btn.configure(fg_color=self.theme["book_accent"], text_color="#000000")
        else:
            self.pin_btn.configure(fg_color=self.theme["bg_card"], text_color=self.theme["text_primary"])

    def _on_text_change(self, event=None):
        content = self.text_area.get("1.0", "end-1c")
        words = len(content.split()) if content.strip() else 0
        chars = len(content)
        self.status_lbl.configure(text=f"{words} words • {chars} characters")

    def _copy_content(self):
        content = self.text_area.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(content)
        self.status_lbl.configure(text="✓ Copied to clipboard!")

    def _load_note_data(self):
        if self.note_id:
            note = self.db.get_note_by_id(self.note_id)
            if note:
                self.title_entry.insert(0, note["title"])
                self.text_area.insert("1.0", note["content"])
                self.selected_category = note.get("category", "General")
                self.selected_color = note.get("color", "#D4AF37")
                self.is_pinned = bool(note.get("is_pinned", 0))
                self._select_category(self.selected_category, self.selected_color)
                if self.is_pinned:
                    self.pin_btn.configure(fg_color=self.theme["book_accent"], text_color="#000000")
                self._on_text_change()

    def _save_note(self):
        title = self.title_entry.get().strip() or "Untitled Note"
        content = self.text_area.get("1.0", "end-1c")

        if not content.strip() and not title:
            self.destroy()
            return

        if self.note_id:
            self.db.update_note(
                note_id=self.note_id,
                title=title,
                content=content,
                category=self.selected_category,
                color=self.selected_color,
                is_pinned=self.is_pinned
            )
        else:
            self.db.add_note(
                title=title,
                content=content,
                category=self.selected_category,
                color=self.selected_color,
                is_pinned=self.is_pinned
            )

        if self.on_saved:
            self.on_saved()
        self.destroy()

