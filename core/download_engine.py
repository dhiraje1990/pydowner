# core/download_engine.py
import requests
from pathlib import Path

def download_file(info, dest_dir="downloads", on_progress=None):
    dest = Path(dest_dir) / info.filename
    headers = {}
    start_byte = dest.stat().st_size if dest.exists() and info.supports_resume else 0
    if start_byte:
        headers["Range"] = f"bytes={start_byte}-"

    with requests.get(info.url, headers=headers, stream=True, timeout=30) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0)) + start_byte
        mode = "ab" if start_byte else "wb"
        downloaded = start_byte
        with open(dest, mode) as f:
            for chunk in r.iter_content(chunk_size=1024 * 64):
                f.write(chunk)
                downloaded += len(chunk)
                if on_progress:
                    on_progress(downloaded, total)
