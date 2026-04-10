from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class AppConfig:
    data_dir: Path

    def load(self, name: str) -> dict[str, Any]:
        path = self.data_dir / name
        with path.open('r', encoding='utf-8') as handle:
            return json.load(handle)

    def save(self, name: str, data: dict[str, Any]) -> None:
        path = self.data_dir / name
        with path.open('w', encoding='utf-8') as handle:
            json.dump(data, handle, indent=2)
            handle.write('\n')
