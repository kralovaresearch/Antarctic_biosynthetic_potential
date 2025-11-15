#!/usr/bin/env python3
# usage:
#   python3 bakta_replicon_summary.py > bakta_replicon_summary.tsv
#   # or: python3 bakta_replicon_summary.py /path/to/folder > out.tsv

import sys
from pathlib import Path
import re

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")

keys = ["Count", "oriCs", "oriVs", "oriTs"]
print("Genome\t" + "\t".join(keys))

# compile once; match lines like "Count: 5", allow spaces/tabs
pat = re.compile(r"^(Count|oriCs|oriVs|oriTs)\s*:\s*(\d+)\s*$")

rows = []
for txt in sorted(root.rglob("*.txt")):
    genome = txt.stem  # e.g., P12074 from P12074.txt
    vals = {k: "0" for k in keys}
    try:
        with txt.open("r", encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                m = pat.match(line.strip())
                if m:
                    vals[m.group(1)] = m.group(2)
    except Exception as e:
        # skip unreadable files quietly
        continue
    rows.append([genome] + [vals[k] for k in keys])

# print rows
for r in rows:
    print("\t".join(r))

