# plugins/pixeldrain.py
import requests
from core.plugin_base import BaseHostPlugin, DownloadInfo
import re

class PixelDrainPlugin(BaseHostPlugin):
    name = "PixelDrain"
    domains = ["pixeldrain.com"]
    supports_resume = True

    def can_handle(self, url: str) -> bool:
        return "pixeldrain.com/u/" in url

    def resolve(self, url: str) -> DownloadInfo:
        file_id = url.rstrip("/").split("/")[-1]
        api_url = f"https://pixeldrain.com/api/file/{file_id}/info"
        meta = requests.get(api_url).json()
        return DownloadInfo(
            filename=meta["name"],
            url=f"https://pixeldrain.com/api/file/{file_id}",
            filesize=meta["size"],
            referrer=url
        )
