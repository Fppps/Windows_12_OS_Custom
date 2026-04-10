from __future__ import annotations

import ctypes
from ctypes import c_char_p, c_int
from pathlib import Path
from typing import Any


class NativeBridge:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.lib: Any | None = None
        self.loaded_from: str | None = None
        self.load_error: str | None = None

    def _candidates(self) -> list[Path]:
        native = self.root / 'native'
        return [
            native / 'build' / 'w12native.dll',
            native / 'out' / 'Release' / 'w12native.dll',
            native / 'out' / 'w12native.dll',
            native / 'build' / 'libw12native.so',
        ]

    def load(self) -> bool:
        for candidate in self._candidates():
            if not candidate.exists():
                continue
            try:
                self.lib = ctypes.CDLL(str(candidate))
                self.lib.w12_native_version.restype = c_char_p
                self.lib.w12_native_desktop_blur_supported.restype = c_int
                self.lib.w12_native_wallpaper_slots.restype = c_int
                self.loaded_from = str(candidate)
                self.load_error = None
                return True
            except Exception as exc:
                self.load_error = str(exc)
        return False

    def version(self) -> str:
        if not self.lib:
            return 'native layer not loaded'
        raw = self.lib.w12_native_version()
        if isinstance(raw, (bytes, bytearray)):
            return raw.decode('utf-8', errors='replace')
        return str(raw)

    def desktop_blur_supported(self) -> bool:
        if not self.lib:
            return False
        return bool(self.lib.w12_native_desktop_blur_supported())

    def wallpaper_slots(self) -> int:
        if not self.lib:
            return 0
        return int(self.lib.w12_native_wallpaper_slots())


def init_native_layer(root: Path) -> NativeBridge:
    bridge = NativeBridge(root)
    bridge.load()
    return bridge
