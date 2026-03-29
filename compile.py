"""
Compile Yearly CSVs -> Master CSV + Master JSON
================================================
Merges all data/blocks_YYYY.csv files into:
  - block_timestamps_master.csv  (height, timestamp_ms, datetime)
  - block_timestamps_master.json ({"blocks": {"height": timestamp_ms, ...}})

Run from repo root after pulling latest data/:
  python compile.py

Optional flags:
  python compile.py --csv-only    (skip JSON, faster)
  python compile.py --json-only   (skip CSV)
  python compile.py --years 2025 2026  (compile specific years only)
"""

import csv
import json
import os
import sys
import time
from collections import defaultdict

DATA_DIR = "data"
OUT_CSV  = "block_timestamps_master.csv"
OUT_JSON = "block_timestamps_master.json"


def parse_args():
    args = sys.argv[1:]
    csv_only  = "--csv-only"  in args
    json_only = "--json-only" in args
    years = None
    if "--years" in args:
        idx = args.index("--years")
        years = [int(y) for y in args[idx+1:] if y.isdigit()]
    return csv_only, json_only, years


def get_year_files(years=None):
    files = []
    for fname in sorted(os.listdir(DATA_DIR)):
        if not fname.startswith("blocks_") or not fname.endswith(".csv"):
            continue
        if years:
            year = int(fname.replace("blocks_", "").replace(".csv", ""))
            if year not in years:
                continue
        files.append(os.path.join(DATA_DIR, fname))
    return files


def main():
    csv_only, json_only, years = parse_args()

    print("=" * 60)
    print("  COMPILE BLOCK TIMESTAMPS")
    print("=" * 60)

    year_files = get_year_files(years)
    if not year_files:
        print("No yearly files found in data/. Run split_by_year.py first.")
        return

    print(f"\nYearly files found: {len(year_files)}")
    for f in year_files:
        print(f"  {f}")

    # Load all rows
    print("\nLoading...")
    t0 = time.time()
    rows = {}  # height -> {height, timestamp_ms, datetime}

    for fpath in year_files:
        count_before = len(rows)
        with open(fpath, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                h = int(row['height'])
                rows[h] = {
                    'height': h,
                    'timestamp_ms': int(row['timestamp_ms']),
                    'datetime': row['datetime']
                }
        added = len(rows) - count_before
        print(f"  {os.path.basename(fpath)}: {added:,} rows")

    all_heights = sorted(rows.keys())
    total = len(all_heights)
    print(f"\nTotal: {total:,} rows  |  Heights: {all_heights[0]:,} - {all_heights[-1]:,}")

    # Write master CSV
    if not json_only:
        print(f"\nWriting {OUT_CSV}...")
        with open(OUT_CSV, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['height', 'timestamp_ms', 'datetime'])
            writer.writeheader()
            for h in all_heights:
                writer.writerow(rows[h])
        size_mb = os.path.getsize(OUT_CSV) / 1_000_000
        print(f"  Done: {size_mb:.1f} MB")

    # Write master JSON
    if not csv_only:
        print(f"\nWriting {OUT_JSON}...")
        blocks = {str(h): rows[h]['timestamp_ms'] for h in all_heights}
        with open(OUT_JSON, 'w') as f:
            json.dump({"blocks": blocks}, f, separators=(',', ':'))
        size_mb = os.path.getsize(OUT_JSON) / 1_000_000
        print(f"  Done: {size_mb:.1f} MB")

    elapsed = time.time() - t0
    print(f"\nCompile complete in {elapsed:.1f}s")
    print(f"  CSV:  {OUT_CSV}")
    print(f"  JSON: {OUT_JSON}")


if __name__ == "__main__":
    main()
