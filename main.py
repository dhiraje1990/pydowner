# pydowner/main.py (starter)
from core.plugin_manager import PluginManager
from core.download_engine import download_file

if __name__ == "__main__":
    pm = PluginManager()
    pm.load_all()
    plugin = pm.find_plugin("https://pixeldrain.com/u/abc123")
    if plugin:
        info = plugin.resolve("https://pixeldrain.com/u/abc123")
        download_file(info)
    else:
        print("No plugin found")
