import requests
from pathlib import Path
from core.plugin_base import DownloadInfo

def download_file(info: DownloadInfo, dest_dir="downloads"):
    dest = Path(dest_dir) / info.filename
    dest.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Downloading: {info.filename}")
    print(f"Size: {info.filesize / (1024*1024):.1f} MB")
    print(f"To: {dest}")
    
    resp = requests.get(info.url, stream=True, timeout=30)
    resp.raise_for_status()
    
    total = int(resp.headers.get('content-length', 0))
    downloaded = 0
    
    with open(dest, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                pct = (downloaded / total * 100) if total else 0
                print(f"\rProgress: {pct:.1f}% ({downloaded/(1024*1024):.1f}/{total/(1024*1024):.1f} MB)", end='')
    
    print(f"\n✅ Saved: {dest}")
