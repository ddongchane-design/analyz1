import json
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

pending_dir = Path("data/pending")
for p_file in pending_dir.glob("*.json"):
    try:
        data = json.loads(p_file.read_text(encoding="utf-8"))
        video = data.get("video", {})
        print(f"File: {p_file.name} | Channel: {video.get('channel_name')} | Title: {video.get('title')}")
    except Exception as e:
        print(f"Error reading {p_file.name}: {e}")
