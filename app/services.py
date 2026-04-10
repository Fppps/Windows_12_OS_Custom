from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote_plus

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices


@dataclass
class WeatherService:
    data: dict

    def open_general(self) -> None:
        self.search(f"{self.data.get('location', 'Weather')} weather")

    def open_wind(self) -> None:
        self.search(f"{self.data.get('location', 'Weather')} wind")

    def open_humidity(self) -> None:
        self.search(f"{self.data.get('location', 'Weather')} humidity")

    def open_forecast(self) -> None:
        self.search(f"{self.data.get('location', 'Weather')} forecast")

    @staticmethod
    def search(query: str) -> None:
        QDesktopServices.openUrl(QUrl(f'https://www.google.com/search?q={quote_plus(query)}'))


@dataclass
class NetworkService:
    data: dict

    def open_general(self) -> None:
        self.search(f"{self.data.get('name', 'network')} wifi settings")

    def open_adapter(self) -> None:
        self.search(f"{self.data.get('adapter', 'wifi adapter')} driver")

    def open_signal(self) -> None:
        self.search(f"how to improve wifi signal {self.data.get('name', '')}")

    @staticmethod
    def search(query: str) -> None:
        QDesktopServices.openUrl(QUrl(f'https://www.google.com/search?q={quote_plus(query)}'))


@dataclass
class RuntimeState:
    system_data: dict

    @property
    def volume(self) -> int:
        return int(self.system_data['sound']['volume'])

    @volume.setter
    def volume(self, value: int) -> None:
        self.system_data['sound']['volume'] = max(0, min(100, int(value)))

    @property
    def brightness(self) -> int:
        return int(self.system_data['display']['brightness'])

    @brightness.setter
    def brightness(self, value: int) -> None:
        self.system_data['display']['brightness'] = max(0, min(100, int(value)))

    @property
    def night_light(self) -> bool:
        return bool(self.system_data['display']['night_light'])

    @night_light.setter
    def night_light(self, value: bool) -> None:
        self.system_data['display']['night_light'] = bool(value)
