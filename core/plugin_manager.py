import importlib.util
import os
from core.plugin_base import BaseHostPlugin

class PluginManager:
    def __init__(self, plugin_dir="plugins"):
        self.plugin_dir = plugin_dir
        self.plugins = []
    
    def load_all(self):
        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir)
            return
        
        for fname in os.listdir(self.plugin_dir):
            if fname.endswith('.py') and not fname.startswith('_'):
                path = os.path.join(self.plugin_dir, fname)
                spec = importlib.util.spec_from_file_location(fname[:-3], path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                for attr in vars(module).values():
                    if isinstance(attr, type) and issubclass(attr, BaseHostPlugin) and attr != BaseHostPlugin:
                        self.plugins.append(attr())
    
    def find_plugin(self, url: str) -> BaseHostPlugin | None:
        for plugin in self.plugins:
            if plugin.can_handle(url):
                return plugin
        return None
