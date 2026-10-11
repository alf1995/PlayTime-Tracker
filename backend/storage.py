"""SQLite persistence. All statements are parametrized and backend uses one task lock."""
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

from .exporter import export_database
from .schema import SCHEMA_SQL

DEFAULTS = {
    "language": "auto", "daily_limit_minutes": 120,
    "break_interval_minutes": 60, "notifications": True,
    "tracking_enabled": True,
}

class Storage:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(self.path), isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA busy_timeout=3000")
        self._init()

    def _init(self):
        self.db.executescript(SCHEMA_SQL)
        self.db.execute("UPDATE sessions SET ended_ms=COALESCE((SELECT MAX(end_ms) FROM active_intervals WHERE session_id=sessions.id),started_ms), ended_reason='backend_restart' WHERE ended_ms IS NULL")
        for key, value in DEFAULTS.items():
            self.db.execute("INSERT OR IGNORE INTO settings(key,value) VALUES(?,?)", (key,json.dumps(value)))

    def close(self):
        self.db.close()

    def get_settings(self):
        return {row["key"]: json.loads(row["value"]) for row in self.db.execute("SELECT key,value FROM settings")}

    def set_setting(self, key, value):
        if key not in DEFAULTS:
            raise ValueError("Unsupported setting")
        if key == "language" and value not in ("auto", "en", "es"):
            raise ValueError("Unsupported language")
        if key in ("notifications", "tracking_enabled") and type(value) is not bool:
            raise ValueError("Expected boolean")
        if key in ("daily_limit_minutes", "break_interval_minutes") and (type(value) is not int or value < 0 or value > 1440):
            raise ValueError("Expected minutes in 0..1440")
        self.db.execute("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key,json.dumps(value)))
        return self.get_settings()

    def start_session(self, appid, name, at_ms):
        self.db.execute("INSERT INTO games(appid,name,last_seen_ms) VALUES(?,?,?) ON CONFLICT(appid) DO UPDATE SET name=excluded.name,last_seen_ms=excluded.last_seen_ms", (appid,name,at_ms))
        cursor = self.db.execute("INSERT INTO sessions(appid,started_ms) VALUES(?,?)", (appid,at_ms))
        return cursor.lastrowid

    def end_session(self, sid, at_ms, reason):
        self.db.execute("UPDATE sessions SET ended_ms=?,ended_reason=? WHERE id=? AND ended_ms IS NULL", (at_ms, reason, sid))

    def new_interval(self, sid, start_ms):
        cursor = self.db.execute("INSERT INTO active_intervals(session_id,start_ms,end_ms,duration_ms) VALUES(?,?,?,0)", (sid,start_ms,start_ms))
        return cursor.lastrowid

    def update_interval(self, interval_id, end_ms, duration_ms):
        self.db.execute("UPDATE active_intervals SET end_ms=?,duration_ms=? WHERE id=? AND duration_ms <= ?", (end_ms,duration_ms,interval_id,duration_ms))

    def add_energy_sample(self, sid, at_ms, watts):
        self.db.execute("INSERT INTO energy_samples(session_id,recorded_ms,watts,source) VALUES(?,?,?,'battery_discharge_sysfs')", (sid, at_ms, watts))

    def mark_notification(self, key, now_ms):
        cursor = self.db.execute("INSERT OR IGNORE INTO notification_history(notification_key,created_ms) VALUES(?,?)", (key,now_ms))
        return cursor.rowcount == 1

    def total_ms(self, appid=None, start_ms=None, end_ms=None):
        """Query with local-day overlap, prorating duration only on overlap."""
        sql = "SELECT a.start_ms,a.end_ms,a.duration_ms FROM active_intervals a JOIN sessions s ON a.session_id=s.id WHERE 1=1"
        args = []
        if appid is not None:
            sql += " AND s.appid=?"; args.append(str(appid))
        if start_ms is not None:
            sql += " AND a.end_ms>?"; args.append(start_ms)
        if end_ms is not None:
            sql += " AND a.start_ms<?"; args.append(end_ms)
        result = 0
        for row in self.db.execute(sql,args):
            duration = row["duration_ms"]
            if not start_ms and not end_ms:
                result += duration; continue
            a = row["start_ms"]; b = row["end_ms"]
            total_wall = max(1,b-a)
            overlap = max(0, min(b, end_ms if end_ms is not None else b) - max(a, start_ms if start_ms is not None else a))
            result += round(duration * min(1.0,overlap/total_wall))
        return result

    def series(self, days=7, appid=None):
        today = datetime.now().astimezone().date()
        values = []
        for delta in range(days-1,-1,-1):
            day = today - timedelta(days=delta)
            start = datetime.combine(day, datetime.min.time()).astimezone()
            end = datetime.combine(day+timedelta(days=1),datetime.min.time()).astimezone()
            values.append({"day": day.isoformat(),"ms": self.total_ms(appid,int(start.timestamp()*1000),int(end.timestamp()*1000))})
        return values

    def summary(self, appid=None):
        today = datetime.now().astimezone().date()
        since = lambda day: int(datetime.combine(day,datetime.min.time()).astimezone().timestamp()*1000)
        first_month = today.replace(day=1)
        first_week = today-timedelta(days=today.weekday())
        first_year = today.replace(month=1,day=1)
        end = since(today+timedelta(days=1))
        return {"today_ms":self.total_ms(appid,since(today),end),
                "week_ms":self.total_ms(appid,since(first_week),end),
                "month_ms":self.total_ms(appid,since(first_month),end),
                "year_ms":self.total_ms(appid,since(first_year),end),
                "total_ms":self.total_ms(appid)}

    def games(self):
        return [dict(row) for row in self.db.execute("""
            SELECT g.appid,g.name,g.last_seen_ms,COUNT(DISTINCT s.id) AS sessions,
                   COALESCE(SUM(a.duration_ms),0) AS total_ms
            FROM games g LEFT JOIN sessions s ON s.appid=g.appid
            LEFT JOIN active_intervals a ON a.session_id=s.id
            GROUP BY g.appid ORDER BY total_ms DESC,g.last_seen_ms DESC
        """)]

    def detail(self, appid):
        game = self.db.execute("SELECT * FROM games WHERE appid=?",(str(appid),)).fetchone()
        if not game: return None
        recent = [dict(row) for row in self.db.execute("""
        SELECT s.id,s.started_ms,s.ended_ms,s.ended_reason,COALESCE(SUM(a.duration_ms),0) AS duration_ms
        FROM sessions s LEFT JOIN active_intervals a ON a.session_id=s.id
        WHERE s.appid=? GROUP BY s.id ORDER BY s.started_ms DESC LIMIT 30
        """,(str(appid),))]
        samples = self.db.execute("""
        SELECT COUNT(*) AS n, ROUND(AVG(e.watts),2) AS avg_watts
        FROM energy_samples e JOIN sessions s ON e.session_id=s.id WHERE s.appid=?
        """,(str(appid),)).fetchone()
        return {"game":dict(game),"summary":self.summary(str(appid)),"series":self.series(7,str(appid)),
                "sessions":recent,"energy":{"samples":samples["n"],"avg_watts":samples["avg_watts"],"source":"battery_discharge_sysfs"}}

    def export(self, fmt, folder):
        return export_database(self.db, fmt, folder)
