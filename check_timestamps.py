import csv

heights = []
with open('block_timestamps_master.csv', newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        heights.append(int(row['height']))

dupes = len(heights) - len(set(heights))
all_h = sorted(heights)
gaps = [(all_h[i-1], all_h[i]) for i in range(1, len(all_h)) if all_h[i] - all_h[i-1] > 1]

print(f'Total rows:  {len(heights):,}')
print(f'Dupes:       {dupes}')
print(f'Min height:  {all_h[0]:,}')
print(f'Max height:  {all_h[-1]:,}')
print(f'Gaps (count):{len(gaps)}')
if gaps:
    print('First 10 gaps:')
    for g in gaps[:10]:
        print(f'  {g[0]:,} -> {g[1]:,} (missing {g[1]-g[0]-1} blocks)')
