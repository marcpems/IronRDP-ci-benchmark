"""Fetch the exact public source snapshots listed in data/sources.json."""
import base64
import json
from pathlib import Path
from collect import api

ROOT = Path(__file__).resolve().parent

for entry in json.loads((ROOT / "data" / "sources.json").read_text()):
    result = json.loads(api(f"repos/{entry['repo']}/contents/{entry['path']}?ref={entry['sha']}"))
    (ROOT / "sources" / entry["local"]).write_bytes(base64.b64decode(result["content"]))
