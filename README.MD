# 📂 PyDowner

**PyDowner** is a robust, modular, and asynchronous download manager built in Python. Inspired by tools like MiPony and FreeRapid, it is specifically designed to handle file-hosting platforms through a flexible plugin architecture.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Database](https://img.shields.io/badge/database-SQLite-003B57.svg)](https://sqlite.org/)

---

## ✨ Key Features

*   **Plugin-Based Architecture**: Modular design allows contributors to add support for new file-hosting sites (like Mediafire, Mega, Google Drive) by simply dropping a script into the `plugins/` folder.
*   **State Persistence**: Uses an **SQLite** backend to ensure download progress is saved. If the application crashes or is closed, you can resume exactly where you left off.
*   **Resume & Restart Logic**: Intelligent handling of HTTP Range headers allows for resuming partial downloads. A "Fresh Restart" option is also available to wipe partial data and start over.
*   **Concurrent Threading**: Downloads run in background threads, ensuring the **Tkinter GUI** remains responsive and fluid at all times.
*   **Context-Aware Management**: Right-click any entry in the queue to Pause, Resume, Restart, or Delete (from list or disk).
*   **Dynamic Settings**: Manage global preferences, including default download locations, via a local `settings.json` configuration.

---

## 🛠️ Installation

### Prerequisites
*   Python 3.8 or higher.
*   `pip` (Python package manager).

### Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/pydowner.git
   cd pydowner
   ```

2. **Install dependencies:**
   ```bash
   pip install requests
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

---

## 🚀 Usage

1.  **Adding a Download**: Paste a supported URL (e.g., a Mediafire link) into the top input bar and click **Add Download**.
2.  **Managing Tasks**: Right-click on any item in the table to access the management menu.
3.  **Changing Folder**: Use the **Change Folder** button in the settings bar to choose where your files are saved.
4.  **Resuming**: If you close PyDowner, simply reopen it and right-click your "Paused" or "Error" tasks to click **Resume**.

---

## 🔌 Plugin Development (For Contributors)

Adding support for a new website is easy. PyDowner automatically loads any class that inherits from `BasePlugin` found within the `plugins/` directory.

### Example Plugin Structure:
Create `plugins/mysite_com.py`:

```python
from .base_plugin import BasePlugin
import requests
import re

class MySitePlugin(BasePlugin):
    def can_handle(self, url: str) -> bool:
        """Return True if this plugin can handle the URL."""
        return "mysite.com" in url

    def get_direct_link(self, url: str) -> str:
        """Logic to scrape/extract the direct file link."""
        # Add scraping logic here
        return extracted_url
```

---

## 📂 Project Structure

```text
pydowner/
├── main.py              # Tkinter GUI Entry Point
├── downloads.db         # SQLite Database (Auto-generated)
├── settings.json        # Configuration file (Auto-generated)
├── downloader/
│   ├── database.py      # SQLite CRUD operations
│   ├── engine.py        # Threading & Streaming logic
│   └── settings.py      # JSON settings manager
└── plugins/
    ├── base_plugin.py   # Abstract base class for plugins
    └── mediafire.py     # Mediafire support plugin
```

---

## 📝 Configuration

PyDowner stores settings in `settings.json`. You can manually edit this file or use the GUI.
*   `default_folder`: The absolute path where files are stored.
*   `max_parallel_downloads`: (Upcoming) limit for concurrent streams.

---

## ⚖️ License

Distributed under the GPL License. See `LICENSE` for more information.

---
