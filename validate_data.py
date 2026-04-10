from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'

for path in sorted(DATA.glob('*.json')):
    with path.open('r', encoding='utf-8') as handle:
        json.load(handle)
    print(f'Validated {path.name}')

print('All JSON files loaded successfully.')
