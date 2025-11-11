#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

def parse_args():
    p = argparse.ArgumentParser(description="Batch-run Bakta for all FASTA files (prefix before first underscore).")
    p.add_argument("-i", "--input-dir", required=True, type=Path, help="Directory with FASTA files.")
    p.add_argument("-d", "--db", required=True, type=Path, help="Path to Bakta database.")
    p.add_argument("-o", "--output-dir", type=Path, default=None,
                   help="Optional base output directory (default: next to each FASTA).")
    p.add_argument("-t", "--threads", type=int, default=max(1, (os.cpu_count() or 2) - 1),
                   help="Threads for Bakta (default: CPUs minus one).")
    p.add_argument("--ext", nargs="+", default=[".fasta", ".fa", ".fna"],
                   help="FASTA extensions (default: .fasta .fa .fna).")
    p.add_argument("--overwrite", action="store_true", help="Force overwriting existing _bakta folders (adds --force).")
    p.add_argument("--dry-run", action="store_true", help="Show commands without running.")
    return p.parse_args()

def derive_prefix(stem: str) -> str:
    """Everything before the first underscore."""
    return stem.split("_", 1)[0] if "_" in stem else stem

def find_fastas(indir: Path, exts):
    files = []
    for ext in exts:
        files.extend(indir.glob(f"*{ext}"))
    return sorted(set(files))

def run_bakta(fasta: Path, db: Path, outdir: Path, threads: int, overwrite: bool, dry_run: bool) -> int:
    """Run Bakta on one FASTA file."""
    cmd = [
        "bakta",
        "--db", str(db),
        "--threads", str(threads),
        "--output", str(outdir),
    ]
    if overwrite:
        cmd.append("--force")
    cmd.append(str(fasta))

    print(f"\n🔹 Running Bakta on {fasta.name}")
    print(f"   Output : {outdir}")
    print(f"   Threads: {threads}")
    print(f"   Cmd    : {' '.join(cmd)}")

    if dry_run:
        return 0

    # Make sure old folders are gone if overwriting
    if overwrite and outdir.exists():
        shutil.rmtree(outdir, ignore_errors=True)

    # Run Bakta and capture output
    tmp_log = Path(tempfile.gettempdir()) / f"{fasta.stem}_bakta.log"
    with tmp_log.open("w", encoding="utf-8") as logf:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in proc.stdout:
            print(line, end="")
            logf.write(line)
        rc = proc.wait()

    if rc == 0:
        outdir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(tmp_log), outdir / "bakta.log")
    else:
        print(f"❌ Bakta failed for {fasta.name} (exit code {rc})")
        print(f"   Log saved at {tmp_log}")
    return rc

def main():
    args = parse_args()
    if shutil.which("bakta") is None:
        sys.exit("ERROR: Bakta not found in PATH. Activate your environment first.")

    input_dir = args.input_dir.resolve()
    db = args.db.resolve()
    base_out = args.output_dir.resolve() if args.output_dir else None

    fastas = find_fastas(input_dir, args.ext)
    if not fastas:
        sys.exit(f"No FASTA files with extensions {args.ext} found in {input_dir}")

    print(f"Found {len(fastas)} FASTA files.")
    successes = skips = failures = 0

    for fasta in fastas:
        prefix = derive_prefix(fasta.stem)
        outdir = (base_out if base_out else fasta.parent) / f"{prefix}_bakta"

        if outdir.exists() and not args.overwrite:
            print(f"⚠️  Skipping {fasta.name}: {outdir} already exists (use --overwrite to replace)")
            skips += 1
            continue

        rc = run_bakta(fasta, db, outdir, args.threads, args.overwrite, args.dry_run)
        if rc == 0:
            successes += 1
        else:
            failures += 1

    print("\nSummary:")
    print(f"  ✅ Successful: {successes}")
    print(f"  ⚠️ Skipped   : {skips}")
    print(f"  ❌ Failed    : {failures}")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

