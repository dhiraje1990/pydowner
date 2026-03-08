# PyDowner

A modular Python download manager with plugin support for file hosting services, similar to JDownloader and Mipony. Add new file hosts by simply dropping `.py` files into the `plugins/` directory.

[
[

## ✨ Features

- **Plugin-based architecture** - Add support for new file hosts without modifying core code
- **Resume support** - Pick up interrupted downloads
- **Concurrent downloads** - Multiple files download simultaneously
- **Priority queue** - Control download order
- **CLI interface** - Rich progress bars and status
- **Account support** - Premium accounts per service
- **Direct API usage** - No browser automation needed

## 📁 Project Structure

```
pydowner/
├── core/                 # Core engine & plugin system
│   ├── plugin_base.py    # Plugin interface
│   ├── plugin_manager.py # Dynamic plugin loading
│   ├── download_engine.py # Download handling
│   └── queue_manager.py  # Download queue
├── plugins/              # One .py file per file host
│   └── mediafire.py
├── ui/
│   └── cli.py           # Command line interface
├── config/
│   └── settings.json    # User preferences
├── requirements.txt
├── main.py
└── README.md
```

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/eadaradhiraj/pydowner.git
cd pydowner
pip install -r requirements.txt
```

### 2. Run

```bash
python main.py add "https://pixeldrain.com/u/abc123"
python main.py start
```

### 3. Add New Host (Example)

Create `plugins/mega.py`:

```python
from core.plugin_base import BaseHostPlugin, DownloadInfo

class MegaPlugin(BaseHostPlugin):
    name = "Mega"
    domains = ["mega.nz"]
    
    def can_handle(self, url: str) -> bool:
        return "mega.nz" in url
    
    def resolve(self, url: str) -> DownloadInfo:
        # Your download logic here
        pass
```

**Done!** Restart the app - new host is automatically loaded.

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- Git

### Development Setup

```bash
# Clone repository
git clone https://github.com/eadaradhiraj/pydowner.git
cd pydowner

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Optional: linting, testing

# Run
python main.py --help
```

## 📦 Core Dependencies

| Package | Purpose |
|---------|---------|
| `requests` | HTTP requests |
| `beautifulsoup4` | HTML parsing |
| `rich` | CLI interface & progress bars |
| `pathlib` | File path handling |

Install with:
```bash
pip install requests beautifulsoup4 rich
```

## 🎮 Usage

```bash
# Add download links
python main.py add "https://pixeldrain.com/u/abc123"
python main.py add "https://gofile.io/d/xyz789"

# Start downloading (3 concurrent)
python main.py start --workers 3

# Pause/resume
python main.py pause
python main.py resume

# View status
python main.py status

# Clear finished
python main.py clear-finished
```

## 🔌 Writing Plugins

### Plugin Template

```python
# plugins/{hostname}.py
import requests
from core.plugin_base import BaseHostPlugin, DownloadInfo

class {Hostname}Plugin(BaseHostPlugin):
    name = "{Hostname}"
    domains = ["example.com", "*.example.com"]
    
    def can_handle(self, url: str) -> bool:
        return "example.com" in url
    
    def resolve(self, url: str) -> DownloadInfo:
        # 1. Make request to URL
        # 2. Parse HTML or call API
        # 3. Extract direct download URL + metadata
        # 4. Return DownloadInfo object
        response = requests.get(url)
        # Your parsing logic here...
        return DownloadInfo(
            filename="file.zip",
            url="https://direct-download-link.com/file.zip",
            filesize=1024*1024*500,  # 500MB
            referrer=url
        )
```

### Plugin Requirements

- ✅ Inherit `BaseHostPlugin`
- ✅ Set `name` and `domains`
- ✅ Implement `can_handle(url)`
- ✅ Implement `resolve(url)`
- ✅ Return `DownloadInfo` object
- ✅ Handle errors gracefully

## 🧪 Development

```bash
# Run tests
pytest tests/

# Lint code
ruff check .
ruff format .

# Type checking
mypy .

# Run with debug
python main.py --debug
```

## 🤝 Contributing

1. Fork the project
2. Create feature branch (`git checkout -b feature/amazing-plugin`)
3. Write your plugin in `plugins/`
4. Commit (`git commit -m "Add amazing plugin"`)
5. Push (`git push origin feature/amazing-plugin`)
6. Open Pull Request

**Plugin Guidelines:**
- One hosting service per file
- Use direct APIs when available
- Handle rate limits and errors
- Document your parsing logic
- Test with real URLs

## 📋 Current Plugins

| Service | Resume | Premium | Status |
|---------|--------|---------|--------|
| PixelDrain | ✅ | ❌ | Production |
| GoFile | ✅ | ❌ | Production |
| MediaFire | ✅ | 🔜 | Beta |

## ⚠️ Limitations

- No JavaScript-heavy sites (needs Playwright/Selenium)
- No video streaming sites
- Rate limiting per host (configurable)

## 🔮 Roadmap

- [ ] PyQt6 GUI
- [ ] Browser integration
- [ ] Torrent support
- [ ] Premium account manager
- [ ] Debrid service integration
- [ ] Mobile app (via Kivy)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by JDownloader, FreeRapid, Mipony
- Built with Python's amazing ecosystem
- Thanks to all plugin contributors!

***