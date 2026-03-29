"""
Split block_timestamps_master_fixed.csv into yearly CSV files
=============================================================
Output: data/blocks_YYYY.csv for each year

Run from the repo root directory.
After running fill_gaps.py
"""

import csv
import os
from datetime import datetime, timezone
from collections import defaultdict

INPUT_FILE = "block_timestamps_master_fixed.csv"
OUTPUT_DIR = "data"


def main():
    print("=" * 60)
    print("  SPLIT BY YEAR")
    print("=" * 60)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load and bucket by year
    print(f"\nLoading {INPUT_FILE}...")
    by_year = defaultdict(list)

    with open(INPUT_FILE, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts_ms = int(row['timestamp_ms'])
            year = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).year
            by_year[year].append({
                'height': int(row['height']),
                'timestamp_ms': ts_ms,
                'datetime': row['datetime']
            })

    print(f"  Years found: {sorted(by_year.keys())}")

    # Write yearly files
    for year in sorted(by_year.keys()):
        rows = sorted(by_year[year], key=lambda r: r['height'])
        out_file = os.path.join(OUTPUT_DIR, f"blocks_{year}.csv")
        with open(out_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['height', 'timestamp_ms', 'datetime'])
            writer.writeheader()
            writer.writerows(rows)
        print(f"  {out_file}: {len(rows):,} rows  ({rows[0]['height']:,} - {rows[-1]['height']:,})")

    total = sum(len(v) for v in by_year.values())
    print(f"\nDone: {total:,} total rows across {len(by_year)} files")


if __name__ == "__main__":
    main()
