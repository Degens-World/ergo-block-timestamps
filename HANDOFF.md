# Ergo Block Timestamps — Handoff

## Objective

GitHub repo (`ergo-block-timestamps`) maintaining a complete, gap-free Ergo
blockchain block height → timestamp lookup table, split into yearly CSV files,
with master CSV + JSON convenience files, and a GitHub Actions workflow that
auto-updates every hour.

**Repo**: `https://github.com/Degens-World/ergo-block-timestamps`

---

## Current State (as of March 29, 2026)

- **1,752,520 rows**, heights 2–1,752,521
- **0 gaps, 0 dupes** (verified via `check_timestamps.py`)
- All gap blocks filled via local Ergo node (`localhost:9053`)
- Data split into 8 yearly files (2019–2026)

---

## Repo Structure

```
ergo-block-timestamps/
  data/
    blocks_2019.csv      (132,120 rows)
    blocks_2020.csv      (263,236 rows)
    blocks_2021.csv      (258,648 rows)
    blocks_2022.csv      (254,420 rows)
    blocks_2023.csv      (259,782 rows)
    blocks_2024.csv      (261,280 rows)
    blocks_2025.csv      (260,453 rows)
    blocks_2026.csv      (62,581 rows, growing)
  block_timestamps_master.csv     (~86 MB)
  block_timestamps_master.json    (~41 MB)
  fill_gaps.py
  split_by_year.py
  compile.py
  update.py
  check_timestamps.py
  README.md
  HANDOFF.md
  .github/
    workflows/
      update.yml
```

---

## Scripts Reference

### `fill_gaps.py`
- Input: `block_timestamps_master.csv`
- Output: `block_timestamps_master_fixed.csv`
- API: Local Ergo node (`localhost:9053`)
- Run once locally to fix historical gaps

### `split_by_year.py`
- Input: `block_timestamps_master_fixed.csv`
- Output: `data/blocks_YYYY.csv`
- Run once locally after fill_gaps.py

### `compile.py`
- Input: `data/blocks_YYYY.csv` (all years)
- Output: `block_timestamps_master.csv` + `block_timestamps_master.json`
- Run locally anytime to rebuild master files from yearly sources
- Flags: `--csv-only`, `--json-only`, `--years 2025 2026`

### `update.py`
- Run by GitHub Actions every hour
- Finds last known height across all yearly CSVs
- Fetches new blocks from Explorer API in batches of 50
- Appends to current year CSV (creates new year file if needed)
- Does NOT rebuild master CSV/JSON (run compile.py locally for that)

### `check_timestamps.py`
- Input: `block_timestamps_master.csv` (must be in same directory)
- Prints: total rows, dupes, min/max height, gap count and details
- Run locally to verify integrity

---

## CSV Format

All files use identical format:

```
height,timestamp_ms,datetime
2,1561978989703,2019-07-01T06:03:09
3,1561979000032,2019-07-01T06:03:20
```

- `height`: integer block height
- `timestamp_ms`: Unix timestamp in milliseconds (UTC)
- `datetime`: ISO 8601 UTC string (no timezone suffix)

---

## GitHub Actions Workflow Notes

- Workflow file: `.github/workflows/update.yml`
- Runs on: `ubuntu-latest`
- Schedule: `0 * * * *` (every hour)
- Permissions: `contents: write` (needed to push CSV updates)
- Only commits if data changed (uses `git diff --cached --quiet` check)
- Commit author: `github-actions[bot]`

No secrets or API keys required — Explorer API is public.

---

## Explorer API Details

Base URL: `https://api.ergoplatform.com/api/v1`

Endpoints used:
- `GET /info` → current chain height (`fullHeight` field)
- `GET /blocks?fromHeight=X&toHeight=Y&limit=50&sortBy=height&sortDirection=asc`
  → returns array of block objects with `height` and `timestamp` fields

Rate limit: no hard limit, but use 0.15s delay between requests to be safe.

---

## Usage in Other Scripts

```python
import csv

# Load just the years you need (fast)
height_to_ts = {}
for year in [2025, 2026]:
    with open(f'data/blocks_{year}.csv') as f:
        for row in csv.DictReader(f):
            height_to_ts[int(row['height'])] = int(row['timestamp_ms'])

ts_ms = height_to_ts.get(1700000)

# Or load the full master (slow, ~80MB)
with open('block_timestamps_master.csv') as f:
    for row in csv.DictReader(f):
        height_to_ts[int(row['height'])] = int(row['timestamp_ms'])
```

---

## Known Issues / Watch For

- **Year rollover**: On Jan 1 each year, `update.py` will automatically create
  a new `blocks_YYYY.csv` file for the new year. First run of the new year may
  show 0 rows in the new file — this is fine, it populates on the next run.

- **Explorer API downtime**: If the API is down, the GitHub Actions run will
  fail. This is fine — it retries in 1 hour. Gaps will be filled on the
  next successful run since `update.py` always starts from the last known height.

- **Master files drift**: The committed `block_timestamps_master.csv` and `.json`
  will become stale over time as yearly files grow. Pull the repo and run
  `python compile.py` locally to refresh them, then push the updated masters.
