# core/queue_manager.py
import threading
from queue import PriorityQueue
from core.download_engine import download_file

class DownloadQueue:
    def __init__(self, max_workers=3):
        self.queue = PriorityQueue()
        self.max_workers = max_workers

    def add(self, download_info, priority=5):
        self.queue.put((priority, download_info))

    def start(self):
        threads = [threading.Thread(target=self._worker, daemon=True)
                   for _ in range(self.max_workers)]
        for t in threads:
            t.start()

    def _worker(self):
        while True:
            _, info = self.queue.get()
            try:
                download_file(info)
            finally:
                self.queue.task_done()
