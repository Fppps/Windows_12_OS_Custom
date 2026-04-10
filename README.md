# Windows 12 Preview - R1U00 Official Project Update

This is a Python + JSON desktop-shell concept built with PySide6.

Included in this build:
- full-screen shell
- login screen
- working Start menu
- This PC window
- Settings window
- weather, search, network, sound, display, calendar, and about flyouts
- JSON-driven data for apps, system state, settings, and wallpaper choices

## Run

1. Double-click `launch_windows.bat`
2. Or install manually:
   - `pip install -r requirements.txt`
   - `python validate_data.py`
   - `python main.py`

## Demo sign-in

Password: `preview`

## Project notes

- This build uses locally bundled assets only.
- It does not bundle Google image results or Microsoft assets.
- All visible controls in the shell are wired to actions.


## R1U00 Add-ons build

- Fixed the `QUrl` import issue by moving it to `PySide6.QtCore`.
- Added a desktop context menu, welcome screen, supervisor restart flow, cleaner Settings home cards, better wallpapers, and improved Start menu positioning.
- Desktop and taskbar stay minimal, with This PC as the main app surface.


## Native folder added

- Added an optional `native/` folder with C sources and build scripts.
- The Python shell can load `w12native.dll` if you build it, but it still runs without it.
- This is an **official project update** for your concept shell, not an official Microsoft update.
