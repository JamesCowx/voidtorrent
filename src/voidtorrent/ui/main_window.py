"""VoidTorrent main window (Qt Widgets)."""

from __future__ import annotations

import sys
from pathlib import Path


def _asset_path(filename: str) -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "assets" / filename
    return Path(__file__).resolve().parents[3] / "assets" / filename


from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QToolBar, QPushButton, QLabel, QProgressBar, QTabWidget, QSizePolicy,
    QListWidget, QListWidgetItem, QMenu, QFileDialog, QFrame, QHeaderView,
    QSystemTrayIcon, QMessageBox, QApplication,
)
from PyQt6.QtGui import QIcon

from ..engine import TorrentManager, TorrentState
from ..config import Settings, VERSION
from ..theme import VOID_PURPLE, VOID_TEXT_DIM, VOID_TEXT, VOID_BORDER
from ..utils import human_size, human_speed, human_eta
from .add_dialog import AddTorrentDialog
from .options_dialog import OptionsDialog


class MainWindow(QMainWindow):
    def __init__(self, manager: TorrentManager, settings: Settings) -> None:
        super().__init__()
        self.manager = manager
        self.settings = settings
        self.setWindowTitle(f"VoidTorrent {VERSION}")
        self.setMinimumSize(980, 640)
        self.resize(1100, 720)

        icon_path = _asset_path("logo.svg")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self._build_tray()
        self._build_ui()
        self._wire_signals()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._refresh)
        self.timer.start(1000)

        if settings.start_minimized:
            self.hide()
        else:
            self.show()

    # ------------------------------------------------------------------ #
    def _build_tray(self) -> None:
        icon = self._make_icon()
        self.tray = QSystemTrayIcon(icon, self)
        self.tray.setToolTip("VoidTorrent")
        menu = QMenu()
        show_action = menu.addAction("Show VoidTorrent")
        show_action.triggered.connect(self.show)
        quit_action = menu.addAction("Quit")
        quit_action.triggered.connect(QApplication.quit)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(
            lambda reason: self.show() if reason == QSystemTrayIcon.ActivationReason.DoubleClick else None
        )
        self.tray.show()

    def _make_icon(self) -> QIcon:
        icon_path = _asset_path("logo.svg")
        if icon_path.exists():
            return QIcon(str(icon_path))
        from PyQt6.QtGui import QPixmap, QPainter, QBrush
        pix = QPixmap(32, 32)
        pix.fill(Qt.GlobalColor.transparent)
        p = QPainter(pix)
        p.setBrush(QBrush(Qt.GlobalColor.black))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(4, 4, 24, 24)
        p.end()
        return QIcon(pix)

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        root.addWidget(self._build_toolbar())
        root.addWidget(self._build_stats_bar())
        root.addWidget(self._build_lists(), 1)

    def _build_toolbar(self) -> QToolBar:
        bar = QToolBar()
        bar.setMovable(False)
        bar.setObjectName("MainToolbar")

        # Brand: logo image + wordmark
        brand = QWidget()
        brand_layout = QHBoxLayout(brand)
        brand_layout.setContentsMargins(6, 0, 10, 0)
        brand_layout.setSpacing(7)
        icon_path = _asset_path("logo.svg")
        logo_img = QLabel()
        if icon_path.exists():
            logo_img.setPixmap(QIcon(str(icon_path)).pixmap(24, 24))
        logo_img.setStyleSheet("padding: 0; background: transparent;")
        brand_layout.addWidget(logo_img)
        void_lbl = QLabel("VOID")
        void_lbl.setStyleSheet(f"color: {VOID_TEXT}; font-weight: 800; font-size: 14px; letter-spacing: 2px; background: transparent;")
        brand_layout.addWidget(void_lbl)
        tor_lbl = QLabel("TORRENT")
        tor_lbl.setStyleSheet(f"color: {VOID_PURPLE}; font-weight: 600; font-size: 14px; letter-spacing: 2px; background: transparent;")
        brand_layout.addWidget(tor_lbl)
        bar.addWidget(brand)
        bar.addSeparator()

        add_file = QPushButton("+ Add Torrent File")
        add_file.setObjectName("Accent")
        add_file.setToolTip("Open a .torrent file from your computer")
        add_file.clicked.connect(self._add_file)
        add_magnet = QPushButton("Add Magnet Link")
        add_magnet.setToolTip("Paste a magnet:?xt=urn:btih:… link")
        add_magnet.clicked.connect(self._add_magnet)
        pause = QPushButton("Pause")
        pause.setToolTip("Pause selected torrent(s)")
        pause.clicked.connect(lambda: self._control("pause"))
        resume = QPushButton("Resume")
        resume.setToolTip("Resume selected torrent(s)")
        resume.clicked.connect(lambda: self._control("resume"))
        remove = QPushButton("Remove")
        remove.setToolTip("Remove selected torrent(s)")
        remove.clicked.connect(lambda: self._control("remove"))
        options = QPushButton("Options")
        options.setToolTip("Configure download limits, port, and network settings")
        options.clicked.connect(self._open_options)

        for w in (add_file, add_magnet, pause, resume, remove, options):
            bar.addWidget(w)
        bar.addSeparator()
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        bar.addWidget(spacer)
        return bar

    def _build_stats_bar(self) -> QWidget:
        frame = QFrame()
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(0)

        def _stat(label, value_color=VOID_TEXT):
            lbl = QLabel(label)
            lbl.setStyleSheet(f"color: {value_color}; font-weight: 600; font-size: 13px;")
            return lbl

        self.dl_label = _stat("▼ 0 B/s", VOID_PURPLE)
        self.ul_label = _stat("▲ 0 B/s", VOID_TEXT)
        self.total_label = _stat("0 active", VOID_TEXT_DIM)

        sep = QLabel("•")
        sep.setStyleSheet(f"color: {VOID_BORDER}; padding: 0 18px;")
        layout.addWidget(self.dl_label)
        layout.addWidget(sep)
        layout.addWidget(self.ul_label)
        layout.addWidget(sep)
        layout.addWidget(self.total_label)
        layout.addStretch(1)

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(f"color: {VOID_TEXT_DIM}; font-size: 12px;")
        layout.addWidget(self.status_label)
        return frame

    def _build_lists(self) -> QWidget:
        tabs = QTabWidget()
        self.tree = QTreeWidget()
        self.tree.setRootIsDecorated(False)
        self.tree.setAlternatingRowColors(True)
        self.tree.setHeaderLabels(
            ["Name", "Status", "Progress", "Size", "Down", "Up", "Peers", "ETA", ""]
        )
        self.tree.hideColumn(8)
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self._context_menu)
        self.tree.itemSelectionChanged.connect(self._on_select)
        tabs.addTab(self.tree, "Transfers")

        detail = QWidget()
        dlayout = QVBoxLayout(detail)
        dlayout.setContentsMargins(14, 14, 14, 14)
        files_header = QLabel("FILES")
        files_header.setStyleSheet(f"color: {VOID_TEXT_DIM}; font-weight: 600; font-size: 12px; letter-spacing: 1px;")
        dlayout.addWidget(files_header)
        self.files_list = QListWidget()
        self.files_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.files_list.customContextMenuRequested.connect(self._file_menu)
        dlayout.addWidget(self.files_list, 1)
        tabs.addTab(detail, "Details")

        self.log_list = QListWidget()
        tabs.addTab(self.log_list, "Log")

        self._tabs = tabs
        return tabs

    # ------------------------------------------------------------------ #
    def _wire_signals(self) -> None:
        self.manager.torrent_added.connect(self._on_added)
        self.manager.torrent_removed.connect(self._on_removed)
        self.manager.torrent_updated.connect(self._on_updated)
        self.manager.session_stats.connect(self._on_stats)
        self.manager.log_message.connect(self._on_log)

    # ------------------------------------------------------------------ #
    @pyqtSlot(str)
    def _on_added(self, info_hash: str) -> None:
        if self.tree.findItems(info_hash, Qt.MatchFlag.MatchExactly, 8):
            return
        item = QTreeWidgetItem(self.tree)
        item.setText(8, info_hash)
        self._update_item(item, self.manager.get_state(info_hash))

    @pyqtSlot(str)
    def _on_removed(self, info_hash: str) -> None:
        for item in self.tree.findItems(info_hash, Qt.MatchFlag.MatchExactly, 8):
            self.tree.takeTopLevelItem(self.tree.indexOfTopLevelItem(item))

    @pyqtSlot(str)
    def _on_updated(self, info_hash: str) -> None:
        items = self.tree.findItems(info_hash, Qt.MatchFlag.MatchExactly, 8)
        if items:
            self._update_item(items[0], self.manager.get_state(info_hash))

    @pyqtSlot(dict)
    def _on_stats(self, stats: dict) -> None:
        self.dl_label.setText(f"▼ {human_speed(stats['download_rate'])}")
        self.ul_label.setText(f"▲ {human_speed(stats['upload_rate'])}")
        active = len(self.manager.list_hashes())
        self.total_label.setText(f"{active} active")
        if stats["download_rate"] > 0:
            self.status_label.setText("Downloading…")
        elif stats["upload_rate"] > 0:
            self.status_label.setText("Seeding…")
        else:
            self.status_label.setText("Idle")

    @pyqtSlot(str)
    def _on_log(self, msg: str) -> None:
        self.log_list.addItem(msg)
        self.log_list.scrollToBottom()

    # ------------------------------------------------------------------ #
    def _update_item(self, item: QTreeWidgetItem, st: TorrentState | None) -> None:
        if not st:
            return
        item.setText(0, st.name)
        item.setText(1, st.state if not st.paused else "Paused")
        item.setText(2, f"{st.progress * 100:.1f}%")
        item.setText(3, human_size(st.total_size))
        item.setText(4, human_speed(st.download_rate))
        item.setText(5, human_speed(st.upload_rate))
        item.setText(6, f"{st.num_peers}" if st.num_peers else "-")
        item.setText(7, human_eta(st.eta))
        item.setTextAlignment(2, Qt.AlignmentFlag.AlignRight)

    def _refresh(self) -> None:
        for info_hash in self.manager.list_hashes():
            items = self.tree.findItems(info_hash, Qt.MatchFlag.MatchExactly, 8)
            if items:
                self._update_item(items[0], self.manager.get_state(info_hash))

    # ------------------------------------------------------------------ #
    def _selected_hash(self) -> str | None:
        item = self.tree.currentItem()
        return item.text(8) if item else None

    def _add_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Open .torrent", "", "Torrent files (*.torrent)"
        )
        if path:
            self._spawn_dialog(path)

    def _add_magnet(self) -> None:
        self._spawn_dialog("")

    def _spawn_dialog(self, source: str) -> None:
        dlg = AddTorrentDialog(source, self.settings.default_save_path, self)
        if dlg.exec():
            src = dlg.result_source
            path = dlg.result_path
            seq = dlg.result_sequential
            if src.startswith("magnet:"):
                self.manager.add_magnet(src, path, seq)
            elif src.endswith(".torrent"):
                self.manager.add_torrent_file(src, path, seq)
                if self.settings.delete_torrent_file_after_add:
                    try:
                        Path(src).unlink()
                    except OSError:
                        pass

    def _control(self, action: str) -> None:
        h = self._selected_hash()
        if not h:
            return
        if action == "pause":
            self.manager.pause(h)
        elif action == "resume":
            self.manager.resume(h)
        elif action == "remove":
            self._remove_hash(h)

    def _context_menu(self, pos) -> None:
        item = self.tree.itemAt(pos)
        if not item:
            return
        h = item.text(8)
        menu = QMenu()
        menu.addAction("Pause", lambda: self.manager.pause(h))
        menu.addAction("Resume", lambda: self.manager.resume(h))
        menu.addAction("Remove", lambda: self._remove_hash(h))
        menu.exec(self.tree.viewport().mapToGlobal(pos))

    def _remove_hash(self, info_hash: str) -> None:
        reply = QMessageBox.question(
            self, "Remove torrent",
            "Remove the torrent? Choose whether to also delete the downloaded files.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
        )
        if reply == QMessageBox.StandardButton.Cancel:
            return
        delete = reply == QMessageBox.StandardButton.Yes
        self.manager.remove(info_hash, delete_files=delete)

    def _file_menu(self, pos) -> None:
        item = self.files_list.itemAt(pos)
        if not item:
            return
        idx = item.data(Qt.ItemDataRole.UserRole)
        menu = QMenu()
        menu.addAction("High priority", lambda: self._set_priority(idx, 7))
        menu.addAction("Normal priority", lambda: self._set_priority(idx, 1))
        menu.addAction("Skip file", lambda: self._set_priority(idx, 0))
        menu.exec(self.files_list.viewport().mapToGlobal(pos))

    def _set_priority(self, file_index: int, priority: int) -> None:
        h = self._selected_hash()
        if h:
            self.manager.set_file_priority(h, file_index, priority)
            self._on_select()

    def _on_select(self) -> None:
        h = self._selected_hash()
        self.files_list.clear()
        if not h:
            return
        st = self.manager.get_state(h)
        if not st or not st.has_metadata:
            return
        for f in st.files:
            item = QListWidgetItem(f"{f['path']}  ({human_size(f['size'])})")
            item.setData(Qt.ItemDataRole.UserRole, f["index"])
            self.files_list.addItem(item)

    def _open_options(self) -> None:
        OptionsDialog(self.settings, self).exec()

    def on_settings_changed(self) -> None:
        self.manager.apply_settings()

    # ------------------------------------------------------------------ #
    def closeEvent(self, event) -> None:
        event.ignore()
        self.hide()
        self.tray.showMessage("VoidTorrent", "Minimized to tray", QSystemTrayIcon.MessageIcon.Information, 1500)
