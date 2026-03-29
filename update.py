"""
Update Ergo Block Timestamps
=============================
Runs in GitHub Actions every 6 hours.
Reads the current year CSV, finds the last known height,
fetches all new blocks from Explorer API, appends to current year file.

Usage:
  python update.py
"""

import csv
import json
import os
import requests
import time
from datetime import datetime, timezone
from collections import defaultdict

EXPLORER = "https://api.ergoplatform.com/api/v1"
DATA_DIR = "data"
BATCH_SIZE = 50   # Explorer API max per request
DELAY = 0.2       # seconds between requests
BURST_EVERY = 10  # pause longer every N batches
BURST_PAUSE = 1.0 # seconds for burst pause


def get_current_height() -> int:
    """Get current chain tip from Explorer."""
    resp = requests.get(f"{EXPLORER}/info", timeout=15)
    resp.raise_for_status()
    return resp.json()["height"]


def get_blocks_batch(from_height: int, count: int) -> list:
    """Fetch a batch of blocks from Explorer using offset pagination.
    Explorer API: offset = height - 1 (height 1 is at offset 0)."""
    offset = from_height - 1
    url = (
        f"{EXPLORER}/blocks"
        f"?offset={offset}&limit={count}"
        f"&sortBy=height&sortDirection=asc"
    )
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json().get("items", [])


def get_last_height() -> int:
    """Find the highest block height across all yearly CSV files."""
    max_height = 0
    for fname in os.listdir(DATA_DIR):
        if not fname.startswith("blocks_") or not fname.endswith(".csv"):
            continue
        fpath = os.path.join(DATA_DIR, fname)
        with open(fpath, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                h = int(row['height'])
                if h > max_height:
                    max_height = h
    return max_height


def ts_to_dt(ts_ms: int) -> str:
    return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")


def get_year_file(year: int) -> str:
    return os.path.join(DATA_DIR, f"blocks_{year}.csv")


def append_rows(rows_by_year: dict):
    """Append new rows to the appropriate yearly CSV files."""
    for year, rows in rows_by_year.items():
        fpath = get_year_file(year)
        file_exists = os.path.exists(fpath)
        with open(fpath, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['height', 'timestamp_ms', 'datetime'])
            if not file_exists:
                writer.writeheader()
            writer.writerows(rows)
        print(f"  Appended {len(rows):,} rows to {fpath}")


def rebuild_json(updated_years):
    """Rebuild JSON files for updated years and the index."""
    for year in updated_years:
        csv_path = get_year_file(year)
        json_path = os.path.join(DATA_DIR, f"blocks_{year}.json")
        blocks = {}
        with open(csv_path, newline='') as f:
            for row in csv.DictReader(f):
                blocks[row['height']] = int(row['timestamp_ms'])
        with open(json_path, 'w') as f:
            json.dump(blocks, f, separators=(',', ':'))
        print(f"  Rebuilt {json_path} ({len(blocks):,} blocks)")

    # Rebuild index.json
    index = {"years": {}}
    total = 0
    for fname in sorted(os.listdir(DATA_DIR)):
        if not fname.startswith("blocks_") or not fname.endswith(".csv"):
            continue
        year = fname.replace("blocks_", "").replace(".csv", "")
        min_h, max_h, count = None, None, 0
        with open(os.path.join(DATA_DIR, fname), newline='') as f:
            for row in csv.DictReader(f):
                h = int(row['height'])
                if min_h is None or h < min_h:
                    min_h = h
                if max_h is None or h > max_h:
                    max_h = h
                count += 1
        index["years"][year] = {"min_height": min_h, "max_height": max_h, "count": count}
        total += count
    all_mins = [v["min_height"] for v in index["years"].values()]
    all_maxs = [v["max_height"] for v in index["years"].values()]
    index["first_height"] = min(all_mins)
    index["latest_height"] = max(all_maxs)
    index["total_blocks"] = total
    with open(os.path.join(DATA_DIR, "index.json"), 'w') as f:
        json.dump(index, f, indent=2)
    print(f"  Rebuilt data/index.json (latest: {index['latest_height']:,})")


def main():
    print("=" * 60)
    print("  ERGO BLOCK TIMESTAMPS UPDATE")
    print(f"  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 60)

    os.makedirs(DATA_DIR, exist_ok=True)

    # Find last known height
    last_height = get_last_height()
    print(f"\nLast known height: {last_height:,}")

    # Get current chain height
    current_height = get_current_height()
    print(f"Current chain height: {current_height:,}")

    blocks_to_fetch = current_height - last_height
    if blocks_to_fetch <= 0:
        print("\nAlready up to date!")
        return

    print(f"Fetching {blocks_to_fetch:,} new blocks...")

    rows_by_year = defaultdict(list)
    fetched = 0
    errors = 0
    start = time.time()

    fetch_from = last_height + 1
    while fetch_from <= current_height:
        count = min(BATCH_SIZE, current_height - fetch_from + 1)

        for attempt in range(3):
            try:
                items = get_blocks_batch(fetch_from, count)
                for item in items:
                    h = item.get("height")
                    ts = item.get("timestamp")
                    if h and ts:
                        year = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).year
                        rows_by_year[year].append({
                            'height': h,
                            'timestamp_ms': ts,
                            'datetime': ts_to_dt(ts)
                        })
                        fetched += 1
                break
            except Exception as e:
                print(f"  Error at height {fetch_from} (attempt {attempt+1}): {e}")
                if attempt < 2:
                    time.sleep(3)
                else:
                    errors += 1

        fetch_from += count
        batch_num = (fetch_from - last_height) // BATCH_SIZE
        if batch_num > 0 and batch_num % BURST_EVERY == 0:
            time.sleep(BURST_PAUSE)
        else:
            time.sleep(DELAY)

    # Append to yearly files
    append_rows(rows_by_year)

    # Rebuild JSON for updated years + index
    rebuild_json(rows_by_year.keys())

    elapsed = time.time() - start
    print(f"\nDone: {fetched:,} blocks fetched in {elapsed:.1f}s ({errors} errors)")

    # Summary for GitHub Actions log
    print(f"\n::notice::Updated {fetched:,} blocks up to height {current_height:,}")


if __name__ == "__main__":
    main()
