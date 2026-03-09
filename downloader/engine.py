import os
import threading
import time
import requests
from typing import Dict, List

class DownloadTask:
    def __init__(self, tid, url, filename, total, downloaded, status):
        self.id = tid
        self.url = url
        self.filename = filename
        self.total_size = total
        self.downloaded = downloaded
        self.status = status
        self.speed = "0 KB/s"

class DownloadEngine:
    def __init__(self, db, settings, plugins):
        self.db = db
        self.settings = settings
        self.plugins = plugins
        self.tasks: Dict[str, DownloadTask] = {}
        self.stop_signals: Dict[str, threading.Event] = {}
        self._load_existing()

    def _load_existing(self):
        """Loads tasks from SQLite on startup."""
        for row in self.db.get_tasks():
            # If app closed while downloading, mark as Paused
            status = "Paused" if row['status'] == "Downloading" else row['status']
            self.tasks[row['id']] = DownloadTask(
                row['id'], row['url'], row['filename'], 
                row['total_size'], row['downloaded'], status
            )

    def add_download(self, url: str):
        """Adds a new task to memory, DB, and starts it."""
        tid = str(int(time.time() * 1000))
        # Initial placeholder task
        self.tasks[tid] = DownloadTask(tid, url, "Resolving...", 0, 0, "Queued")
        self.db.save_task(tid, url, "Resolving...", 0, 0, "Queued")
        self.run_task(tid)

    def run_task(self, tid: str, restart: bool = False):
        """Starts or Resumes a download task."""
        if tid in self.stop_signals:
            self.stop_signals[tid].set() # Stop existing thread if running

        task = self.tasks[tid]
        
        if restart:
            task.downloaded = 0
            task.status = "Queued"
            path = os.path.join(self.settings.get("default_folder"), task.filename)
            if os.path.exists(path):
                try: os.remove(path)
                except: pass

        stop_event = threading.Event()
        self.stop_signals[tid] = stop_event
        
        # Start the worker thread
        thread = threading.Thread(target=self._worker, args=(tid, stop_event), daemon=True)
        thread.start()

    def pause_task(self, tid: str):
        """Signals the thread to stop and updates status."""
        if tid in self.stop_signals:
            self.stop_signals[tid].set()
        
        task = self.tasks.get(tid)
        if task:
            task.status = "Paused"
            task.speed = "0 KB/s"
            self.db.save_task(task.id, task.url, task.filename, task.total_size, task.downloaded, "Paused")

    def delete_task(self, tid: str, delete_file: bool = False):
        """Removes task from memory/DB and optionally wipes disk file."""
        self.pause_task(tid)
        
        task = self.tasks.get(tid)
        if delete_file and task and task.filename != "Resolving...":
            path = os.path.join(self.settings.get("default_folder"), task.filename)
            if os.path.exists(path):
                try: os.remove(path)
                except: pass
                
        self.db.remove_task(tid)
        if tid in self.tasks:
            del self.tasks[tid]

    def _worker(self, tid: str, stop_event: threading.Event):
        """Threaded worker that handles the actual data streaming."""
        task = self.tasks[tid]
        try:
            # 1. Resolve Link via Plugins
            final_url = task.url
            for plugin in self.plugins:
                if plugin.can_handle(task.url):
                    final_url = plugin.get_direct_link(task.url)

            save_dir = self.settings.get("default_folder")
            save_path = os.path.join(save_dir, task.filename)
            headers = {}
            
            # 2. Check for Resume (HTTP Range)
            if os.path.exists(save_path) and task.downloaded > 0:
                actual_on_disk = os.path.getsize(save_path)
                headers['Range'] = f"bytes={actual_on_disk}-"
                task.downloaded = actual_on_disk
                mode = 'ab'
            else:
                mode = 'wb'

            # 3. Stream Download
            with requests.get(final_url, headers=headers, stream=True, timeout=20) as r:
                r.raise_for_status()
                
                # Resolve filename if it's the first time
                if task.filename == "Resolving...":
                    # Try to get filename from URL
                    task.filename = final_url.split("/")[-1].split("?")[0] or f"download_{tid}.bin"
                    task.total_size = int(r.headers.get('content-length', 0))
                    save_path = os.path.join(save_dir, task.filename)

                task.status = "Downloading"
                
                with open(save_path, mode) as f:
                    start_time = time.time()
                    bytes_this_second = 0
                    
                    for chunk in r.iter_content(chunk_size=16384):
                        if stop_event.is_set():
                            return # Exit thread quietly
                        
                        f.write(chunk)
                        task.downloaded += len(chunk)
                        bytes_this_second += len(chunk)
                        
                        # Calculate speed every second
                        if time.time() - start_time > 1.0:
                            task.speed = f"{bytes_this_second // 1024} KB/s"
                            bytes_this_second = 0
                            start_time = time.time()
                            # Save progress to DB occasionally
                            self.db.save_task(task.id, task.url, task.filename, task.total_size, task.downloaded, task.status)

            task.status = "Completed"
            task.speed = "0 KB/s"
            
        except Exception as e:
            task.status = "Error"
            task.speed = "Failed"
            print(f"Engine Error on {tid}: {e}")
            
        finally:
            self.db.save_task(task.id, task.url, task.filename, task.total_size, task.downloaded, task.status)