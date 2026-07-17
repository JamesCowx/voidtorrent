"""VoidTorrent application entry point."""

from __future__ import annotations

import sys
import logging
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from .config import Settings
from .engine import TorrentManager
from .ui.main_window import MainWindow
from .theme import QSS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("voidtorrent")


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("VoidTorrent")
    app.setStyleSheet(QSS)

    profile_dir = Path.home() / ".voidtorrent"
    settings = Settings(profile_dir)
    manager = TorrentManager(settings)

    window = MainWindow(manager, settings)
    app.aboutToQuit.connect(manager.shutdown)

    # Handle a .torrent file or magnet passed as an argument.
    for arg in sys.argv[1:]:
        if arg.endswith(".torrent"):
            manager.add_torrent_file(arg)
        elif arg.startswith("magnet:"):
            manager.add_magnet(arg)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
