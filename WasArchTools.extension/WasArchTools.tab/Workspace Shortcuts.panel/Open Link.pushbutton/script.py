"""Open the configured URL in the default web browser.

This implementation relies only on the Python standard library to avoid
environment-specific imports. On Windows, it prefers ``os.startfile`` for
reliability; otherwise it falls back to ``webbrowser``.
"""

import os
import sys
import webbrowser


TARGET_URL = "https://github.com/vasiliy-924/WasArchTools_forRevit"  # Replace with your desired link


def open_url_in_default_browser(url):
    """Open the given URL using the system default handler.

    On Windows, attempt to use os.startfile first; otherwise use webbrowser.
    """
    if sys.platform.startswith("win"):
        try:
            os.startfile(url)  # type: ignore[attr-defined]
            return
        except (AttributeError, OSError):
            pass

    webbrowser.open(url, new=2)


if __name__ == "__main__":
    open_url_in_default_browser(TARGET_URL)


