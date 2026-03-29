"""
Fill gap blocks in block_timestamps_master.csv
===============================================
Fetches missing blocks via local Ergo node and writes
block_timestamps_master_fixed.csv

Run from the repo root directory.
"""

import csv
import requests
from datetime import datetime, timezone

NODE = "http://localhost:9053"
INPUT_FILE = "block_timestamps_master.csv"
OUTPUT_FILE = "block_timestamps_master_fixed.csv"


def get_block_timestamp(height: int):
    """Fetch timestamp for a single block height via local node."""
    try:
        # Get header IDs at this height
        resp = requests.get(f"{NODE}/blocks/at/{height}", timeout=10)
        if resp.status_code == 200:
            header_ids = resp.json()
            if header_ids:
                # Get full block header for timestamp
                resp2 = requests.get(f"{NODE}/blocks/{header_ids[0]}/header", timeout=10)
                if resp2.status_code == 200:
                    return resp2.json().get("timestamp")
    except Exception as e:
        print(f"  Error at height {height}: {e}")
    return None


def main():
    print("=" * 60)
    print("  FILL GAP BLOCKS")
    print("=" * 60)

    # Load existing data
    print(f"\nLoading {INPUT_FILE}...")
    rows = {}
    with open(INPUT_FILE, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows[int(row['height'])] = row
    print(f"  Loaded {len(rows):,} rows")

    # Find gaps
    all_h = sorted(rows.keys())
    gaps = []
    for i in range(1, len(all_h)):
        if all_h[i] - all_h[i-1] > 1:
            for missing in range(all_h[i-1] + 1, all_h[i]):
                gaps.append(missing)

    print(f"  Found {len(gaps):,} missing blocks")

    if not gaps:
        print("  No gaps found — already complete!")
        return

    # Fetch missing blocks from local node
    print(f"\nFetching {len(gaps):,} missing blocks from node...")
    filled = 0
    errors = 0

    for i, height in enumerate(gaps):
        ts = get_block_timestamp(height)
        if ts:
            dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")
            rows[height] = {'height': height, 'timestamp_ms': ts, 'datetime': dt}
            filled += 1
        else:
            errors += 1
            print(f"  Failed: {height}")

        if (i + 1) % 500 == 0:
            print(f"  Progress: {i+1}/{len(gaps)} ({filled} filled, {errors} errors)")

    # Write output
    print(f"\nWriting {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['height', 'timestamp_ms', 'datetime'])
        writer.writeheader()
        for h in sorted(rows.keys()):
            writer.writerow(rows[h])

    print(f"\nDone: {len(rows):,} rows -> {OUTPUT_FILE}")
    print(f"  Filled: {filled}, Errors: {errors}")


if __name__ == "__main__":
    main()
