import asyncio
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.storage import Storage
from backend.tracker import PlayTimeTracker
from backend.detection import GameDetector

GAME = {"1091500": {"appid":"1091500","name":"Cyberpunk 2077","processes":1}}

class Clock:
    def __init__(self):
        self.mono=100.0
        self.wall=1700000000.0
    def monotonic(self): return self.mono
    def time(self): return self.wall
    def step(self, seconds):
        self.mono += seconds
        self.wall += seconds
    def sleep(self, seconds):
        # Monotonic excludes time in Linux suspend.
        self.wall += seconds

class LedgerTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store=Storage(Path(self.tmp.name)/"test.sqlite")
        self.clock=Clock()
        self.announcements=[]
        async def notify(name,payload): self.announcements.append((name,payload))
        self.tracker=PlayTimeTracker(self.store,emitter=notify,clock=self.clock.monotonic,wall_clock=self.clock.time)

    async def asyncTearDown(self):
        self.store.close()
        self.tmp.cleanup()

    async def step(self, seconds, found=GAME):
        self.clock.step(seconds)
        await self.tracker.tick(found)

    async def test_count_and_shutdown(self):
        await self.tracker.tick(GAME)
        await self.step(5)
        await self.step(5)
        self.assertEqual(self.store.summary()["total_ms"],10000)
        await self.tracker.tick({})
        self.assertEqual(self.tracker.status,"idle")
        self.assertEqual(self.store.summary()["total_ms"],10000)

    async def test_sleep_exclusion_and_resume(self):
        await self.tracker.tick(GAME)
        await self.step(5)
        await self.tracker.on_sleep_signal(True)
        self.clock.sleep(3*3600)
        await self.tracker.on_sleep_signal(False)
        await self.tracker.tick(GAME)
        await self.step(5)
        self.assertEqual(self.store.summary()["total_ms"],10000)

    async def test_poll_gap_capped(self):
        await self.tracker.tick(GAME)
        self.clock.step(120)
        await self.tracker.tick(GAME)
        self.assertEqual(self.store.summary()["total_ms"],12000)

    async def test_manual_pause(self):
        await self.tracker.tick(GAME)
        await self.step(5)
        await self.tracker.set_paused(True)
        await self.step(5)
        self.assertEqual(self.store.summary()["total_ms"],5000)
        await self.tracker.set_paused(False)
        await self.tracker.tick(GAME)
        await self.step(5)
        self.assertEqual(self.store.summary()["total_ms"],10000)

    async def test_ambiguous_game_prevents_count(self):
        await self.tracker.tick(GAME)
        await self.step(5, {**GAME,"2":{"appid":"2","name":"Second","processes":1}})
        self.assertEqual(self.tracker.status,"ambiguous")
        self.assertEqual(self.store.summary()["total_ms"],0)

    async def test_restart_closes_prior_session_no_fabrication(self):
        await self.tracker.tick(GAME)
        await self.step(5)
        self.store.close()
        self.store=Storage(Path(self.tmp.name)/"test.sqlite")
        self.assertEqual(self.store.summary()["total_ms"],5000)
        status=self.store.db.execute("SELECT ended_reason FROM sessions").fetchone()[0]
        self.assertEqual(status,"backend_restart")

    async def test_export_json_csv(self):
        await self.tracker.tick(GAME)
        await self.step(5)
        out=Path(self.tmp.name)/"out"
        js=Path(self.store.export("json",out))
        csv=Path(self.store.export("csv",out))
        self.assertTrue(js.exists() and csv.exists())
        self.assertEqual(json.loads(js.read_text())["version"],1)
        self.assertIn("Cyberpunk 2077",csv.read_text())

    async def test_notices_once(self):
        self.store.set_setting("daily_limit_minutes",0)
        self.store.set_setting("break_interval_minutes",1)
        await self.tracker.tick(GAME)
        for _ in range(13): await self.step(5)
        self.assertEqual(len(self.announcements),1)
        await self.step(5)
        self.assertEqual(len(self.announcements),1)

class DetectionTest(unittest.TestCase):
    def test_env(self):
        self.assertEqual(GameDetector._get_appid(b"X=a\0SteamAppId=570\0"),"570")
        self.assertIsNone(GameDetector._get_appid(b"SteamAppId=0\0"))
        self.assertIsNone(GameDetector._get_appid(b"SteamAppId=--\0"))

class DateBoundaryTest(unittest.TestCase):
    def test_intervals_split_without_duplication(self):
        from datetime import datetime
        with tempfile.TemporaryDirectory() as folder:
            db=Storage(Path(folder)/"history.sqlite")
            # Five minutes before and five minutes after UTC midnight.
            start=int(datetime(2026,10,10,23,55).timestamp()*1000)
            pivot=int(datetime(2026,10,11,0,0).timestamp()*1000)
            end=int(datetime(2026,10,11,0,5).timestamp()*1000)
            sid=db.start_session("570","Dota 2",start)
            item=db.new_interval(sid,start)
            db.update_interval(item,end,600000)
            self.assertEqual(db.total_ms("570",start,pivot),300000)
            self.assertEqual(db.total_ms("570",pivot,end),300000)
            self.assertEqual(db.total_ms("570"),600000)
            db.close()

class StorageTest(unittest.TestCase):
    def test_settings_validation(self):
        with tempfile.TemporaryDirectory() as path:
            db=Storage(Path(path)/"test.db")
            self.assertEqual(db.set_setting("language","es")["language"],"es")
            with self.assertRaises(ValueError): db.set_setting("language","fr")
            with self.assertRaises(ValueError): db.set_setting("notifications",1)
            with self.assertRaises(ValueError): db.set_setting("daily_limit_minutes",100000)
            db.close()

if __name__=="__main__": unittest.main()
