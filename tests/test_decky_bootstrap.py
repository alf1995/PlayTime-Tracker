"""Regression test: Decky can import main.py by module spec without plugin root in sys.path."""
import subprocess
import sys
import unittest
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]

class DeckyImportTest(unittest.TestCase):
    def test_loader_import_and_dashboard(self):
        code = r'''
import asyncio
import importlib.util
import sys
import tempfile
import types
from pathlib import Path
stub = types.ModuleType('decky')
stub.DECKY_PLUGIN_RUNTIME_DIR = tempfile.mkdtemp(prefix='playtime-boot-')
stub.DECKY_USER_HOME = str(Path.home())
class Log:
    def info(self, *args): pass
    def warning(self, *args): pass
    def exception(self, *args): pass
stub.logger = Log()
async def emit(*args): pass
stub.emit = emit
sys.modules['decky'] = stub
spec = importlib.util.spec_from_file_location('playtime_decky', sys.argv[1])
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
async def check():
    plugin = module.Plugin()
    await plugin._main()
    try:
        assert (await plugin.backend_health())['initialized'] is True
        dashboard = await plugin.get_dashboard()
        assert dashboard['summary']['total_ms'] == 0
    finally:
        await plugin._unload()
asyncio.run(check())
'''
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run(
                [sys.executable, '-I', '-c', code, str(ROOT / 'main.py')],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=15
            )
        self.assertEqual(result.returncode, 0, result.stderr)

if __name__ == '__main__':
    unittest.main()
