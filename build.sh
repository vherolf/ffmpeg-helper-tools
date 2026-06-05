#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SCRIPT_DIR/venv"
PYINSTALLER="$VENV/bin/pyinstaller"

if [ ! -f "$PYINSTALLER" ]; then
    echo "pyinstaller not found — run install.sh first"
    exit 1
fi

SCRIPTS=(
    analyzer.py
    compressor.py
    resizer.py
    renamer.py
    mosaic.py
    mosaic-left-right.py
    videoslicer-horizontal.py
    videoslicer-vertical.py
    generate-test-media.py
)

cd "$SCRIPT_DIR"

for script in "${SCRIPTS[@]}"; do
    name="${script%.py}"
    echo "Building $name ..."
    "$PYINSTALLER" --onefile --name "$name" "$script" \
        --distpath "$SCRIPT_DIR/dist" \
        --workpath "$SCRIPT_DIR/build" \
        --specpath "$SCRIPT_DIR/build" \
        --noconfirm --clean -q
    echo "  -> dist/$name"
done

echo ""
echo "Done. Binaries are in: $SCRIPT_DIR/dist/"
