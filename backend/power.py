"""Power monitoring: Linux monotonic clock plus optional login1 D-Bus signals."""
import asyncio
import shutil


class PowerMonitor:
    def __init__(self, callback, logger=None):
        self.callback = callback
        self.logger = logger
        self.task = None
        self.process = None
        self.available = False

    async def start(self):
        if not shutil.which("dbus-monitor"):
            return
        self.task = asyncio.create_task(self._run())

    async def _run(self):
        try:
            self.process = await asyncio.create_subprocess_exec(
                "dbus-monitor", "--system",
                "type='signal',interface='org.freedesktop.login1.Manager',member='PrepareForSleep'",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
            )
            self.available = True
            while self.process.returncode is None:
                line = await self.process.stdout.readline()
                if not line:
                    break
                text = line.strip()
                if text == b"boolean true":
                    await self.callback(True)
                elif text == b"boolean false":
                    await self.callback(False)
        except asyncio.CancelledError:
            raise
        except (OSError, RuntimeError) as exc:
            if self.logger:
                self.logger.warning("Power monitor unavailable: %s", exc)
        finally:
            self.available = False
            if self.process and self.process.returncode is None:
                self.process.terminate()
                try:
                    await asyncio.wait_for(self.process.wait(), timeout=2)
                except asyncio.TimeoutError:
                    self.process.kill()
                    await self.process.wait()

    async def stop(self):
        if self.task:
            self.task.cancel()
            await asyncio.gather(self.task, return_exceptions=True)
            self.task = None


def battery_watts():
    """Positive discharge W from sysfs. This is device battery drain, NOT game TDP.
    Returns None for mains/charging, missing sensors and invalid readings.
    """
    from pathlib import Path
    for bat in Path("/sys/class/power_supply").glob("BAT*"):
        try:
            status = (bat / "status").read_text().strip().lower()
            if status != "discharging":
                continue
            power = bat / "power_now"
            if power.exists():
                watts = int(power.read_text().strip()) / 1_000_000
            else:
                amps = int((bat / "current_now").read_text().strip())
                volts = int((bat / "voltage_now").read_text().strip())
                watts = amps * volts / 1_000_000_000_000
            if 0 < watts <= 200:
                return round(watts, 2)
        except (OSError, ValueError):
            continue
    return None
