import json
import os

class SettingsManager:
    """Manages application configuration via JSON."""
    
    def __init__(self, path: str = "settings.json"):
        self.path = path
        self.defaults = {
            "default_folder": os.path.join(os.path.expanduser("~"), "Downloads", "PyDowner")
        }
        self.data = self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                return {**self.defaults, **json.load(f)}
        return self.defaults

    def get(self, key: str):
        return self.data.get(key)

    def set(self, key: str, value: any):
        self.data[key] = value
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=4)