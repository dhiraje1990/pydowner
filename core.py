import os
import json
import time
import threading
import requests
import importlib
import pkgutil
import re

class DownloadManager:
    def __init__(self):
        self.settings_path = "settings.json"
        self.downloads_path = "downloads.json"
        self.settings = {
            "default_folder": os.path.join(
                os.path.expanduser("~"),
                "Downloads", 
                "PyDowner"
            )
        }
        self.load_settings()
        
        self.downloads = {} 
        self.stop_events = {}    
        self.plugins = self.load_plugins()
        self.load_downloads()

    def load_settings(self):
        if os.path.exists(self.settings_path):
            with open(self.settings_path, "r") as f: self.settings.update(json.load(f))
        else: self.save_settings()

    def save_settings(self):
        with open(self.settings_path, "w") as f: json.dump(self.settings, f, indent=4)

    def load_downloads(self):
        if os.path.exists(self.downloads_path):
            with open(self.downloads_path, "r") as f:
                self.downloads = json.load(f)
                for d in self.downloads.values():
                    if d["status"] == "Downloading": d["status"] = "Paused"

    def save_downloads(self):
        with open(self.downloads_path, "w") as f: json.dump(self.downloads, f, indent=4)

    def load_plugins(self):
        import plugins as p_pkg
        found = []
        for _, name, _ in pkgutil.iter_modules(p_pkg.__path__):
            if name == "base_plugin": continue
            mod = importlib.import_module(f"plugins.{name}")
            for attr in dir(mod):
                obj = getattr(mod, attr)
                if isinstance(obj, type) and hasattr(obj, "can_handle") and obj.__name__ != "BasePlugin":
                    found.append(obj())
        return found

    def add_download(self, url):
        dl_id = str(int(time.time() * 1000))
        self.downloads[dl_id] = {
            "url": url, "filename": "Resolving...", "size": 0,
            "downloaded": 0, "status": "Queued", "speed": "0 KB/s"
        }
        self.start_download(dl_id)
        return dl_id

    def start_download(self, dl_id, restart=False):
        """ Handles both Resume (default) and Restart """
        info = self.downloads[dl_id]
        
        if restart:
            # Wipe local file if it exists to start fresh
            path = os.path.join(self.settings["default_folder"], info["filename"])
            if os.path.exists(path): 
                try: os.remove(path)
                except: pass
            info["downloaded"] = 0
            info["status"] = "Queued"

        stop_event = threading.Event()
        self.stop_events[dl_id] = stop_event
        threading.Thread(target=self._worker, args=(dl_id, stop_event), daemon=True).start()

    def pause_download(self, dl_id):
        if dl_id in self.stop_events: self.stop_events[dl_id].set()
        self.downloads[dl_id]["status"] = "Paused"
        self.save_downloads()

    def delete_download(self, dl_id, delete_file=False):
        self.pause_download(dl_id)
        if delete_file:
            path = os.path.join(self.settings["default_folder"], self.downloads[dl_id].get("filename", ""))
            if os.path.exists(path):
                try: os.remove(path)
                except: pass
        del self.downloads[dl_id]
        self.save_downloads()

    def _worker(self, dl_id, stop_event):
        info = self.downloads[dl_id]
        try:
            # Resolve URL via plugins
            direct_link = info["url"]
            for p in self.plugins:
                if p.can_handle(info["url"]):
                    direct_link = p.get_direct_link(info["url"])
            
            path = os.path.join(self.settings["default_folder"], info["filename"])
            headers = {}
            
            # Resume Logic: Check if file exists and set Range header
            if os.path.exists(path) and info["downloaded"] > 0:
                curr_size = os.path.getsize(path)
                headers['Range'] = f'bytes={curr_size}-'
                mode = 'ab'
            else:
                mode = 'wb'

            resp = requests.get(direct_link, headers=headers, stream=True, timeout=15)
            
            if info["filename"] == "Resolving...":
                # Try to get real filename
                d = resp.headers.get("Content-Disposition")
                info["filename"] = re.findall('filename="?([^"]+)"?', d)[0] if d else direct_link.split("/")[-1]
                info["size"] = int(resp.headers.get('content-length', 0)) + info["downloaded"]
                path = os.path.join(self.settings["default_folder"], info["filename"])

            info["status"] = "Downloading"
            with open(path, mode) as f:
                start = time.time()
                chunk_sum = 0
                for chunk in resp.iter_content(chunk_size=8192):
                    if stop_event.is_set(): return
                    f.write(chunk)
                    info["downloaded"] += len(chunk)
                    chunk_sum += len(chunk)
                    
                    if time.time() - start > 1:
                        info["speed"] = f"{(chunk_sum/1024):.1f} KB/s"
                        start, chunk_sum = time.time(), 0
            
            info["status"] = "Completed"
        except Exception as e:
            info["status"] = "Error"
            print(f"Error: {e}")
        self.save_downloads()