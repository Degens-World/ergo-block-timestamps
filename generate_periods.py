"""
Generate period boundary files from block data
================================================
Reads all data/blocks_YYYY.csv and produces:
  - data/days.json    (daily boundaries)
  - data/weeks.json   (ISO week boundaries)
  - data/months.json  (calendar month boundaries)
  - data/years.json   (yearly boundaries)

Run from repo root:
  python generate_periods.py
"""

import csv
import json
import os
from datetime import datetime, timezone

DATA_DIR = "data"

MONTH_NAMES = ["", "January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]


def load_all_blocks():
    blocks = []
    for fname in sorted(os.listdir(DATA_DIR)):
        if not fname.startswith("blocks_") or not fname.endswith(".csv"):
            continue
        with open(os.path.join(DATA_DIR, fname), newline='') as f:
            for row in csv.DictReader(f):
                blocks.append((int(row['height']), int(row['timestamp_ms'])))
    blocks.sort()
    return blocks


def ts_to_utc(ts_ms):
    return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)


def main():
    print("=" * 60)
    print("  GENERATE PERIOD BOUNDARIES")
    print("=" * 60)

    blocks = load_all_blocks()
    print(f"\nLoaded {len(blocks):,} blocks")

    # --- Days ---
    days = {}
    for height, ts_ms in blocks:
        key = ts_to_utc(ts_ms).strftime('%Y-%m-%d')
        if key not in days:
            days[key] = {'block_start': height, 'block_end': height}
        else:
            days[key]['block_end'] = height

    days_list = []
    for key in sorted(days.keys()):
        d = days[key]
        dt = datetime.strptime(key, '%Y-%m-%d')
        days_list.append({
            'date': key, 'year': dt.year, 'month': dt.month, 'day': dt.day,
            'block_start': d['block_start'], 'block_end': d['block_end'],
            'count': d['block_end'] - d['block_start'] + 1,
        })

    with open(os.path.join(DATA_DIR, 'days.json'), 'w') as f:
        json.dump(days_list, f, separators=(',', ':'))
    print(f"  data/days.json: {len(days_list)} days")

    # --- Weeks (ISO) ---
    weeks = {}
    for height, ts_ms in blocks:
        dt = ts_to_utc(ts_ms)
        iso_year, iso_week, _ = dt.isocalendar()
        key = f"{iso_year}-W{iso_week:02d}"
        if key not in weeks:
            weeks[key] = {"year": iso_year, "week": iso_week,
                          "block_start": height, "block_end": height,
                          "ts_start": ts_ms, "ts_end": ts_ms}
        else:
            weeks[key]["block_end"] = height
            weeks[key]["ts_end"] = ts_ms

    weeks_list = []
    for key in sorted(weeks.keys()):
        w = weeks[key]
        weeks_list.append({
            "year": w["year"], "week": w["week"], "label": f"W{w['week']:02d}",
            "block_start": w["block_start"], "block_end": w["block_end"],
            "date_start": ts_to_utc(w["ts_start"]).strftime("%Y-%m-%d"),
            "date_end": ts_to_utc(w["ts_end"]).strftime("%Y-%m-%d"),
        })

    with open(os.path.join(DATA_DIR, 'weeks.json'), 'w') as f:
        json.dump(weeks_list, f, separators=(',', ':'))
    print(f"  data/weeks.json: {len(weeks_list)} weeks")

    # --- Months ---
    months = {}
    for height, ts_ms in blocks:
        dt = ts_to_utc(ts_ms)
        key = f"{dt.year}-{dt.month:02d}"
        if key not in months:
            months[key] = {"year": dt.year, "month": dt.month,
                           "block_start": height, "block_end": height,
                           "ts_start": ts_ms, "ts_end": ts_ms}
        else:
            months[key]["block_end"] = height
            months[key]["ts_end"] = ts_ms

    months_list = []
    for key in sorted(months.keys()):
        m = months[key]
        months_list.append({
            "year": m["year"], "month": m["month"], "name": MONTH_NAMES[m["month"]],
            "label": f"M{m['month']:02d}", "block_start": m["block_start"],
            "block_end": m["block_end"],
            "date_start": ts_to_utc(m["ts_start"]).strftime("%Y-%m-%d"),
            "date_end": ts_to_utc(m["ts_end"]).strftime("%Y-%m-%d"),
        })

    with open(os.path.join(DATA_DIR, 'months.json'), 'w') as f:
        json.dump(months_list, f, separators=(',', ':'))
    print(f"  data/months.json: {len(months_list)} months")

    # --- Years ---
    years = {}
    for height, ts_ms in blocks:
        y = ts_to_utc(ts_ms).year
        if y not in years:
            years[y] = {"block_start": height, "block_end": height,
                        "ts_start": ts_ms, "ts_end": ts_ms, "count": 1}
        else:
            years[y]["block_end"] = height
            years[y]["ts_end"] = ts_ms
            years[y]["count"] += 1

    years_list = []
    for y in sorted(years.keys()):
        yr = years[y]
        years_list.append({
            "year": y, "block_start": yr["block_start"], "block_end": yr["block_end"],
            "count": yr["count"],
            "date_start": ts_to_utc(yr["ts_start"]).strftime("%Y-%m-%d"),
            "date_end": ts_to_utc(yr["ts_end"]).strftime("%Y-%m-%d"),
        })

    with open(os.path.join(DATA_DIR, 'years.json'), 'w') as f:
        json.dump(years_list, f, separators=(',', ':'))
    print(f"  data/years.json: {len(years_list)} years")

    print(f"\nDone.")


if __name__ == "__main__":
    main()