def parse_args():
    p = argparse.ArgumentParser(description="Batch-run Bakta for all FASTA files (prefix before first underscore).")
    p.add_argument("-i", "--input-dir", required=True, type=Path, help="Directory with FASTA files.")
    p.add_argument("-d", "--db", required=True, type=Path, help="Path to Bakta database.")
    p.add_argument("-o", "--output-dir", type=Path, default=None,
                   help="Optional base output directory (default: next to each FASTA).")
    p.add_argument("-t", "--threads", type=int, default=max(1, (os.cpu_count() or 2) - 1),
                   help="Threads for Bakta (default: CPUs minus one).")
    p.add_argument("--ext", nargs="+", default=[".fasta", ".fa", ".fna"],
                   help="FASTA extensions (default: .fasta .fa .fna).")
    p.add_argument("--overwrite", action="store_true", help="Force overwriting existing _bakta folders (adds --force).")
    p.add_argument("--dry-run", action="store_true", help="Show commands without running.")
    return p.parse_args()

def derive_prefix(stem: str) -> str:
    """Everything before the first underscore."""
    return stem.split("_", 1)[0] if "_" in stem else stem

def find_fastas(indir: Path, exts):
    files = []
    for ext in exts:
        files.extend(indir.glob(f"*{ext}"))
    return sorted(set(files))

def run_bakta(fasta: Path, db: Path, outdir: Path, threads: int, overwrite: bool, dry_run: bool) -> int:
    """Run Bakta on one FASTA file."""
    cmd = [
        "bakta",
        "--db", str(db),
        "--threads", str(threads),
        "--output", str(outdir),
    ]
    if overwrite:
        cmd.append("--force")
    cmd.append(str(fasta))

    print(f"\n🔹 Running Bakta on {fasta.name}")
    print(f"   Output : {outdir}")
    print(f"   Threads: {threads}")
    print(f"   Cmd    : {' '.join(cmd)}")

    if dry_run:
        return 0

    # Make sure old folders are gone if overwriting
    if overwrite and outdir.exists():
        shutil.rmtree(outdir, ignore_errors=True)

    # Run Bakta and capture output
    tmp_log = Path(tempfile.gettempdir()) / f"{fasta.stem}_bakta.log"
    with tmp_log.open("w", encoding="utf-8") as logf:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in proc.stdout:
            print(line, end="")
            logf.write(line)
        rc = proc.wait()

    if rc == 0:
        outdir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(tmp_log), outdir / "bakta.log")
    else:
        print(f"❌ Bakta failed for {fasta.name} (exit code {rc})")
        print(f"   Log saved at {tmp_log}")
    return rc

def main():
    args = parse_args()
    if shutil.which("bakta") is None:
        sys.exit("ERROR: Bakta not found in PATH. Activate your environment first.")

    input_dir = args.input_dir.resolve()
    db = args.db.resolve()
    base_out = args.output_dir.resolve() if args.output_dir else None

    fastas = find_fastas(input_dir, args.ext)
    if not fastas:
        sys.exit(f"No FASTA files with extensions {args.ext} found in {input_dir}")

    print(f"Found {len(fastas)} FASTA files.")
    successes = skips = failures = 0

    for fasta in fastas:
        prefix = derive_prefix(fasta.stem)
        outdir = (base_out if base_out else fasta.parent) / f"{prefix}_bakta"

        if outdir.exists() and not args.overwrite:
            print(f"⚠️  Skipping {fasta.name}: {outdir} already exists (use --overwrite to replace)")
            skips += 1
            continue

        rc = run_bakta(fasta, db, outdir, args.threads, args.overwrite, args.dry_run)
        if rc == 0:
            successes += 1
        else:
            failures += 1

    print("\nSummary:")
    print(f"  ✅ Successful: {successes}")
    print(f"  ⚠️ Skipped   : {skips}")
    print(f"  ❌ Failed    : {failures}")

if __name__ == "__main__":
    main()

