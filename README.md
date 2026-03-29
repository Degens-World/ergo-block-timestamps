# ergo-block-timestamps

Complete Ergo blockchain block height → timestamp lookup table. Updated hourly via GitHub Actions. Public API available.

## API

Base URL: `https://ergo-block-timestamps.vercel.app`

### Get a single block

```
GET /api/block/1752521
```
```json
{
  "height": 1752521,
  "timestamp_ms": 1774800957664,
  "datetime": "2026-03-29T16:15:57.664000"
}
```

### Get a range of blocks

```
GET /api/blocks?from=1752000&to=1752010
```
```json
{
  "blocks": [
    {"height": 1752000, "timestamp_ms": 1774738527691, "datetime": "..."},
    ...
  ],
  "count": 11
}
```

Max 1,000 blocks per request.

### Dataset info

```
GET /api/info
```
```json
{
  "latest_height": 1752578,
  "first_height": 2,
  "total_blocks": 1752577,
  "years": { "2019": {"min_height": 2, "max_height": 132121, "count": 132120}, ... }
}
```

## Data Files

Yearly CSVs and JSONs in `data/`:

| File | Coverage |
|------|----------|
| `data/blocks_2019.csv` / `.json` | Genesis → Dec 2019 |
| `data/blocks_2020.csv` / `.json` | 2020 |
| `data/blocks_2021.csv` / `.json` | 2021 |
| `data/blocks_2022.csv` / `.json` | 2022 |
| `data/blocks_2023.csv` / `.json` | 2023 |
| `data/blocks_2024.csv` / `.json` | 2024 |
| `data/blocks_2025.csv` / `.json` | 2025 |
| `data/blocks_2026.csv` / `.json` | 2026 → present |

**CSV columns:** `height`, `timestamp_ms`, `datetime`
**JSON format:** `{"height": timestamp_ms, ...}`

## Direct usage (without API)

```python
import csv

height_to_ts = {}
for year in [2025, 2026]:
    with open(f'data/blocks_{year}.csv') as f:
        for row in csv.DictReader(f):
            height_to_ts[int(row['height'])] = int(row['timestamp_ms'])
```

## Update frequency

Every hour via GitHub Actions. Each push triggers a Vercel redeploy so the API stays current.
