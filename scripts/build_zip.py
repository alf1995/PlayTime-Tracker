"""Build a Decky Loader release ZIP from an existing compiled frontend.

The ZIP MUST contain exactly one top-level plugin directory. A source ZIP
with loose files at archive root is not a valid installation archive.
"""
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = "PlayTime-Tracker"
manifest = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
version = package["version"]
if package.get("type") != "module":
    sys.exit('ERROR: package.json needs "type": "module" for a modern Decky plugin.')
if not manifest.get("name"):
    sys.exit('ERROR: plugin.json has no name.')

required = ("dist/index.js", "main.py", "plugin.json", "package.json", "LICENSE")
for rel in required:
    if not (ROOT / rel).is_file():
        sys.exit("ERROR: missing %s. Build the frontend with npm run build." % rel)
if (ROOT / "dist/index.js").stat().st_size < 1000:
    sys.exit("ERROR: dist/index.js is unexpectedly small. Rebuild the frontend.")

out = ROOT / ("PlayTime-Tracker-v%s-INSTALL.zip" % version)
extras = ("README.md",)
paths = [ROOT / f for f in required + extras if (ROOT / f).is_file()]
paths += [p for p in (ROOT / "backend").rglob("*.py") if p.is_file()]
if (ROOT / "dist/index.js.map").is_file():
    paths.append(ROOT / "dist/index.js.map")

with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted(paths):
        z.write(p, FOLDER + "/" + p.relative_to(ROOT).as_posix())

with zipfile.ZipFile(out) as z:
    names = z.namelist()
    assert names and all(name.startswith(FOLDER + "/") for name in names)
    for f in required:
        assert FOLDER + "/" + f in names
    assert not z.testzip(), "Damaged ZIP"
    assert json.loads(z.read(FOLDER + "/plugin.json"))['name'] == manifest['name']
    assert json.loads(z.read(FOLDER + "/package.json"))['version'] == version
print("VALID INSTALL ZIP:", out)
print("Files:", len(paths))
