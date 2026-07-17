"""Persistent settings for VoidTorrent, stored in JSON under the profile dir."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

VERSION = "1.0.0"


class Settings:
    """Typed wrapper around a JSON settings file."""

    def __init__(self, profile_dir: Path) -> None:
        self.profile_dir = profile_dir
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self._path = profile_dir / "settings.json"
        self.version = VERSION
        self._defaults()

    def _defaults(self) -> None:
        self.default_save_path: str = str(Path.home() / "Downloads" / "VoidTorrent")
        self.listen_port: int = 6881
        self.dht: bool = True
        self.lsd: bool = True
        self.upnp: bool = True
        self.natpmp: bool = True
        self.max_download: int = 0
        self.max_upload: int = 0
        self.max_connections: int = 200
        self.max_active_downloads: int = 8
        self.max_active_uploads: int = 8
        self.start_minimized: bool = False
        self.delete_torrent_file_after_add: bool = False
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def as_dict(self) -> Dict[str, Any]:
        keys = [
            "version", "default_save_path", "listen_port", "dht", "lsd",
            "upnp", "natpmp", "max_download", "max_upload", "max_connections",
            "max_active_downloads", "max_active_uploads", "start_minimized",
            "delete_torrent_file_after_add",
        ]
        return {k: getattr(self, k) for k in keys}

    def update(self, data: Dict[str, Any]) -> None:
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()

    def save(self) -> None:
        self._path.write_text(json.dumps(self.as_dict(), indent=2), encoding="utf-8")
