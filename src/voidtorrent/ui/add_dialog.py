"""Add-torrent dialog: accept a .torrent path or magnet link, pick a save folder."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFileDialog, QCheckBox, QFrame,
)

from ..theme import VOID_BLACK


class AddTorrentDialog(QDialog):
    def __init__(self, source: str = "", default_path: str = "", parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add Torrent - VoidTorrent")
        self.setMinimumWidth(520)
        self.setStyleSheet(f"QDialog {{ background-color: {VOID_BLACK}; }}")
        self.result_source = ""
        self.result_path = default_path
        self.result_sequential = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title = QLabel("Add Torrent")
        title.setObjectName("Title")
        layout.addWidget(title)

        dim = QLabel("Paste a magnet link or choose a .torrent file.")
        dim.setObjectName("Dim")
        layout.addWidget(dim)

        src_frame = QFrame()
        src_frame.setObjectName("Panel")
        src_layout = QVBoxLayout(src_frame)
        src_layout.setContentsMargins(14, 14, 14, 14)
        src_layout.setSpacing(10)

        self.source_edit = QLineEdit(source)
        self.source_edit.setPlaceholderText("magnet:?xt=urn:btih:...  or  path/to/file.torrent")
        src_layout.addWidget(self.source_edit)

        pick_row = QHBoxLayout()
        self.file_btn = QPushButton("Choose .torrent file")
        self.file_btn.clicked.connect(self._pick_file)
        pick_row.addWidget(self.file_btn)
        pick_row.addStretch(1)
        src_layout.addLayout(pick_row)
        layout.addWidget(src_frame)

        path_frame = QFrame()
        path_frame.setObjectName("Panel")
        path_layout = QVBoxLayout(path_frame)
        path_layout.setContentsMargins(14, 14, 14, 14)
        path_layout.setSpacing(10)

        path_label = QLabel("Save to")
        path_label.setObjectName("Dim")
        path_layout.addWidget(path_label)
        path_row = QHBoxLayout()
        self.path_edit = QLineEdit(default_path)
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self._pick_path)
        path_row.addWidget(self.path_edit)
        path_row.addWidget(self.browse_btn)
        path_layout.addLayout(path_row)

        self.sequential = QCheckBox("Download sequentially (stream-friendly)")
        path_layout.addWidget(self.sequential)
        layout.addWidget(path_frame)

        actions = QHBoxLayout()
        actions.addStretch(1)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        self.add_btn = QPushButton("Add")
        self.add_btn.setObjectName("Accent")
        self.add_btn.clicked.connect(self._accept)
        actions.addWidget(self.cancel_btn)
        actions.addWidget(self.add_btn)
        layout.addLayout(actions)

    def _pick_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Select .torrent file", "", "Torrent files (*.torrent)"
        )
        if path:
            self.source_edit.setText(path)
            self.path_edit.setText(str(Path(path).with_suffix("")))

    def _pick_path(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Select download folder")
        if path:
            self.path_edit.setText(path)

    def _accept(self) -> None:
        self.result_source = self.source_edit.text().strip()
        self.result_path = self.path_edit.text().strip()
        self.result_sequential = self.sequential.isChecked()
        if not self.result_source:
            return
        self.accept()
