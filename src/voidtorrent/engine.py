"""VoidTorrent - core BitTorrent engine wrapper around libtorrent.

Mirrors the qBittorrent architecture: a single Session manages the native
libtorrent session, processes alerts on a worker thread, and exposes torrent
state to the UI via Qt signals.
"""

from __future__ import annotations

import time
import logging
import threading
from pathlib import Path
from typing import Dict, List, Optional

import libtorrent as lt
from PyQt6.QtCore import QObject, pyqtSignal

from .config import Settings

logger = logging.getLogger("voidtorrent.engine")

STATE_MAP = {
    lt.torrent_status.states.queued_for_checking: "Queued",
    lt.torrent_status.states.checking_files: "Checking",
    lt.torrent_status.states.downloading_metadata: "Downloading metadata",
    lt.torrent_status.states.downloading: "Downloading",
    lt.torrent_status.states.finished: "Finished",
    lt.torrent_status.states.seeding: "Seeding",
    lt.torrent_status.states.allocating: "Allocating",
    lt.torrent_status.states.checking_resume_data: "Checking resume data",
}


class TorrentState:
    """Plain-data snapshot of a torrent's live status for the UI layer."""

    def __init__(self) -> None:
        self.info_hash = ""
        self.name = ""
        self.save_path = ""
        self.progress = 0.0
        self.download_rate = 0
        self.upload_rate = 0
        self.total_download = 0
        self.total_upload = 0
        self.total_size = 0
        self.total_done = 0
        self.num_peers = 0
        self.num_seeds = 0
        self.state = "Unknown"
        self.eta = 0
        self.paused = False
        self.has_metadata = False
        self.files: List[dict] = []


