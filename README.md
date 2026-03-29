# ergo-block-timestamps

Complete Ergo blockchain block height → timestamp lookup table, split by year. Updated automatically every 6 hours via GitHub Actions.

## Data

| File | Coverage |
|------|----------|
| `data/blocks_2019.csv` | Genesis → Dec 2019 |
| `data/blocks_2020.csv` | Jan 2020 → Dec 2020 |
| `data/blocks_2021.csv` | Jan 2021 → Dec 2021 |
| `data/blocks_2022.csv` | Jan 2022 → Dec 2022 |
| `data/blocks_2023.csv` | Jan 2023 → Dec 2023 |
| `data/blocks_2024.csv` | Jan 2024 → Dec 2024 |
| `data/blocks_2025.csv` | Jan 2025 → Dec 2025 |
| `data/blocks_2026.csv` | Jan 2026 → present |

**Columns:** `height`, `timestamp_ms`, `datetime`

## Usage

```python
import csv

# Load just the years you need
height_to_ts = {}
for year in [2025, 2026]:
    with open(f'data/blocks_{year}.csv') as f:
        for row in csv.DictReader(f):
            height_to_ts[int(row['height'])] = int(row['timestamp_ms'])

ts = height_to_ts.get(1700000)
```

## Setup (first time)

1. Run locally to fill historical data:
```bash
python fill_gaps.py        # Fix any gap blocks
python split_by_year.py    # Split master CSV into yearly files
```

2. Push `data/` folder to this repo.

3. GitHub Actions handles all future updates automatically.

## Update frequency

Every 6 hours via cron. Can also be triggered manually from the Actions tab.
