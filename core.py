import os
import json
import time
import threading
import requests
import importlib
import pkgutil

class DownloadManager:
    def __init__(self, settings_path="settings.json", downloads_path="downloads.json"):
        self.settings_path = settings_path
        self.downloads_path = downloads_path
        
        # Default Settings
        self.settings = {
            "default_folder": os.path.join(os.path.expanduser("~"), "Downloads", "OpenDownloader"),
            "max_concurrent": 3
        }
        self.load_settings()
        
        if not os.path.exists(self.settings["default_folder"]):
            os.makedirs(self.settings["default_folder"])

        # Dictionary to hold download states and active threads
        self.downloads = {}  # Format: { id: { 'url':..., 'filename':..., 'size':..., 'downloaded':..., 'status':... } }
        self.active_threads = {} # Format: { id: thread_object }
        self.stop_events = {}    # Format: { id: threading.Event }
        
        self.plugins = self.load_plugins()
        self.load_downloads()

    def load_settings(self):
        if os.path.exists(self.settings_path):
            with open(self.settings_path, "r") as f:
                self.settings.update(json.load(f))
        else:
            self.save_settings()

    def save_settings(self):
        with open(self.settings_path, "w") as f:
            json.dump(self.settings, f, indent=4)

    def load_downloads(self):
        """Loads previous downloads, resetting any 'Downloading' state to 'Paused' on startup."""
        if os.path.exists(self.downloads_path):
            with open(self.downloads_path, "r") as f:
                self.downloads = json.load(f)
                for dl_id, dl_info in self.downloads.items():
                    if dl_info["status"] == "Downloading":
                        dl_info["status"] = "Paused"

    def save_downloads(self):
        with open(self.downloads_path, "w") as f:
            json.dump(self.downloads, f, indent=4)

    def load_plugins(self):
        """Dynamically loads all plugins from the plugins folder."""
        plugins =[]
        import plugins as plugins_package
        for _, module_name, _ in pkgutil.iter_modules(plugins_package.__path__):
            if module_name == "base_plugin": continue
            module = importlib.import_module(f"plugins.{module_name}")
            for attr in dir(module):
                obj = getattr(module, attr)
                if isinstance(obj, type) and obj.__name__ != "BasePlugin" and hasattr(obj, "can_handle"):
                    plugins.append(obj())
        return plugins

    def add_download(self, url):
        dl_id = str(int(time.time() * 1000))
        self.downloads[dl_id] = {
            "url": url,
            "filename": "Resolving...",
            "size": 0,
            "downloaded": 0,
            "status": "Queued",
            "speed": "0 KB/s"
        }
        self.save_downloads()
        self.start_download(dl_id)
        return dl_id

    def _resolve_direct_link(self, url):
        for plugin in self.plugins:
            if plugin.can_handle(url):
                return plugin.get_direct_link(url)
        return url # Fallback to direct download if no plugin matches

    def start_download(self, dl_id):
        if dl_id in self.active_threads and self.active_threads[dl_id].is_alive():
            return # Already running
        
        stop_event = threading.Event()
        self.stop_events[dl_id] = stop_event
        
        thread = threading.Thread(target=self._download_worker, args=(dl_id, stop_event), daemon=True)
        self.active_threads[dl_id] = thread
        thread.start()

    def pause_download(self, dl_id):
        if dl_id in self.stop_events:
            self.stop_events[dl_id].set()
        self.downloads[dl_id]["status"] = "Paused"
        self.save_downloads()

    def delete_download(self, dl_id, delete_file=False):
        self.pause_download(dl_id)
        if delete_file:
            filepath = os.path.join(self.settings["default_folder"], self.downloads[dl_id].get("filename", ""))
            if os.path.exists(filepath) and os.path.isfile(filepath):
                try: os.remove(filepath)
                except: pass
        if dl_id in self.downloads:
            del self.downloads[dl_id]
        self.save_downloads()

    def _download_worker(self, dl_id, stop_event):
        dl_info = self.downloads[dl_id]
        dl_info["status"] = "Resolving..."
        
        try:
            # Plugin resolution
            direct_url = self._resolve_direct_link(dl_info["url"])
            if not direct_url:
                raise Exception("Could not resolve direct link.")

            # File and Range setup for resuming
            file_path = os.path.join(self.settings["default_folder"], dl_info["filename"])
            headers = {}
            mode = 'wb'
            
            if os.path.exists(file_path) and dl_info["filename"] != "Resolving...":
                downloaded_size = os.path.getsize(file_path)
                headers['Range'] = f'bytes={downloaded_size}-'
                dl_info["downloaded"] = downloaded_size
                mode = 'ab'

            # Initiate request
            response = requests.get(direct_url, headers=headers, stream=True, timeout=10)
            response.raise_for_status()

            # Determine filename if not set
            if dl_info["filename"] == "Resolving...":
                if "Content-Disposition" in response.headers:
                    import re
                    fname = re.findall('filename="?([^"]+)"?', response.headers["Content-Disposition"])
                    dl_info["filename"] = fname[0] if fname else direct_url.split("/")[-1].split("?")[0]
                else:
                    dl_info["filename"] = direct_url.split("/")[-1].split("?")[0]
                
                # Update file path with new filename
                file_path = os.path.join(self.settings["default_folder"], dl_info["filename"])
                
                total_size = int(response.headers.get('content-length', 0))
                dl_info["size"] = total_size

            dl_info["status"] = "Downloading"
            
            # Download Loop
            with open(file_path, mode) as f:
                start_time = time.time()
                bytes_since_start = 0
                
                for chunk in response.iter_content(chunk_size=8192):
                    if stop_event.is_set():
                        dl_info["status"] = "Paused"
                        self.save_downloads()
                        return
                    
                    if chunk:
                        f.write(chunk)
                        dl_info["downloaded"] += len(chunk)
                        bytes_since_start += len(chunk)
                        
                        # Speed calculation
                        elapsed = time.time() - start_time
                        if elapsed > 1.0:
                            speed_kb = (bytes_since_start / elapsed) / 1024
                            dl_info["speed"] = f"{speed_kb:.2f} KB/s"
                            start_time = time.time()
                            bytes_since_start = 0
                            
            dl_info["status"] = "Completed"
            dl_info["speed"] = "0 KB/s"
            
        except Exception as e:
            dl_info["status"] = "Error"
            dl_info["speed"] = str(e)
            
        finally:
            self.save_downloads()