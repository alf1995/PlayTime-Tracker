"""Best-effort Steam game detection without privileged/private Steam APIs.

Only Linux /proc environment variables are used; they identify a *running*
Steam game process, not necessarily a focused/interactive game. The UI states
this explicitly. No arbitrary user-supplied shell commands are executed.
"""
from __future__ import annotations
import os
import re
from pathlib import Path
from typing import Dict, Optional

PID_RE = re.compile(r"^\d+$")
ACF_NAME_RE = re.compile(r'^\s*"name"\s+"(.*)"\s*$', re.I)
APP_IDS = (b"SteamAppId", b"SteamGameId", b"STEAM_COMPAT_APP_ID")
# Common Steam/Proton helpers can linger after the actual game exits.
HELPERS = (
    "steamwebhelper", "steam.exe", "steam", "wineserver", "winedevice.exe",
    "services.exe", "explorer.exe", "rpcss.exe", "start.exe", "conhost.exe",
    "reaper", "pressure-vessel", "pv-bwrap", "gamemoderun", "steam-runtime",
    "crashhandler", "crashpad", "gameoverlayui", "steamservice",
)


class GameDetector:
    def __init__(self, proc_path: str = "/proc", home: Optional[str] = None):
        self.proc_path = Path(proc_path)
        self.home = Path(home or os.path.expanduser("~"))
        self.names: Dict[str, str] = {}
        self.problem: Optional[str] = None

    def _name(self, appid: str) -> str:
        if appid in self.names:
            return self.names[appid]
        roots = [
            self.home / ".local/share/Steam/steamapps",
            self.home / ".steam/steam/steamapps",
            self.home / ".steam/root/steamapps",
        ]
        for base in roots:
            filename = base / ("appmanifest_%s.acf" % appid)
            try:
                text = filename.read_text(encoding="utf-8", errors="replace")
            except (OSError, UnicodeError):
                continue
            for line in text.splitlines():
                match = ACF_NAME_RE.match(line)
                if match:
                    self.names[appid] = match.group(1)
                    return self.names[appid]
        return "Steam #%s" % appid

    @staticmethod
    def _get_appid(data: bytes) -> Optional[str]:
        # Some wrappers inherit several game identifiers; SteamAppId has priority.
        environment = {}
        for part in data.split(b"\0"):
            if b"=" in part:
                key, value = part.split(b"=", 1)
                if key in APP_IDS:
                    environment[key] = value
        for name in APP_IDS:
            raw = environment.get(name, b"")
            if raw.isdigit():
                val = raw.decode("ascii")
                if 0 < int(val) < 10**11:
                    return val
        return None

    @staticmethod
    def _helper(cmd: str) -> bool:
        # Only the executable's name, not command arguments (which can contain
        # a legitimate game's path), is used for filtering.
        executable = cmd.split("\0", 1)[0].rsplit("/", 1)[-1].lower()
        return not executable or any(executable == x or executable.startswith(x + "-") for x in HELPERS)

    def running(self) -> Dict[str, dict]:
        games: Dict[str, dict] = {}
        seen = 0
        try:
            pids = self.proc_path.iterdir()
            for path in pids:
                if not PID_RE.match(path.name):
                    continue
                try:
                    # Skip zombies (a dead process must never count).
                    stat = (path / "stat").read_text(errors="replace")
                    state = stat.rsplit(")", 1)[-1].strip().split()[0]
                    if state in ("Z", "X", "x", "T", "t"):
                        continue
                    command = (path / "cmdline").read_bytes()[:4096].decode("utf-8", "replace")
                    if self._helper(command):
                        continue
                    environ = (path / "environ").read_bytes()[:32768]
                    appid = self._get_appid(environ)
                    if not appid:
                        continue
                    seen += 1
                    entry = games.setdefault(appid, {"appid": appid, "name": self._name(appid), "processes": 0})
                    entry["processes"] += 1
                except (OSError, ValueError, IndexError):
                    continue
            self.problem = None
        except OSError as exc:
            self.problem = str(exc)
        return games
