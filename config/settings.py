# config/settings.py
import json
from pathlib import Path

class Settings:
    def __init__(self):
        self.file = Path("config/settings.json")
        self.download_dir = "downloads"
        self.max_workers = 2
        self.auto_start = False
        self.load()
    
    def load(self):
        if self.file.exists():
            with open(self.file) as f:
                data = json.load(f)
                self.download_dir = data.get('download_dir', self.download_dir)
                self.max_workers = data.get('max_workers', self.max_workers)
                self.auto_start = data.get('auto_start', self.auto_start)
    
    def save(self):
        data = {
            'download_dir': self.download_dir,
            'max_workers': self.max_workers,
            'auto_start': self.auto_start
        }
        self.file.parent.mkdir(exist_ok=True)
        with open(self.file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def update_download_dir(self, path: str):
        self.download_dir = path
        self.save()
