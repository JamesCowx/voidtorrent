"""Options dialog for VoidTorrent global settings."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QSpinBox,
    QPushButton, QFileDialog, QCheckBox, QFrame, QTabWidget, QWidget,
)

from ..config import Settings
from ..theme import VOID_BLACK


class OptionsDialog(QDialog):
    def __init__(self, settings: Settings, parent=None) -> None:
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Options - VoidTorrent")
        self.setMinimumWidth(560)
        self.setStyleSheet(f"QDialog {{ background-color: {VOID_BLACK}; }}")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        tabs = QTabWidget()
        tabs.addTab(self._general_tab(), "General")
        tabs.addTab(self._connection_tab(), "Connection")
        tabs.addTab(self._speed_tab(), "Speed")
        layout.addWidget(tabs)

        actions = QHBoxLayout()
        actions.addStretch(1)
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        save = QPushButton("Save")
        save.setObjectName("Accent")
        save.clicked.connect(self._save)
        actions.addWidget(cancel)
        actions.addWidget(save)
        layout.addLayout(actions)

    def _panel(self) -> QFrame:
        f = QFrame()
        f.setObjectName("Panel")
        f.setLayout(QVBoxLayout())
        f.layout().setContentsMargins(14, 14, 14, 14)
        f.layout().setSpacing(10)
        return f

    def _general_tab(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        panel = self._panel()
        row = QHBoxLayout()
        row.addWidget(QLabel("Default save path:"))
        self.save_path = QLineEdit(self.settings.default_save_path)
        browse = QPushButton("Browse")
        browse.clicked.connect(self._browse)
        row.addWidget(self.save_path)
        row.addWidget(browse)
        panel.layout().addLayout(row)

        self.del_torrent = QCheckBox("Delete .torrent file after adding")
        self.del_torrent.setChecked(self.settings.delete_torrent_file_after_add)
        panel.layout().addWidget(self.del_torrent)
        v.addWidget(panel)
        v.addStretch(1)
        return w

    def _connection_tab(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        panel = self._panel()

        port_row = QHBoxLayout()
        port_row.addWidget(QLabel("Listen port:"))
        self.port = QSpinBox()
        self.port.setRange(1024, 65535)
        self.port.setValue(self.settings.listen_port)
        port_row.addWidget(self.port)
        port_row.addStretch(1)
        panel.layout().addLayout(port_row)

        self.dht = QCheckBox("Enable DHT (decentralized peer discovery)")
        self.lsd = QCheckBox("Enable Local Peer Discovery (LSD)")
        self.upnp = QCheckBox("Enable UPnP port forwarding")
        self.natpmp = QCheckBox("Enable NAT-PMP port forwarding")
        for cb, val in ((self.dht, "dht"), (self.lsd, "lsd"),
                        (self.upnp, "upnp"), (self.natpmp, "natpmp")):
            cb.setChecked(getattr(self.settings, val))
            panel.layout().addWidget(cb)

        conn_row = QHBoxLayout()
        conn_row.addWidget(QLabel("Max connections:"))
        self.connections = QSpinBox()
        self.connections.setRange(10, 1000)
        self.connections.setValue(self.settings.max_connections)
        conn_row.addWidget(self.connections)
        conn_row.addStretch(1)
        panel.layout().addLayout(conn_row)

        v.addWidget(panel)
        v.addStretch(1)
        return w

    def _speed_tab(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        panel = self._panel()

        dl_row = QHBoxLayout()
        dl_row.addWidget(QLabel("Max download (KB/s, 0 = unlimited):"))
        self.max_dl = QSpinBox()
        self.max_dl.setRange(0, 100000)
        self.max_dl.setValue(self.settings.max_download)
        dl_row.addWidget(self.max_dl)
        panel.layout().addLayout(dl_row)

        ul_row = QHBoxLayout()
        ul_row.addWidget(QLabel("Max upload (KB/s, 0 = unlimited):"))
        self.max_ul = QSpinBox()
        self.max_ul.setRange(0, 100000)
        self.max_ul.setValue(self.settings.max_upload)
        ul_row.addWidget(self.max_ul)
        panel.layout().addLayout(ul_row)

        act_row = QHBoxLayout()
        act_row.addWidget(QLabel("Max active downloads:"))
        self.act_dl = QSpinBox()
        self.act_dl.setRange(1, 100)
        self.act_dl.setValue(self.settings.max_active_downloads)
        act_row.addWidget(self.act_dl)
        panel.layout().addLayout(act_row)

        actu_row = QHBoxLayout()
        actu_row.addWidget(QLabel("Max active uploads:"))
        self.act_ul = QSpinBox()
        self.act_ul.setRange(1, 100)
        self.act_ul.setValue(self.settings.max_active_uploads)
        actu_row.addWidget(self.act_ul)
        panel.layout().addLayout(actu_row)

        v.addWidget(panel)
        v.addStretch(1)
        return w

    def _browse(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select default folder")
        if path:
            self.save_path.setText(path)

    def _save(self) -> None:
        self.settings.update({
            "default_save_path": self.save_path.text(),
            "listen_port": self.port.value(),
            "dht": self.dht.isChecked(),
            "lsd": self.lsd.isChecked(),
            "upnp": self.upnp.isChecked(),
            "natpmp": self.natpmp.isChecked(),
            "max_connections": self.connections.value(),
            "max_download": self.max_dl.value(),
            "max_upload": self.max_ul.value(),
            "max_active_downloads": self.act_dl.value(),
            "max_active_uploads": self.act_ul.value(),
            "delete_torrent_file_after_add": self.del_torrent.isChecked(),
        })
        if self.parent():
            self.parent().on_settings_changed()
        self.accept()
