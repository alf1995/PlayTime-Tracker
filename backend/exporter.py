"""Local JSON/CSV exports."""

import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path

EXPORT_TABLES = (
    "games", "sessions", "active_intervals", "energy_samples", "settings", "notification_history"
)


def _csv_safe(value):
    if isinstance(value, str) and value.startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def export_database(db, fmt, folder):
    if fmt not in ("json", "csv"):
        raise ValueError("Unsupported format")

    destination = Path(folder)
    destination.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = destination / ("playtime_%s_%s.%s" % (stamp, int(time.time_ns() % 1_000_000), fmt))

    if fmt == "json":
        data = {
            "version": 1,
            "exported_at_utc": datetime.now(timezone.utc).isoformat(),
            "tables": {
                table: [dict(row) for row in db.execute("SELECT * FROM " + table)]
                for table in EXPORT_TABLES
            },
        }
        with path.open("x", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
        return str(path)

    with path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "session_id", "appid", "game", "started_utc_ms",
            "ended_utc_ms", "duration_ms", "reason",
        ])
        rows = db.execute("""
            SELECT s.id, s.appid, g.name, s.started_ms, s.ended_ms,
                   COALESCE(SUM(a.duration_ms), 0) AS duration_ms,
                   s.ended_reason
            FROM sessions s
            JOIN games g ON g.appid = s.appid
            LEFT JOIN active_intervals a ON a.session_id = s.id
            GROUP BY s.id
            ORDER BY s.started_ms
        """)
        for row in rows:
            writer.writerow([_csv_safe(value) for value in tuple(row)])

    return str(path)
