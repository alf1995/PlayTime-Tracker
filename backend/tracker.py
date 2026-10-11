"""Backend-owned game-time ledger; does not depend on Decky UI visibility."""
import asyncio
import time
from datetime import datetime
from .detection import GameDetector
from .power import PowerMonitor, battery_watts


class PlayTimeTracker:
    def __init__(self, store, emitter=None, detector=None, clock=None, wall_clock=None, logger=None):
        self.store = store
        self.emitter = emitter
        self.detector = detector or GameDetector()
        self.clock = clock or time.monotonic
        self.wall_clock = wall_clock or time.time
        self.logger = logger
        self.lock = asyncio.Lock()
        self.loop_task = None
        self.power = PowerMonitor(self.on_sleep_signal, logger)
        self.suspended = False
        self.paused = False
        self.appid = None
        self.game_name = None
        self.sid = None
        self.interval_id = None
        self.interval_duration = 0
        self.interval_end = None
        self.last_mono = None
        self.last_wall = None
        self.detected = {}
        self.status = "idle"
        self.last_energy = 0

    def _wall_ms(self):
        return int(self.wall_clock() * 1000)

    async def start(self):
        await self.power.start()
        self.loop_task = asyncio.create_task(self._poll_loop())

    async def stop(self):
        if self.loop_task:
            self.loop_task.cancel()
            await asyncio.gather(self.loop_task,return_exceptions=True)
            self.loop_task = None
        await self.power.stop()
        async with self.lock:
            self._finish(self._wall_ms(),"backend_unload")

    async def _poll_loop(self):
        while True:
            try:
                await self.tick()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                if self.logger:
                    self.logger.exception("Tracker polling error: %s",exc)
            await asyncio.sleep(5)

    def _new_interval(self, wall_ms):
        self.interval_id = self.store.new_interval(self.sid, wall_ms)
        self.interval_duration = 0
        self.interval_end = wall_ms

    def _close_interval(self):
        self.interval_id = None
        self.interval_duration = 0
        self.interval_end = None

    def _finish(self, when, reason):
        self._close_interval()
        if self.sid is not None:
            # End at last accounted time (rather than attributing unobserved gaps).
            self.store.end_session(self.sid,when,reason)
        self.sid = None
        self.appid = None
        self.game_name = None
        self.last_mono = None
        self.last_wall = None

    async def on_sleep_signal(self, going_to_sleep):
        async with self.lock:
            self.suspended = bool(going_to_sleep)
            if self.suspended:
                self._close_interval()
                self.last_mono = None
                self.last_wall = None
                self.status = "suspended"
            else:
                # Must validate the current game again before continuing.
                self._close_interval()
                self.last_mono = None
                self.last_wall = None
                self.status = "unknown"

    async def set_paused(self, paused):
        if type(paused) is not bool:
            raise ValueError("Expected boolean")
        async with self.lock:
            self.paused = paused
            self._close_interval()
            self.last_mono = None
            self.last_wall = None
            self.status = "paused" if paused else "unknown"
        return self.snapshot()

    def snapshot(self):
        return {"status":self.status,"appid":self.appid,"name":self.game_name,
                "paused":self.paused,"suspended":self.suspended,
                "detected":list(self.detected.values()),
                "detection_method":"linux_proc_steam_environment",
                "foreground_verified":False,"power_signals_available":self.power.available,
                "detector_error":self.detector.problem}

    async def tick(self, found=None):
        now_mono = self.clock()
        now_wall = self._wall_ms()
        if found is None:
            found = await asyncio.to_thread(self.detector.running)
        async with self.lock:
            self.detected = found
            settings = self.store.get_settings()
            if self.suspended:
                self.status = "suspended"; return
            if not settings["tracking_enabled"]:
                self._finish(now_wall,"disabled")
                self.status = "disabled"; return
            if not found:
                self._finish(now_wall,"game_not_detected")
                self.status = "idle"; return
            if len(found) != 1:
                self._finish(now_wall,"multiple_games")
                self.status = "ambiguous"; return
            appid, info = next(iter(found.items()))
            if self.appid != appid:
                self._finish(now_wall,"game_changed")
                self.appid = appid
                self.game_name = info["name"]
                self.sid = self.store.start_session(appid,self.game_name,now_wall)
                self.last_mono = None
                self.last_wall = None
            if self.paused:
                self._close_interval()
                self.last_mono = None; self.last_wall = None
                self.status = "paused"
                return
            self.status = "running"
            if self.last_mono is None:
                self._new_interval(now_wall)
                self.last_mono = now_mono
                self.last_wall = now_wall
                return
            delta_mono_ms = int(max(0,(now_mono-self.last_mono)*1000))
            delta_wall_ms = max(0, now_wall - self.last_wall)
            # Linux CLOCK_MONOTONIC excludes sleep; do not count unobserved
            # long stalls even if the process stays alive during a hang.
            duration = min(delta_mono_ms, 12000)
            slept_or_skipped = delta_wall_ms - delta_mono_ms > 2500 or delta_mono_ms > 12000
            if duration > 0:
                if self.interval_id is None:
                    self._new_interval(self.last_wall)
                self.interval_duration += duration
                self.interval_end += duration
                self.store.update_interval(self.interval_id,self.interval_end,self.interval_duration)
            if slept_or_skipped:
                # End the previous interval before the wall-clock jump; after
                # revalidation, start the next one at the current wall time.
                self._close_interval()
            self.last_mono = now_mono
            self.last_wall = now_wall
            if now_mono-self.last_energy > 30:
                watts = battery_watts()
                if watts is not None:
                    self.store.add_energy_sample(self.sid,now_wall,watts)
                self.last_energy = now_mono
            await self._notify(settings,now_wall)

    async def _notify(self, settings, now_ms):
        if not settings["notifications"] or not self.emitter or self.sid is None:
            return
        daily_limit = settings["daily_limit_minutes"]
        if daily_limit > 0 and self.store.summary()["today_ms"] >= daily_limit*60000:
            key = "daily:%s:%d" % (datetime.fromtimestamp(now_ms/1000).date().isoformat(),daily_limit)
            if self.store.mark_notification(key,now_ms):
                await self.emitter("playtime_notice",{"type":"limit", "minutes":daily_limit})
        minutes = settings["break_interval_minutes"]
        if minutes > 0:
            row = self.store.db.execute("SELECT COALESCE(SUM(duration_ms),0) FROM active_intervals WHERE session_id=?",(self.sid,)).fetchone()
            block = row[0] // (minutes*60000)
            if block:
                key = "break:%d:%d:%d" % (self.sid,minutes,block)
                if self.store.mark_notification(key,now_ms):
                    await self.emitter("playtime_notice",{"type":"break","minutes":int(block*minutes)})
