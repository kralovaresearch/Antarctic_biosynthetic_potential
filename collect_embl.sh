#!/bin/bash
# collect_embl.sh
# Collect all .embl files from *_bakta folders into embl_fin

# === SETTINGS ===
SRC_DIR="$(pwd)"                   # directory containing *_bakta folders
DEST_DIR="${SRC_DIR}/embl_fin"     # folder where .embl files will be collected

# === SETUP ===
mkdir -p "$DEST_DIR"

echo "Collecting .embl files from *_bakta folders..."
echo "Source: $SRC_DIR"
echo "Destination: $DEST_DIR"
echo "----------------------------------------"

# === MAIN LOOP ===
for folder in "${SRC_DIR}"/*_bakta; do
    [ -d "$folder" ] || continue  # skip if not a directory

    strain=$(basename "$folder" _bakta)
    embl_file=$(find "$folder" -type f -name "*.embl" | head -n 1)

    if [ -n "$embl_file" ]; then
        cp "$embl_file" "${DEST_DIR}/${strain}.embl"
        echo "✅ Copied ${strain}.embl"
    else
        echo "⚠️  No .embl file found in $folder"
    fi
done

echo "----------------------------------------"
echo "🎉 All .embl files collected in: $DEST_DIR"

