#!/usr/bin/env python3
"""
Extract protocluster info from antiSMASH .gbk files.

Usage:
    python3 gbk_overview.py /path/to/gbks > gbks_overview.csv
    # or, if you're in the folder with gbks:
    python3 gbk_overview.py > gbks_overview.csv

Output columns:
    gbk_name,protocluster_number,start,end,length_bp,product,category,contig_edge
"""

import sys
from pathlib import Path
import csv
from Bio import SeqIO

# Root directory with .gbk files (default = current directory)
root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")

out = csv.writer(sys.stdout)
out.writerow([
    "gbk_name",
    "protocluster_number",
    "start",
    "end",
    "length_bp",
    "product",
    "category",
    "contig_edge",
])

for gbk_path in sorted(root.rglob("*.gbk")):
    gbk_name = gbk_path.name  # keep full filename, including .gbk

    for record in SeqIO.parse(gbk_path, "genbank"):
        for feat in record.features:
            if feat.type != "protocluster":
                continue

            q = feat.qualifiers

            # Biopython locations are 0-based, half-open: [start, end)
            # Convert to 1-based inclusive coordinates
            loc = feat.location
            start = int(loc.start) + 1
            end = int(loc.end)
            length_bp = end - start + 1

            protocluster_number = q.get("protocluster_number", [""])[0]
            product = q.get("product", [""])[0]
            category = q.get("category", [""])[0]
            contig_edge = q.get("contig_edge", [""])[0]

            out.writerow([
                gbk_name,
                protocluster_number,
                start,
                end,
                length_bp,
                product,
                category,
                contig_edge,
            ])

