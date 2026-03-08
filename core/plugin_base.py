# core/plugin_base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class DownloadInfo:
    filename: str
    url: str          # resolved direct download URL
    filesize: int     # bytes, -1 if unknown
    referrer: str

class BaseHostPlugin(ABC):
    name: str = ""          # e.g., "MediaFire"
    domains: list = []      # e.g., ["mediafire.com"]
    version: str = "1.0"
    supports_resume: bool = False
    requires_account: bool = False

    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """Return True if this plugin handles the given URL."""

    @abstractmethod
    def resolve(self, url: str) -> DownloadInfo:
        """Parse the page and return the direct download link + metadata."""

    def login(self, username: str, password: str) -> bool:
        """Optional: implement for premium accounts."""
        return False
