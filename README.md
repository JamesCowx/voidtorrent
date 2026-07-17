# VoidTorrent

A dark, minimal, ad-free BitTorrent client for Windows.

VoidTorrent is built on the battle-tested [libtorrent](https://www.libtorrent.org/)
engine (the same core used by qBittorrent) with a sleek PyQt6 interface in a
black / greyscale color scheme with red accents.

## Features

- Add `.torrent` files or magnet links
- Per-file selection and priority
- Sequential download (stream-friendly)
- DHT, PEX, Local Peer Discovery, UPnP / NAT-PMP
- Global speed limits and connection caps
- Resume data persistence across restarts
- System tray minimize
- No ads, no telemetry, fully open source (GPLv3)

## Project layout

```
VoidTorrent/
├── src/voidtorrent/        # Python package (engine + UI + theme)
│   ├── engine.py           # libtorrent session manager + alerts loop
│   ├── config.py           # persistent JSON settings
│   ├── theme.py            # black/red QSS stylesheet
│   ├── __main__.py         # app entry point
│   └── ui/                 # PyQt6 windows & dialogs
├── build/
│   ├── voidtorrent.spec    # PyInstaller spec
│   └── Build-VoidTorrent.ps1
├── website/                # static marketing site (download + how-to)
├── launcher.py             # top-level launcher used by PyInstaller
└── pyproject.toml
```

## Run from source (Windows)

```powershell
pip install PyQt6 libtorrent
cd src
python -m voidtorrent            # opens the GUI
python -m voidtorrent "magnet:?xt=urn:btih:..."   # add a magnet
```

## Build the standalone .exe

```powershell
cd build
.\Build-VoidTorrent.ps1
# -> build/dist/VoidTorrent.exe            (portable, self-contained)
# -> build/VoidTorrent-1.0.0-x64-setup.exe (installer: Start Menu + desktop shortcuts)
```

The build script generates the brand icon (`assets/voidtorrent.ico`) from
`build/make_icon.py`, compiles the portable `.exe` via PyInstaller, then wraps
it in a self-extracting installer that creates Start Menu and desktop
shortcuts.

> Note: on networks behind an SSL-inspecting proxy, install packages with
> `pip install --use-feature=truststore ...` so pip trusts the Windows
> certificate store.

## Website

The `website/` folder is a static site. Open `website/index.html` or serve it:

```powershell
cd website
python -m http.server 8000
# visit http://localhost:8000
```

## License

GPLv3. VoidTorrent is a tool for transferring data; respect copyright law and
only download content you are entitled to access.
