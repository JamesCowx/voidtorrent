"""Build a self-contained VoidTorrent installer (.exe) using PyInstaller.

Produces build/VoidTorrent-1.0.0-x64-setup.exe that extracts VoidTorrent to
%LOCALAPPDATA%\VoidTorrent, creates Start Menu + desktop shortcuts, and can
launch the app. The prebuilt VoidTorrent.exe is embedded (zlib+base64) and
appended to the installer so the output is a single file with no dependencies.
"""

from __future__ import annotations

import base64
import os
import pathlib
import sys
import tempfile
import zlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST_EXE = ROOT / "build" / "dist" / "VoidTorrent.exe"
OUT = ROOT / "build" / "VoidTorrent-1.0.0-x64-setup.exe"

MARK = "===VOIDTORRENT_PAYLOAD==="

BOOTSTRAP = r'''
import base64, os, sys, zlib, subprocess

MARK = "===VOIDTORRENT_PAYLOAD==="

def extract_payload():
    data = open(sys.executable, "rb").read()
    sep = b"==VOIDTORRENT_SEP=="
    i = data.find(sep)
    if i == -1:
        sys.exit("Error: installer payload not found. The installer may be corrupted.")
    raw = data[i + len(sep):]
    return zlib.decompress(base64.b64decode(raw))

def make_shortcut(path, target, icon):
    # Use WScript.Shell COM (pywin32 bundled into the installer) for reliability.
    try:
        from win32com.client import Dispatch
        ws = Dispatch("WScript.Shell")
        sc = ws.CreateShortcut(path)
        sc.TargetPath = target
        sc.IconLocation = "%s,0" % icon
        sc.WorkingDirectory = os.path.dirname(target)
        sc.save()
        return True
    except Exception as e:
        sys.stderr.write("shortcut failed: %s\n" % e)
        return False

def main():
    local = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    instdir = os.path.join(local, "VoidTorrent")
    os.makedirs(instdir, exist_ok=True)
    exe = os.path.join(instdir, "VoidTorrent.exe")
    payload = extract_payload()
    with open(exe, "wb") as f:
        f.write(payload)

    sm = os.path.join(os.environ.get("APPDATA", ""),
                      "Microsoft", "Windows", "Start Menu", "Programs", "VoidTorrent")
    os.makedirs(sm, exist_ok=True)
    make_shortcut(os.path.join(sm, "VoidTorrent.lnk"), exe, exe)
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    make_shortcut(os.path.join(desktop, "VoidTorrent.lnk"), exe, exe)

    print("VoidTorrent installed to %s" % instdir)
    try:
        ans = input("Launch VoidTorrent now? [Y/n] ").strip().lower()
    except Exception:
        ans = "y"
    if ans in ("", "y", "yes"):
        subprocess.Popen([exe], cwd=instdir)

if __name__ == "__main__":
    main()
'''


def build():
    if not DIST_EXE.exists():
        sys.exit("Missing %s - run Build-VoidTorrent.ps1 first." % DIST_EXE)

    try:
        import PyInstaller.__main__ as pyi  # noqa: F401
    except Exception:
        sys.exit("PyInstaller is required to build the installer. Install it and retry.")

    exe_bytes = DIST_EXE.read_bytes()
    payload = base64.b64encode(zlib.compress(exe_bytes, 9)).decode("ascii")

    tmp = tempfile.mkdtemp()
    boot_path = os.path.join(tmp, "boot.py")
    with open(boot_path, "w", encoding="utf-8") as f:
        f.write(BOOTSTRAP)

    work = ROOT / "build" / "installer_work"
    pyi.run([
        boot_path,
        "--onefile",
        "--console",
        "--name", "VoidTorrent-setup",
        "--hidden-import", "win32com",
        "--hidden-import", "win32com.client",
        "--hidden-import", "pythoncom",
        "--distpath", str(OUT.parent),
        "--workpath", str(work),
        "--specpath", str(work),
    ])

    built = OUT.parent / "VoidTorrent-setup.exe"
    if not built.exists():
        sys.exit("PyInstaller did not produce the installer executable.")

    with open(built, "ab") as f:
        f.write(("==VOIDTORRENT_SEP==" + payload).encode("utf-8"))
    os.replace(built, OUT)
    print("Installer written:", OUT, "(%d bytes)" % OUT.stat().st_size)
    # Cleanup temp files
    import shutil
    os.unlink(boot_path)
    shutil.rmtree(tmp, ignore_errors=True)
    shutil.rmtree(str(work), ignore_errors=True)


if __name__ == "__main__":
    build()
