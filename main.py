"""Decky Loader entrypoint for PlayTime Tracker."""

import os
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

import decky

from backend.storage import Storage
from backend.tracker import PlayTimeTracker


class Plugin:
    async def _main(self):
        runtime = os.environ.get("DECKY_PLUGIN_RUNTIME_DIR", decky.DECKY_PLUGIN_RUNTIME_DIR)
        self.state_dir = Path(runtime)
        self.state_dir.mkdir(parents=True, exist_ok=True)

        decky.logger.info("PlayTime Tracker initialization: plugin=%s state=%s", PLUGIN_ROOT, self.state_dir)
        self.store = Storage(self.state_dir / "playtime.sqlite3")
        self.tracker = PlayTimeTracker(self.store, emitter=decky.emit, logger=decky.logger)
        self.tracker.detector.home = Path(getattr(decky, "DECKY_USER_HOME", os.path.expanduser("~")))
        await self.tracker.start()
        decky.logger.info("PlayTime Tracker started")

    async def _unload(self):
        if hasattr(self, "tracker"):
            await self.tracker.stop()
        if hasattr(self, "store"):
            self.store.close()

    async def _uninstall(self):
        pass

    async def backend_health(self):
        return {
            "initialized": hasattr(self, "store") and hasattr(self, "tracker"),
            "data_folder": str(getattr(self, "state_dir", "")),
        }

    async def get_dashboard(self):
        return {
            "summary": self.store.summary(),
            "series": self.store.series(7),
            "games": self.store.games()[:15],
            "tracker": self.tracker.snapshot(),
            "settings": self.store.get_settings(),
        }

    async def get_game_detail(self, appid: str):
        if not str(appid).isdigit():
            return None
        return self.store.detail(str(appid))

    async def update_setting(self, key: str, value):
        return self.store.set_setting(key, value)

    async def set_paused(self, paused: bool):
        return await self.tracker.set_paused(paused)

    async def export_data(self, fmt: str):
        return {"path": self.store.export(fmt, self.state_dir / "exports")}

    async def diagnostics(self):
        state = self.tracker.snapshot()
        return {
            "platform": os.uname().sysname,
            "machine": os.uname().machine,
            "data_folder": str(self.state_dir),
            "tracking": state,
            "database_size_bytes": (self.state_dir / "playtime.sqlite3").stat().st_size,
        }
