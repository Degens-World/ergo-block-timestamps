import json
import os
from datetime import datetime, timezone

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')

_index_cache = None
_year_cache = {}


def load_index():
    global _index_cache
    if _index_cache is None:
        with open(os.path.join(DATA_DIR, 'index.json')) as f:
            _index_cache = json.load(f)
    return _index_cache


def height_to_year(height):
    index = load_index()
    for year_str, info in index['years'].items():
        if info['min_height'] <= height <= info['max_height']:
            return int(year_str)
    return None


def load_year(year):
    if year not in _year_cache:
        with open(os.path.join(DATA_DIR, f'blocks_{year}.json')) as f:
            _year_cache[year] = json.load(f)
    return _year_cache[year]


def lookup_block(height):
    year = height_to_year(height)
    if year is None:
        return None
    data = load_year(year)
    ts = data.get(str(height))
    if ts is None:
        return None
    dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")
    return {"height": height, "timestamp_ms": ts, "datetime": dt}
