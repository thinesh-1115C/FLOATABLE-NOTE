"""
Short 3-Line Quick Note Jotter Pad (Compact Sticky-Note Window).
"""

import customtkinter as ctk
from PIL import ImageTk
from typing import Callable, Optional
from src.database import Database
from src.theme import THEMES, DEFAULT_THEME
from src.book_graphics import generate_note_logo


class NotesWindow(ctk.CTkToplevel):
    """
    Short, compact 3-line quick note jotter pad.
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

        self.title("📝 Quick Note")
        self.geometry("360x170")
        self.attributes("-topmost", True)
        self.resizable(False, False)
        self.configure(fg_color=self.theme["bg_primary"])

        # Center on screen
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - 360) // 2
        y = (screen_h - 170) // 2
        self.geometry(f"360x170+{x}+{y}")

        self._build_ui()
        self._load_note_data()

    def _build_ui(self):
        # Outer Card with Gold/Accent Border
        card = ctk.CTkFrame(
            self,
            fg_color=self.theme["bg_secondary"],
            corner_radius=12,
            border_width=2,
            border_color=self.theme["book_accent"]
        )
        card.pack(fill="both", expand=True, padx=6, pady=6)

        # Header Bar
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=10, pady=(6, 4))

        # Mini Note Logo
        logo_pil = generate_note_logo(size=22, theme_name=self.theme_name, is_hovered=True)
        self.logo_img = ImageTk.PhotoImage(logo_pil)
        icon_lbl = ctk.CTkLabel(header, image=self.logo_img, text="")
        icon_lbl.pack(side="left", padx=(0, 6))

        title_lbl = ctk.CTkLabel(
            header,
            text="QUICK NOTE (3 LINES)",
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

        # 3-Line Text Editor Box
        page_box = ctk.CTkFrame(
            card,
            fg_color=self.theme["page_bg"],
            corner_radius=8,
            border_width=1,
            border_color=self.theme["page_lines"]
        )
        page_box.pack(fill="x", padx=10, pady=(0, 6))

        # Precisely 3-lines text area (height=68)
        self.text_area = ctk.CTkTextbox(
            page_box,
            fg_color=self.theme["page_bg"],
            text_color=self.theme["text_page"],
            font=ctk.CTkFont(family="Georgia", size=12),
            height=68,
            wrap="word",
            corner_radius=6,
            border_width=0
        )
        self.text_area.pack(fill="x", padx=4, pady=4)
        self.text_area.focus_set()

        # Keyboard shortcuts: Ctrl+Enter to save instantly
        self.text_area.bind("<Control-Return>", lambda e: self._save_note())

        # Bottom Bar with Hint & Mini Save Button
        bottom_bar = ctk.CTkFrame(card, fg_color="transparent")
        bottom_bar.pack(fill="x", padx=10, pady=(0, 6))

        hint_lbl = ctk.CTkLabel(
            bottom_bar,
            text="Ctrl+Enter to save",
            font=ctk.CTkFont(size=9),
            text_color=self.theme["text_secondary"]
        )
        hint_lbl.pack(side="left")

        save_btn = ctk.CTkButton(
            bottom_bar,
            text="💾 Save",
            width=70,
            height=24,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=self.theme["book_cover"],
            hover_color=self.theme["book_spine"],
            corner_radius=6,
            command=self._save_note
        )
        save_btn.pack(side="right")

    def _load_note_data(self):
        if self.note_id:
            note = self.db.get_note_by_id(self.note_id)
            if note:
                self.text_area.insert("1.0", note["content"])

    def _save_note(self):
        content = self.text_area.get("1.0", "end-1c").strip()
        if not content:
            self.destroy()
            return

        # Generate smart title from first line / first few words
        first_line = content.split("\n")[0].strip()
        title = first_line[:35] + ("..." if len(first_line) > 35 else "")
        if not title:
            title = "Quick Note"

        if self.note_id:
            self.db.update_note(
                note_id=self.note_id,
                title=title,
                content=content,
                category="General",
                color="#D4AF37",
                is_pinned=False
            )
        else:
            self.db.add_note(
                title=title,
                content=content,
                category="General",
                color="#D4AF37",
                is_pinned=False
            )

        if self.on_saved:
            self.on_saved()
        self.destroy()
