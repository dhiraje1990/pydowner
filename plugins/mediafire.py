import requests
import re
from core.plugin_base import BaseHostPlugin, DownloadInfo

class MediaFirePlugin(BaseHostPlugin):
    name = "MediaFire"
    domains = ["mediafire.com"]
    
    def can_handle(self, url: str) -> bool:
        return 'mediafire.com/file/' in url
    
    def resolve(self, url: str) -> DownloadInfo:
        print(f"🔍 Resolving MediaFire: {url}")
        
        # Get page HTML with browser headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        
        # Extract direct download link from <a class="input popsok" href="...">
        dl_match = re.search(r'<a class="input popsok"[^>]*href="(http[^"]+download\d+\.mediafire\.com[^"]*)"', resp.text)
        
        if not dl_match:
            raise ValueError("Download button not found - file may be private/deleted")
        
        dl_url = dl_match.group(1)
        print(f"🔗 Direct link: {dl_url[:80]}...")
        
        # Extract filename from URL path (last part)
        filename = dl_url.split('/')[-1]
        
        # Try to get filesize from page (optional)
        size_match = re.search(r'(\d+(?:\.\d+)?)\s*(MB|GB)', resp.text)
        filesize = -1
        if size_match:
            size = float(size_match.group(1))
            unit = size_match.group(2)
            filesize = int(size * (1024**3 if unit == 'GB' else 1024**2))
        
        return DownloadInfo(
            filename=filename,
            url=dl_url,
            filesize=filesize,
            referrer=url
        )
