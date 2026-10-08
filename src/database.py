"""
SQLite Database manager for Notes, Reminders, and Application Settings.
"""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "library_data.db")


class Database:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._memory_conn = None
        if self.db_path == ":memory:":
            self._memory_conn = sqlite3.connect(":memory:", check_same_thread=False)
            self._memory_conn.row_factory = sqlite3.Row
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        if self._memory_conn:
            return self._memory_conn
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Notes Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT DEFAULT 'General',
                    color TEXT DEFAULT '#D4AF37',
                    is_pinned INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Reminders Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    remind_time TEXT NOT NULL,
                    repeat_interval TEXT DEFAULT 'none',
                    is_completed INTEGER DEFAULT 0,
                    is_active INTEGER DEFAULT 1,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Settings Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            
            conn.commit()

    # ------------------- Notes Operations -------------------

    def add_note(self, title: str, content: str, category: str = "General", color: str = "#D4AF37", is_pinned: bool = False) -> int:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO notes (title, content, category, color, is_pinned, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (title.strip() or "Untitled Page", content, category, color, 1 if is_pinned else 0, now, now))
            conn.commit()
            return cursor.lastrowid

    def update_note(self, note_id: int, title: str, content: str, category: str = "General", color: str = "#D4AF37", is_pinned: bool = False) -> bool:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE notes 
                SET title = ?, content = ?, category = ?, color = ?, is_pinned = ?, updated_at = ?
                WHERE id = ?
            """, (title.strip() or "Untitled Page", content, category, color, 1 if is_pinned else 0, now, note_id))
            conn.commit()
            return cursor.rowcount > 0

    def delete_note(self, note_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_notes(self, search_query: str = "", category: str = "All") -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM notes WHERE 1=1"
            params = []
            
            if category and category != "All":
                query += " AND category = ?"
                params.append(category)
                
            if search_query:
                query += " AND (title LIKE ? OR content LIKE ?)"
                search_param = f"%{search_query}%"
                params.extend([search_param, search_param])
                
            query += " ORDER BY is_pinned DESC, updated_at DESC"
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_note_by_id(self, note_id: int) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    # ------------------- Reminders Operations -------------------

    def add_reminder(self, title: str, remind_time: str, description: str = "", repeat_interval: str = "none") -> int:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO reminders (title, description, remind_time, repeat_interval, is_completed, is_active, created_at)
                VALUES (?, ?, ?, ?, 0, 1, ?)
            """, (title.strip() or "Reminder", description, remind_time, repeat_interval, now))
            conn.commit()
            return cursor.lastrowid

    def update_reminder(self, reminder_id: int, title: str, remind_time: str, description: str = "", repeat_interval: str = "none") -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE reminders
                SET title = ?, description = ?, remind_time = ?, repeat_interval = ?, is_completed = 0, is_active = 1
                WHERE id = ?
            """, (title.strip() or "Reminder", description, remind_time, repeat_interval, reminder_id))
            conn.commit()
            return cursor.rowcount > 0

    def delete_reminder(self, reminder_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
            conn.commit()
            return cursor.rowcount > 0

    def complete_reminder(self, reminder_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Check repeat interval
            cursor.execute("SELECT * FROM reminders WHERE id = ?", (reminder_id,))
            row = cursor.fetchone()
            if not row:
                return False
                
            repeat = row["repeat_interval"]
            if repeat == "daily":
                # Schedule next day
                curr_time = datetime.strptime(row["remind_time"], "%Y-%m-%d %H:%M:%S")
                next_time = (curr_time + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("UPDATE reminders SET remind_time = ?, is_completed = 0, is_active = 1 WHERE id = ?", (next_time, reminder_id))
            elif repeat == "weekly":
                # Schedule next week
                curr_time = datetime.strptime(row["remind_time"], "%Y-%m-%d %H:%M:%S")
                next_time = (curr_time + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("UPDATE reminders SET remind_time = ?, is_completed = 0, is_active = 1 WHERE id = ?", (next_time, reminder_id))
            else:
                cursor.execute("UPDATE reminders SET is_completed = 1, is_active = 0 WHERE id = ?", (reminder_id,))
                
            conn.commit()
            return True

    def snooze_reminder(self, reminder_id: int, minutes: int = 5) -> bool:
        new_time = (datetime.now() + timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE reminders SET remind_time = ?, is_active = 1 WHERE id = ?", (new_time, reminder_id))
            conn.commit()
            return cursor.rowcount > 0

    def get_pending_due_reminders(self, current_time_str: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM reminders 
                WHERE is_completed = 0 AND is_active = 1 AND remind_time <= ?
                ORDER BY remind_time ASC
            """, (current_time_str,))
            return [dict(row) for row in cursor.fetchall()]

    def get_reminders(self, include_completed: bool = True) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if include_completed:
                cursor.execute("SELECT * FROM reminders ORDER BY is_completed ASC, remind_time ASC")
            else:
                cursor.execute("SELECT * FROM reminders WHERE is_completed = 0 ORDER BY remind_time ASC")
            return [dict(row) for row in cursor.fetchall()]

    # ------------------- Settings Operations -------------------

    def get_setting(self, key: str, default: Any = None) -> Any:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row["value"] if row else default

    def set_setting(self, key: str, value: Any):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO settings (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """, (key, str(value)))
            conn.commit()
