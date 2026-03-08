#!/usr/bin/env python3
from core.plugin_manager import PluginManager
from core.download_engine import download_file

if __name__ == "__main__":
    pm = PluginManager()
    pm.load_all()
    
    test_url = "http://www.mediafire.com/file/tjmjrmtuyco/Mahlerfeest09.part1.rar"
    
    plugin = pm.find_plugin(test_url)
    if plugin:
        print(f"✅ Found plugin: {plugin.name}")
        info = plugin.resolve(test_url)
        download_file(info)
    else:
        print("❌ No plugin handles this URL")
        print("Available plugins:", [p.name for p in pm.plugins])
