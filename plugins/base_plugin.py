class BasePlugin:
    def can_handle(self, url):
        """Returns True if the plugin supports this URL."""
        raise NotImplementedError

    def get_direct_link(self, url):
        """Scrapes or requests the direct download link."""
        raise NotImplementedError