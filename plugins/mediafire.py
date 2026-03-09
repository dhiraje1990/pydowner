import re
import requests
from .base_plugin import BasePlugin

class MediafirePlugin(BasePlugin):
    def can_handle(self, url):
        return "mediafire.com" in url

    def get_direct_link(self, url):
        try:
            # Mediafire requires a standard User-Agent sometimes
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Mediafire usually houses the actual download link in an element with id "downloadButton"
            # Regex extracts the href link
            match = re.search(r'href="(https?://[a-zA-Z0-9.-]*mediafire\.com/file/[^"]+|https?://download[^"]+)"\s+id="downloadButton"', response.text)
            
            if match:
                return match.group(1)
            
            # Fallback regex if class changes
            match_fallback = re.search(r'class="[^"]*download[^"]*".*?href="(https?://[^"]+)"', response.text, re.IGNORECASE)
            if match_fallback:
                return match_fallback.group(1)
                
            return None
        except Exception as e:
            print(f"Mediafire Plugin Error: {e}")
            return None