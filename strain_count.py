#!/usr/bin/env python3
# usage:
#   python3 count_gbks_per_strain.py /path/to/gbks > strain_counts.csv
#   # or, if you are in that folder:
#   python3 count_gbks_per_strain.py > strain_counts.csv

import sys
from pathlib import Path
from collections import Counter

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")

counts = Counter()

# find all .gbk files (recursively)
for gbk in root.rglob("*.gbk"):
    name = gbk.stem  # filename without extension
    # strain ID = part before first underscore
    strain = name.split("_", 1)[0]
    counts[strain] += 1

# print CSV header
print("strain_id,count")
for strain, n in sorted(counts.items()):
    print(f"{strain},{n}")