class TorrentManager(QObject):
    """Owns the libtorrent session and all live torrents."""

    torrent_added = pyqtSignal(str)
    torrent_removed = pyqtSignal(str)
    torrent_updated = pyqtSignal(str)
    session_stats = pyqtSignal(dict)
    log_message = pyqtSignal(str)

    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self.settings = settings
        self.resume_dir = settings.profile_dir / "resume"
        self.resume_dir.mkdir(parents=True, exist_ok=True)

        self._session = self._create_session()
        self._handles: Dict[str, lt.torrent_handle] = {}
        self._lock = threading.Lock()
        self._running = True
        self._worker = threading.Thread(target=self._alert_loop, daemon=True)
        self._worker.start()

        self._restore_resume_data()

    def _create_session(self) -> lt.session:
        s = self.settings
        params = lt.session_params()
        pack = {
            "listen_interfaces": f"0.0.0.0:{s.listen_port}",
            "enable_dht": s.dht,
            "enable_lsd": s.lsd,
            "enable_upnp": s.upnp,
            "enable_natpmp": s.natpmp,
            "download_rate_limit": int(s.max_download * 1024),
            "upload_rate_limit": int(s.max_upload * 1024),
            "active_downloads": s.max_active_downloads,
            "active_seeds": s.max_active_uploads,
            "active_limit": s.max_active_downloads + s.max_active_uploads,
            "connections_limit": s.max_connections,
            "user_agent": f"VoidTorrent/{s.version}",
            "alert_mask": lt.alert.category_t.all_categories,
        }
        params.settings.update(pack)
        ses = lt.session(params)
        ses.add_dht_router("router.bittorrent.com", 6881)
        ses.add_dht_router("router.utorrent.com", 6881)
        return ses

    def apply_settings(self) -> None:
        s = self.settings
        pack = {
            "listen_interfaces": f"0.0.0.0:{s.listen_port}",
            "enable_dht": s.dht,
            "enable_lsd": s.lsd,
            "enable_upnp": s.upnp,
            "enable_natpmp": s.natpmp,
            "download_rate_limit": int(s.max_download * 1024),
            "upload_rate_limit": int(s.max_upload * 1024),
            "active_downloads": s.max_active_downloads,
            "active_seeds": s.max_active_uploads,
            "active_limit": s.max_active_downloads + s.max_active_uploads,
            "connections_limit": s.max_connections,
        }
        self._session.apply_settings(pack)

    def _alert_loop(self) -> None:
        while self._running:
            alerts = self._session.pop_alerts()
            for alert in alerts:
                self._handle_alert(alert)
            self._emit_session_stats()
            time.sleep(0.4)

    def _emit_session_stats(self) -> None:
        status = self._session.status()
        self.session_stats.emit({
            "download_rate": status.download_rate,
            "upload_rate": status.upload_rate,
            "total_download": status.total_download,
            "total_upload": status.total_upload,
            "num_peers": status.num_peers,
        })

    def _handle_alert(self, alert) -> None:
        t = type(alert).__name__
        if t == "state_update_alert":
            for st in alert.status:
                info_hash = str(st.info_hashes)
                with self._lock:
                    if info_hash in self._handles:
                        self.torrent_updated.emit(info_hash)
        elif t == "save_resume_data_alert":
            self._save_resume(alert)
        elif t == "torrent_finished_alert":
            self.log_message.emit(f"Completed: {alert.torrent_name}")
        elif t == "metadata_received_alert":
            self.torrent_updated.emit(str(alert.handle.info_hashes))
        elif t in ("torrent_error_alert", "file_error_alert"):
            self.log_message.emit(f"Error: {getattr(alert, 'message', 'unknown')}")

    # ------------------------------------------------------------------ #
    # Adding torrents
    # ------------------------------------------------------------------ #
    def add_torrent_file(self, path: str, save_path: Optional[str] = None,
                         sequential: bool = False) -> Optional[str]:
        save_path = save_path or self.settings.default_save_path
        Path(save_path).mkdir(parents=True, exist_ok=True)
        try:
            ti = lt.torrent_info(path)
        except RuntimeError as exc:
            self.log_message.emit(f"Failed to parse torrent: {exc}")
            return None
        return self._add_params(ti, save_path, sequential, is_magnet=False)

    def add_magnet(self, uri: str, save_path: Optional[str] = None,
                   sequential: bool = False) -> Optional[str]:
        save_path = save_path or self.settings.default_save_path
        Path(save_path).mkdir(parents=True, exist_ok=True)
        try:
            atp = lt.parse_magnet_uri(uri)
        except RuntimeError as exc:
            self.log_message.emit(f"Invalid magnet link: {exc}")
            return None
        atp.save_path = save_path
        atp.storage_mode = lt.storage_mode_t.storage_mode_sparse
        atp.flags |= lt.torrent_flags.auto_managed
        if sequential and atp.ti is not None:
            for i in range(atp.ti.num_files()):
                atp.file_priorities[i] = 0 if i > 0 else 4
        return self._register(atp, uri)

    def _add_params(self, ti, save_path, sequential, is_magnet):
        atp = lt.add_torrent_params()
        atp.ti = ti
        atp.save_path = save_path
        atp.storage_mode = lt.storage_mode_t.storage_mode_sparse
        atp.flags |= lt.torrent_flags.auto_managed
        if sequential:
            for i in range(ti.num_files()):
                atp.file_priorities[i] = 4 if i == 0 else 0
        return self._register(atp, ti.name())

    def _register(self, atp, label) -> Optional[str]:
        try:
            handle = self._session.add_torrent(atp)
        except RuntimeError as exc:
            self.log_message.emit(f"Failed to add {label}: {exc}")
            return None
        info_hash = str(handle.info_hashes)
        with self._lock:
            self._handles[info_hash] = handle
        self.torrent_added.emit(info_hash)
        self.log_message.emit(f"Added: {label}")
        return info_hash

    # ------------------------------------------------------------------ #
    # Control
    # ------------------------------------------------------------------ #
    def pause(self, info_hash: str) -> None:
        h = self._handles.get(info_hash)
        if h and h.is_valid():
            h.pause()

    def resume(self, info_hash: str) -> None:
        h = self._handles.get(info_hash)
        if h and h.is_valid():
            h.resume()
            h.set_flags(lt.torrent_flags.auto_managed)

    def remove(self, info_hash: str, delete_files: bool = False) -> None:
        h = self._handles.get(info_hash)
        if h and h.is_valid():
            self._session.remove_torrent(h, int(delete_files))
        with self._lock:
            self._handles.pop(info_hash, None)
        self._remove_resume(info_hash)
        self.torrent_removed.emit(info_hash)

    def set_sequential(self, info_hash: str, enabled: bool) -> None:
        h = self._handles.get(info_hash)
        if not (h and h.is_valid() and h.has_metadata()):
            return
        files = h.torrent_file().files()
        for i in range(files.num_files()):
            h.file_priority(i, 4 if enabled else 1)

    def set_file_priority(self, info_hash: str, file_index: int, priority: int) -> None:
        h = self._handles.get(info_hash)
        if h and h.is_valid() and h.has_metadata():
            h.file_priority(file_index, priority)

    # ------------------------------------------------------------------ #
    # State snapshots
    # ------------------------------------------------------------------ #
    def get_state(self, info_hash: str) -> Optional[TorrentState]:
        h = self._handles.get(info_hash)
        if not (h and h.is_valid()):
            return None
        st = TorrentState()
        status = h.status()
        st.info_hash = info_hash
        st.name = status.name or "Fetching metadata..."
        st.save_path = status.save_path
        st.progress = status.progress
        st.download_rate = status.download_rate
        st.upload_rate = status.upload_rate
        st.total_download = status.total_download
        st.total_upload = status.total_upload
        st.total_size = status.total
        st.total_done = status.total_done
        st.num_peers = status.num_peers
        st.num_seeds = status.num_seeds
        st.state = STATE_MAP.get(status.state, "Unknown")
        st.paused = status.paused
        st.has_metadata = h.has_metadata()
        if st.download_rate > 0 and st.total_size > 0:
            remaining = (st.total_size - st.total_done) / st.download_rate
            st.eta = int(remaining) if remaining > 0 else 0
        if h.has_metadata():
            files = h.torrent_file().files()
            fp = h.file_progress()
            st.files = [
                {
                    "index": i,
                    "path": files.file_path(i),
                    "size": files.file_size(i),
                    "progress": (fp[i] / files.file_size(i)) if files.file_size(i) else 1.0,
                    "priority": h.file_priority(i),
                }
                for i in range(files.num_files())
            ]
        return st

    def list_hashes(self) -> List[str]:
        with self._lock:
            return list(self._handles.keys())

    # ------------------------------------------------------------------ #
    # Resume data persistence
    # ------------------------------------------------------------------ #
    def _resume_path(self, info_hash: str) -> Path:
        return self.resume_dir / f"{info_hash}.resume"

    def _save_resume(self, alert) -> None:
        try:
            data = lt.write_resume_data_buf(alert.params)
        except Exception as exc:  # noqa: BLE001
            logger.warning("resume write failed: %s", exc)
            return
        info_hash = str(alert.handle.info_hashes)
        (self.resume_dir / f"{info_hash}.resume").write_bytes(data)

    def save_all_resume(self) -> None:
        for h in self._handles.values():
            if h.is_valid():
                h.save_resume_data()

    def _remove_resume(self, info_hash: str) -> None:
        p = self._resume_path(info_hash)
        if p.exists():
            p.unlink()

    def _restore_resume_data(self) -> None:
        for f in self.resume_dir.glob("*.resume"):
            try:
                data = f.read_bytes()
                atp = lt.read_resume_data(data)
                atp.save_path = atp.save_path or self.settings.default_save_path
                atp.flags |= lt.torrent_flags.auto_managed
                handle = self._session.add_torrent(atp)
                info_hash = str(handle.info_hashes)
                self._handles[info_hash] = handle
                self.torrent_added.emit(info_hash)
            except Exception as exc:  # noqa: BLE001
                logger.warning("resume restore failed for %s: %s", f.name, exc)

    def shutdown(self) -> None:
        self._running = False
        self.save_all_resume()
        time.sleep(0.6)
        self._session.pause()
        del self._session
