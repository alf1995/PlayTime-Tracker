import csv
import re
import tempfile
import unittest
from pathlib import Path

from backend.storage import Storage

ROOT = Path(__file__).resolve().parents[1]


class RefactorRegressionTest(unittest.TestCase):
    def test_localizations_have_matching_keys(self):
        pattern = re.compile(r'^\s+([a-zA-Z]\w*):\s*"', re.MULTILINE)
        english = pattern.findall((ROOT / "src/i18n/en.ts").read_text(encoding="utf-8"))
        spanish = pattern.findall((ROOT / "src/i18n/es.ts").read_text(encoding="utf-8"))
        self.assertGreater(len(english), 50)
        self.assertEqual(english, spanish)

    def test_history_survives_reopening_database(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "playtime.sqlite3"
            store = Storage(path)
            session_id = store.start_session("570", "Dota 2", 1700000000000)
            interval_id = store.new_interval(session_id, 1700000000000)
            store.update_interval(interval_id, 1700000120000, 120000)
            store.end_session(session_id, 1700000120000, "game_not_detected")
            store.close()

            reopened = Storage(path)
            self.assertEqual(reopened.detail("570")["summary"]["total_ms"], 120000)
            self.assertEqual(reopened.games()[0]["sessions"], 1)
            reopened.close()

    def test_csv_export_prevents_spreadsheet_formulas(self):
        with tempfile.TemporaryDirectory() as folder:
            store = Storage(Path(folder) / "playtime.sqlite3")
            store.start_session("570", '=HYPERLINK("example.com")', 1700000000000)
            exported = store.export("csv", Path(folder) / "exports")
            with open(exported, encoding="utf-8", newline="") as handle:
                rows = list(csv.reader(handle))
            self.assertTrue(rows[1][2].startswith("'=HYPERLINK"))
            store.close()
