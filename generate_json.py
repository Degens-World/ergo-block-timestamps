"""
Generate JSON data files from yearly CSVs
==========================================
One-time bootstrap: reads each data/blocks_YYYY.csv and writes:
  - data/blocks_YYYY.json  (flat {height: timestamp_ms} mapping)
  - data/index.json         (year boundaries + metadata)

Run from repo root:
  python generate_json.py
"""

import csv
import json
import os

DATA_DIR = "data"


def main():
    print("=" * 60)
    print("  GENERATE JSON DATA FILES")
    print("=" * 60)

    year_files = sorted(f for f in os.listdir(DATA_DIR)
                        if f.startswith("blocks_") and f.endswith(".csv"))

    if not year_files:
        print("No CSV files found in data/")
        return

    index = {"years": {}}
    total_blocks = 0

    for fname in year_files:
        year = fname.replace("blocks_", "").replace(".csv", "")
        csv_path = os.path.join(DATA_DIR, fname)
        json_path = os.path.join(DATA_DIR, f"blocks_{year}.json")

        blocks = {}
        min_h, max_h = None, None

        with open(csv_path, newline='') as f:
            for row in csv.DictReader(f):
                h = int(row['height'])
                blocks[str(h)] = int(row['timestamp_ms'])
                if min_h is None or h < min_h:
                    min_h = h
                if max_h is None or h > max_h:
                    max_h = h

        with open(json_path, 'w') as f:
            json.dump(blocks, f, separators=(',', ':'))

        size_mb = os.path.getsize(json_path) / 1_000_000
        count = len(blocks)
        total_blocks += count
        print(f"  {json_path}: {count:,} blocks ({size_mb:.1f} MB)")

        index["years"][year] = {
            "min_height": min_h,
            "max_height": max_h,
            "count": count
        }

    all_mins = [v["min_height"] for v in index["years"].values()]
    all_maxs = [v["max_height"] for v in index["years"].values()]
    index["first_height"] = min(all_mins)
    index["latest_height"] = max(all_maxs)
    index["total_blocks"] = total_blocks

    index_path = os.path.join(DATA_DIR, "index.json")
    with open(index_path, 'w') as f:
        json.dump(index, f, indent=2)

    print(f"\n  {index_path}: heights {index['first_height']:,} - {index['latest_height']:,}")
    print(f"\nDone: {total_blocks:,} total blocks across {len(year_files)} years")


if __name__ == "__main__":
    main()
