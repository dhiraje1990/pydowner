#!/usr/bin/env python3
import requests
from pathlib import Path
from config.settings import Settings

settings = Settings()

def download_file(info, dest_dir=settings.download_dir, on_progress=None):
    dest = Path(dest_dir) / info.filename
    dest.parent.mkdir(parents=True, exist_ok=True)
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    resp = requests.get(info.url, headers=headers, stream=True, timeout=30)
    resp.raise_for_status()
    
    total_size = int(resp.headers.get('content-length', 0))
    downloaded = 0
    
    with open(dest, 'wb') as f:
        chunk_count = 0
        for chunk in resp.iter_content(chunk_size=16384):  # Bigger chunks
            if not chunk:
                continue
            f.write(chunk)
            downloaded += len(chunk)
            chunk_count += 1
            
            # Force callback every 5 chunks OR 1%
            if on_progress and (chunk_count % 5 == 0 or downloaded > total_size * 0.01):
                pct = min(99.0, (downloaded / total_size * 100) if total_size else 50)
                on_progress(pct, info.filename)
    
    if on_progress:
        on_progress(100.0, info.filename)
    return True
