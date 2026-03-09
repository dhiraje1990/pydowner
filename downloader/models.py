from dataclasses import dataclass
from typing import Optional

@dataclass
class DownloadTask:
    """Represents a single download item in the queue."""
    id: str
    url: str
    filename: str = "Resolving..."
    total_size: int = 0
    downloaded: int = 0
    status: str = "Queued"
    speed: str = "0 KB/s"