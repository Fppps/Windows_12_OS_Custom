# Native C layer

This folder contains optional C sources for the Windows 12 Preview concept.

They are **not required** to run the Python shell. They are here as a clean place
for native helpers you may want later, such as:
- desktop blur experiments
- restart / watchdog hooks
- wallpaper utilities
- future window-effect helpers

## Build on Windows with MinGW

Run:

```bat
build_native.bat
```

That produces:
- `native\\build\\w12native.dll`

## Build with CMake

```bat
cmake -S native -B native\\out
cmake --build native\\out --config Release
```

## Current exported functions

- `w12_native_version`
- `w12_native_restart_requested`
- `w12_native_mark_restart`
- `w12_native_clear_restart`
- `w12_native_desktop_blur_supported`
- `w12_native_wallpaper_slots`
