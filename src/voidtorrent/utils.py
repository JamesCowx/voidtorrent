"""Shared formatting helpers for VoidTorrent."""

from __future__ import annotations


def human_size(num: float) -> str:
    if num is None:
        return "0 B"
    num = float(num)
    for unit in ("B", "KB", "MB", "GB", "TB", "PB"):
        if abs(num) < 1024.0:
            return f"{num:.1f} {unit}"
        num /= 1024.0
    return f"{num:.1f} EB"


def human_speed(num: float) -> str:
    if not num:
        return "0 B/s"
    return f"{human_size(num)}/s"


def human_eta(seconds: int) -> str:
    if not seconds or seconds < 0:
        return "∞"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h {m}m"
    if m:
        return f"{m}m {s}s"
    return f"{s}s"
