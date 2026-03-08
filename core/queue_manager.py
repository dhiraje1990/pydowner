import json
import os
from pathlib import Path
from queue import PriorityQueue
from dataclasses import dataclass
from core.plugin_base import DownloadInfo
from core.plugin_manager import PluginManager
from core.download_engine import download_file
from config.settings import Settings

settings = Settings()

@dataclass
class QueueItem:
    info: DownloadInfo
    url: str
    priority: int = 5
    status: str = "pending"  # pending, downloading, completed, failed

class QueueManager:
    def __init__(self, queue_file="queue.json"):
        self.queue_file = queue_file
        self.queue = PriorityQueue()
        self.items = {}
        self.load()
    
    def add(self, url: str, priority: int = 5):
        pm = PluginManager()
        pm.load_all()
        plugin = pm.find_plugin(url)
        
        if not plugin:
            return f"No plugin for {url}"
        
        try:
            info = plugin.resolve(url)
            item = QueueItem(info, url, priority)
            self.items[url] = item
            self.queue.put((priority, url))
            self.save()
            return f"✅ Added: {info.filename}"
        except Exception as e:
            return f"❌ Failed to add {url}: {e}"
    
    def start(self, max_workers=None):
        workers = max_workers or settings.max_workers
        print(f"🚀 Starting {workers} workers...")
        while not self.queue.empty():
            priority, url = self.queue.get()  # Fixed: unpack priority, url
            item = self.items[url]
            try:
                item.status = "downloading"
                download_file(item.info, settings.download_dir)
                item.status = "completed"
            except Exception as e:
                item.status = "failed"
                print(f"❌ {url}: {e}")
            self.save()
            self.root.after(0, self.refresh_status)  # GUI update


    
    def status(self):
        if not self.items:
            return "Queue empty"
        return "\n".join([f"{item.status}: {item.info.filename}" for item in self.items.values()])
    
    def save(self):
        data = {url: {
            'url': item.url, 'filename': item.info.filename,
            'status': item.status, 'priority': item.priority
        } for url, item in self.items.items()}
        with open(self.queue_file, 'w') as f:
            json.dump(data, f)
    
    def load(self):
        if os.path.exists(self.queue_file):
            with open(self.queue_file, 'r') as f:
                data = json.load(f)
                for url, info in data.items():
                    # Recreate minimal item for display
                    self.items[url] = QueueItem(
                        DownloadInfo(info['filename'], '', -1, ''),
                        url, info['priority'], info['status']
                    )
