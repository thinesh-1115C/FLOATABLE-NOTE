"""
Automated unit and integration test suite for the Book-Shaped Notes & Reminders App.
"""

import unittest
from datetime import datetime, timedelta
from src.database import Database
from src.book_graphics import generate_book_image, generate_app_icon
from src.theme import THEMES, NOTE_CATEGORIES


class TestBookApp(unittest.TestCase):
    def setUp(self):
        # Use an in-memory database for fast, isolated, lock-free tests
        self.db = Database(":memory:")

    def test_database_notes_crud(self):
        # 1. Add Notes
        n1 = self.db.add_note(
            title="Book Chapter 1",
            content="Once upon a time in coding world...",
            category="Ideas",
            color="#A855F7",
            is_pinned=True
        )
        n2 = self.db.add_note(
            title="Meeting Notes",
            content="Discussing the new release schedule.",
            category="Work",
            color="#38BDF8",
            is_pinned=False
        )
        self.assertTrue(n1 > 0)
        self.assertTrue(n2 > 0)

        # 2. Get Notes
        notes = self.db.get_notes()
        self.assertEqual(len(notes), 2)
        # Pinned should be first
        self.assertEqual(notes[0]["title"], "Book Chapter 1")
        self.assertEqual(notes[0]["is_pinned"], 1)

        # 3. Search Notes
        search_res = self.db.get_notes(search_query="coding")
        self.assertEqual(len(search_res), 1)
        self.assertEqual(search_res[0]["title"], "Book Chapter 1")

        # 4. Filter by Category
        work_notes = self.db.get_notes(category="Work")
        self.assertEqual(len(work_notes), 1)
        self.assertEqual(work_notes[0]["title"], "Meeting Notes")

        # 5. Update Note
        upd = self.db.update_note(
            note_id=n1,
            title="Book Chapter 1 Revised",
            content="Updated content...",
            category="Ideas",
            color="#A855F7",
            is_pinned=False
        )
        self.assertTrue(upd)
        updated_note = self.db.get_note_by_id(n1)
        self.assertEqual(updated_note["title"], "Book Chapter 1 Revised")
        self.assertEqual(updated_note["content"], "Updated content...")

        # 6. Delete Note
        del_res = self.db.delete_note(n2)
        self.assertTrue(del_res)
        self.assertEqual(len(self.db.get_notes()), 1)

    def test_database_reminders_crud_and_snooze(self):
        # 1. Add Reminder
        future_time = (datetime.now() + timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
        r1 = self.db.add_reminder(
            title="Check Oven",
            remind_time=future_time,
            description="Pizza is baking",
            repeat_interval="none"
        )
        self.assertTrue(r1 > 0)

        # 2. Check pending due reminders
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pending = self.db.get_pending_due_reminders(now_str)
        self.assertEqual(len(pending), 0)

        # Query with future timestamp to simulate time arrival
        sim_future = (datetime.now() + timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S")
        pending = self.db.get_pending_due_reminders(sim_future)
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]["title"], "Check Oven")

        # 3. Snooze Reminder
        snoozed = self.db.snooze_reminder(r1, minutes=5)
        self.assertTrue(snoozed)

        # 4. Complete Reminder
        comp = self.db.complete_reminder(r1)
        self.assertTrue(comp)
        active_rems = self.db.get_reminders(include_completed=False)
        self.assertEqual(len(active_rems), 0)

    def test_repeating_reminders(self):
        # Daily repeat test
        start_time = "2026-10-08 09:00:00"
        r_daily = self.db.add_reminder(
            title="Daily Standup",
            remind_time=start_time,
            repeat_interval="daily"
        )
        self.assertTrue(r_daily > 0)
        
        # Complete should advance it by 1 day and keep active
        self.db.complete_reminder(r_daily)
        rems = self.db.get_reminders(include_completed=False)
        self.assertEqual(len(rems), 1)
        self.assertEqual(rems[0]["remind_time"], "2026-10-09 09:00:00")
        self.assertEqual(rems[0]["is_active"], 1)

    def test_settings(self):
        self.db.set_setting("theme", "Midnight Blue")
        self.assertEqual(self.db.get_setting("theme"), "Midnight Blue")
        self.db.set_setting("opacity", "0.85")
        self.assertEqual(self.db.get_setting("opacity"), "0.85")
        self.db.set_setting("pos_x", "500")
        self.assertEqual(self.db.get_setting("pos_x"), "500")

    def test_book_graphics_generation(self):
        for theme_name in THEMES.keys():
            # Test normal book
            img_normal = generate_book_image(size=80, theme_name=theme_name, is_hovered=False)
            self.assertEqual(img_normal.size, (80, 80))
            self.assertEqual(img_normal.mode, "RGBA")

            # Test hover book
            img_hover = generate_book_image(size=80, theme_name=theme_name, is_hovered=True)
            self.assertEqual(img_hover.size, (80, 80))

        # Test app icon
        app_icon = generate_app_icon(size=128)
        self.assertEqual(app_icon.size, (128, 128))

    def test_categories_integrity(self):
        cat_names = [c["name"] for c in NOTE_CATEGORIES]
        self.assertIn("General", cat_names)
        self.assertIn("Ideas", cat_names)
        self.assertIn("Work", cat_names)
        self.assertIn("Personal", cat_names)
        self.assertIn("Urgent", cat_names)
        self.assertIn("Study", cat_names)


if __name__ == "__main__":
    unittest.main()

