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
    archiver.py
)

cd "$SCRIPT_DIR"

LIBMAGIC=$(ldconfig -p 2>/dev/null | grep 'libmagic\.so' | awk '{print $NF}' | head -1)
if [ -z "$LIBMAGIC" ]; then
    echo "Warning: libmagic not found — archiver.py binary will be built without it bundled (install libmagic1)"
fi

for script in "${SCRIPTS[@]}"; do
    name="${script%.py}"
    echo "Building $name ..."
    extra_args=()
    if [ "$script" = "archiver.py" ] && [ -n "$LIBMAGIC" ]; then
        extra_args+=(--add-binary "$LIBMAGIC:.")
    fi
    PYTHONWARNINGS=ignore::SyntaxWarning \
    "$PYINSTALLER" --onefile --name "$name" "$script" \
        --distpath "$SCRIPT_DIR/dist" \
        --workpath "$SCRIPT_DIR/build" \
        --specpath "$SCRIPT_DIR/build" \
        --exclude-module tkinter \
        --noconfirm --clean --log-level WARN \
        "${extra_args[@]}"
    echo "  -> dist/$name"
done

echo ""
echo "Done. Binaries are in: $SCRIPT_DIR/dist/"
