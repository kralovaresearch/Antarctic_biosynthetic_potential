#!/usr/bin/env python3
import argparse
import csv
from pathlib import Path
import sys

def parse_args():
    p = argparse.ArgumentParser(
        description="Check that <strain>_bakta folders (and optional result files) exist for all strains in a CSV."
    )
    p.add_argument("-c", "--csv", required=True, type=Path,
                   help="CSV file containing strain IDs.")
    p.add_argument("-b", "--base-dir", type=Path, default=Path.cwd(),
                   help="Base directory where *_bakta folders live (default: current dir).")
    p.add_argument("--col", default=None,
                   help="Column name to read from CSV. If omitted, uses the first column.")
    p.add_argument("--suffix", default="_bakta",
                   help="Suffix for Bakta folders (default: _bakta).")
    p.add_argument("--require-ext", choices=["gbff", "embl", "gff", "tsv"], default=None,
                   help="If set, also require at least one file with this extension inside the folder (e.g. gbff).")
    p.add_argument("--write-rerun", action="store_true",
                   help="Write a rerun.sh with one bakta command per missing strain (customize paths as needed).")
    p.add_argument("--db", default="/home/stanci/Desktop/Programs/db",
                   help="DB path to include in rerun.sh (only used if --write-rerun).")
    p.add_argument("--threads", type=int, default=4,
                   help="Threads for rerun.sh (only used if --write-rerun).")
    p.add_argument("--fasta-dir", type=Path, default=None,
                   help="Directory containing FASTA files for rerun.sh (default: base-dir).")
    p.add_argument("--fasta-ext", default=".fasta",
                   help="FASTA extension for rerun.sh (default: .fasta).")
    return p.parse_args()

def read_strains_from_csv(csv_path: Path, colname: str | None):
    strains = []
    with csv_path.open(newline='', encoding='utf-8') as f:
        sniffer = csv.Sniffer()
        sample = f.read(4096)
        f.seek(0)
        dialect = sniffer.sniff(sample) if sample else csv.excel
        reader = csv.reader(f, dialect)
        rows = list(reader)

    if not rows:
        return strains

    # If a header exists and user provided a column name, use it
    header = rows[0]
    if colname:
        # build DictReader and pull the named column
        with csv_path.open(newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f, dialect=dialect)
            for row in reader:
                val = (row.get(colname) or "").strip()
                if val:
                    strains.append(val)
        return strains

    # No column provided: use the first column for all rows, skipping header if it looks like text
    def looks_like_header(value: str) -> bool:
        v = value.strip().lower()
        return any(k in v for k in ("strain", "id", "sample"))

    start_idx = 1 if rows and rows[0] and looks_like_header(rows[0][0]) else 0
    for r in rows[start_idx:]:
        if not r:
            continue
        val = (r[0] or "").strip()
        if val:
            strains.append(val)
    return strains

def main():
    args = parse_args()
    base = args.base_dir.resolve()
    if not base.is_dir():
        sys.exit(f"ERROR: Base directory not found: {base}")

    strains = read_strains_from_csv(args.csv, args.col)
    if not strains:
        sys.exit(f"ERROR: No strains found in CSV: {args.csv}")

    present, missing, present_but_no_result = [], [], []
    required_glob = f"*.{args.require_ext}" if args.require_ext else None

    for s in strains:
        folder = base / f"{s}{args.suffix}"
        if not folder.is_dir():
            missing.append(s)
            continue

        if required_glob:
            found = any(folder.glob(required_glob))
            if not found:
                present_but_no_result.append(s)
            else:
                present.append(s)
        else:
            present.append(s)

    # Write lists
    (base / "present.txt").write_text("\n".join(present) + ("\n" if present else ""), encoding="utf-8")
    (base / "missing.txt").write_text("\n".join(missing) + ("\n" if missing else ""), encoding="utf-8")
    (base / "present_but_no_result.txt").write_text(
        "\n".join(present_but_no_result) + ("\n" if present_but_no_result else ""), encoding="utf-8"
    )

    # Optionally write a rerun script for missing strains
    if args.write_rerun:
        fasta_dir = (args.fasta_dir or base).resolve()
        lines = [
            "#!/bin/bash",
            "# Auto-generated: rerun Bakta for missing strains",
            f'DB="{args.db}"',
            f'THREADS="{args.threads}"',
            f'TMPDIR="${{TMPDIR:-$HOME/bakta_tmp}}"',
            f'FASTA_DIR="{fasta_dir}"',
            f'FASTA_EXT="{args.fasta_ext}"',
            "",
            "mkdir -p \"$TMPDIR\"",
            ""
        ]
        for s in missing:
            fasta = f"${{FASTA_DIR}}/{s}{args.fasta_ext}"
            outdir = f"{s}{args.suffix}"
            lines += [
                f'echo "▶️  {s}"',
                f'bakta --db "$DB" --threads "$THREADS" --tmp-dir "$TMPDIR" --output "{outdir}" --force "{fasta}"',
                ""
            ]
        rerun_path = base / "rerun.sh"
        rerun_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        rerun_path.chmod(0o755)

    # Summary
    print(f"Base dir          : {base}")
    print(f"Total strains     : {len(strains)}")
    print(f"Present           : {len(present)}  (list: present.txt)")
    if args.require_ext:
        print(f"Present, no .{args.require_ext}: {len(present_but_no_result)}  (list: present_but_no_result.txt)")
    print(f"Missing folders   : {len(missing)}  (list: missing.txt)")
    if args.write_rerun:
        print(f"Wrote rerun script: {base / 'rerun.sh'}")

if __name__ == "__main__":
    main()

