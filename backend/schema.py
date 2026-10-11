SCHEMA_SQL = """
        CREATE TABLE IF NOT EXISTS schema_migrations(version INTEGER PRIMARY KEY);
        CREATE TABLE IF NOT EXISTS games(
          appid TEXT PRIMARY KEY, name TEXT NOT NULL, last_seen_ms INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS sessions(
          id INTEGER PRIMARY KEY AUTOINCREMENT, appid TEXT NOT NULL,
          started_ms INTEGER NOT NULL, ended_ms INTEGER,
          ended_reason TEXT, FOREIGN KEY(appid) REFERENCES games(appid));
        CREATE TABLE IF NOT EXISTS active_intervals(
          id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER NOT NULL,
          start_ms INTEGER NOT NULL, end_ms INTEGER NOT NULL,
          duration_ms INTEGER NOT NULL DEFAULT 0 CHECK(duration_ms >= 0),
          FOREIGN KEY(session_id) REFERENCES sessions(id));
        CREATE INDEX IF NOT EXISTS idx_intervals_dates ON active_intervals(start_ms,end_ms);
        CREATE INDEX IF NOT EXISTS idx_sessions_app ON sessions(appid,started_ms);
        CREATE TABLE IF NOT EXISTS energy_samples(
          id INTEGER PRIMARY KEY AUTOINCREMENT, session_id INTEGER NOT NULL,
          recorded_ms INTEGER NOT NULL, watts REAL NOT NULL,
          source TEXT NOT NULL, FOREIGN KEY(session_id) REFERENCES sessions(id));
        CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS notification_history(
          notification_key TEXT PRIMARY KEY, created_ms INTEGER NOT NULL);
        INSERT OR IGNORE INTO schema_migrations(version) VALUES (1);
        """
