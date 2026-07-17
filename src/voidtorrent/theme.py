"""VoidTorrent visual theme: black base, greyscale surfaces, purple accent."""

from __future__ import annotations

VOID_BLACK = "#060508"
VOID_PANEL = "#0e0d14"
VOID_PANEL_2 = "#141220"
VOID_BORDER = "#231f30"
VOID_TEXT = "#ECEAF2"
VOID_TEXT_DIM = "#9a93ac"
VOID_PURPLE = "#7c4dd6"
VOID_PURPLE_SOFT = "#9a6fe6"
VOID_PURPLE_GLOW = "#5b2ea8"
VOID_GREY = "#3a3a42"

QSS = f"""
QWidget {{
    background-color: {VOID_BLACK};
    color: {VOID_TEXT};
    font-family: "Segoe UI", "Inter", sans-serif;
    font-size: 13px;
}}
QMainWindow, QDialog {{
    background-color: {VOID_BLACK};
}}
QFrame#Panel {{
    background-color: {VOID_PANEL};
    border: 1px solid {VOID_BORDER};
    border-radius: 10px;
}}
QToolBar {{
    background-color: {VOID_PANEL};
    border: none;
    border-bottom: 1px solid {VOID_BORDER};
    padding: 4px 6px;
    spacing: 6px;
}}
QToolBar::separator {{
    width: 1px;
    background-color: {VOID_BORDER};
    margin: 4px 6px;
}}
QLineEdit, QComboBox, QSpinBox, QPlainTextEdit {{
    background-color: {VOID_PANEL_2};
    border: 1px solid {VOID_BORDER};
    border-radius: 8px;
    padding: 8px 12px;
    color: {VOID_TEXT};
    selection-background-color: {VOID_PURPLE};
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QPlainTextEdit:focus {{
    border: 1px solid {VOID_PURPLE};
}}
QPushButton {{
    background-color: {VOID_PANEL_2};
    border: 1px solid {VOID_BORDER};
    border-radius: 8px;
    padding: 8px 16px;
    color: {VOID_TEXT};
    font-weight: 500;
}}
QPushButton:hover {{
    border: 1px solid {VOID_PURPLE};
    background-color: #1f1a2c;
}}
QPushButton:pressed {{
    background-color: {VOID_PANEL};
}}
QPushButton#Accent {{
    background-color: {VOID_PURPLE};
    border: 1px solid {VOID_PURPLE};
    color: #ffffff;
    font-weight: 700;
    padding: 8px 18px;
}}
QPushButton#Accent:hover {{
    background-color: {VOID_PURPLE_SOFT};
    border: 1px solid {VOID_PURPLE_SOFT};
}}
QPushButton#Accent:pressed {{
    background-color: {VOID_PURPLE_GLOW};
}}
QPushButton:disabled {{
    color: {VOID_TEXT_DIM};
    background-color: {VOID_PANEL};
    border: 1px solid {VOID_BORDER};
}}
QTreeWidget, QListWidget, QTableWidget {{
    background-color: {VOID_PANEL};
    border: 1px solid {VOID_BORDER};
    border-radius: 10px;
    alternate-background-color: {VOID_PANEL_2};
    outline: none;
}}
QTreeWidget::item:selected, QListWidget::item:selected {{
    background-color: {VOID_PURPLE_GLOW};
    color: {VOID_TEXT};
}}
QTreeWidget::item:hover, QListWidget::item:hover {{
    background-color: rgba(124,77,214,30);
}}
QHeaderView::section {{
    background-color: {VOID_PANEL_2};
    color: {VOID_TEXT_DIM};
    border: none;
    border-bottom: 2px solid {VOID_BORDER};
    border-radius: 0;
    padding: 10px 8px;
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 1px;
}}
QTabWidget::pane {{
    border: 1px solid {VOID_BORDER};
    border-radius: 10px;
    top: -1px;
    background-color: {VOID_PANEL};
}}
QTabBar::tab {{
    background-color: {VOID_PANEL};
    color: {VOID_TEXT_DIM};
    padding: 9px 18px;
    border: 1px solid {VOID_BORDER};
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    color: {VOID_TEXT};
    background-color: {VOID_PANEL_2};
    border-bottom: 2px solid {VOID_PURPLE};
}}
QTabBar::tab:hover:!selected {{
    color: {VOID_TEXT};
    background-color: #1f1a2c;
}}
QProgressBar {{
    background-color: {VOID_PANEL_2};
    border: 1px solid {VOID_BORDER};
    border-radius: 5px;
    text-align: center;
    color: {VOID_TEXT};
    height: 8px;
}}
QProgressBar::chunk {{
    background-color: {VOID_PURPLE};
    border-radius: 4px;
}}
QStatusBar {{
    background-color: {VOID_PANEL};
    border-top: 1px solid {VOID_BORDER};
    color: {VOID_TEXT_DIM};
    font-size: 12px;
}}
QMenu {{
    background-color: {VOID_PANEL};
    border: 1px solid {VOID_BORDER};
    border-radius: 8px;
    padding: 6px;
}}
QMenu::item {{
    padding: 8px 28px 8px 16px;
    border-radius: 6px;
}}
QMenu::item:selected {{
    background-color: {VOID_PURPLE_GLOW};
}}
QMenu::separator {{
    height: 1px;
    background: {VOID_BORDER};
    margin: 4px 8px;
}}
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 2px;
}}
QScrollBar::handle:vertical {{
    background: {VOID_GREY};
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {VOID_PURPLE};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: transparent;
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 8px;
    margin: 2px;
}}
QScrollBar::handle:horizontal {{
    background: {VOID_GREY};
    border-radius: 4px;
    min-width: 30px;
}}
QScrollBar::handle:horizontal:hover {{
    background: {VOID_PURPLE};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}
QLabel#Title {{
    font-size: 22px;
    font-weight: 800;
    color: {VOID_TEXT};
    letter-spacing: -0.5px;
}}
QLabel#Dim {{
    color: {VOID_TEXT_DIM};
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {VOID_BORDER};
    border-radius: 4px;
    background: {VOID_PANEL_2};
}}
QCheckBox::indicator:checked {{
    background: {VOID_PURPLE};
    border: 1px solid {VOID_PURPLE};
}}
QToolTip {{
    background-color: {VOID_PANEL};
    color: {VOID_TEXT};
    border: 1px solid {VOID_BORDER};
    border-radius: 6px;
    padding: 6px 10px;
}}
"""
