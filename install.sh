#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/vherolf/ffmpeg-helper-tools.git"
INSTALL_DIR="${HOME}/.local/share/ffmpeg-helper-tools"

# ── colours ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
ok()   { echo -e "${GREEN}[ok]${NC}  $*"; }
warn() { echo -e "${YELLOW}[warn]${NC} $*"; }
fail() { echo -e "${RED}[fail]${NC} $*"; exit 1; }

# ── system dependency checks ──────────────────────────────────────────────────
echo "Checking system dependencies..."

check_cmd() {
    if command -v "$1" &>/dev/null; then
        ok "$1 found ($(command -v "$1"))"
    else
        fail "$1 not found — install it and re-run.  Hint: $2"
    fi
}

check_cmd git    "sudo apt install git  /  brew install git"
check_cmd python3 "sudo apt install python3  /  brew install python3"
check_cmd pip3    "sudo apt install python3-pip  /  brew install python3"
check_cmd ffmpeg  "sudo apt install ffmpeg  /  brew install ffmpeg"
check_cmd ffprobe "ffprobe is part of ffmpeg — reinstall ffmpeg"

echo ""

# ── clone or update ───────────────────────────────────────────────────────────
if [ -d "$INSTALL_DIR/.git" ]; then
    echo "Updating existing installation in $INSTALL_DIR ..."
    git -C "$INSTALL_DIR" pull --ff-only
    ok "repo updated"
else
    echo "Installing to $INSTALL_DIR ..."
    git clone "$REPO_URL" "$INSTALL_DIR"
    ok "repo cloned"
fi

echo ""

# ── virtual environment ───────────────────────────────────────────────────────
VENV_DIR="$INSTALL_DIR/venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    ok "venv created"
else
    ok "venv already exists"
fi

# ── pip packages ──────────────────────────────────────────────────────────────
echo "Installing/updating pip packages..."
"$VENV_DIR/bin/pip" install --upgrade pip -q
"$VENV_DIR/bin/pip" install -r "$INSTALL_DIR/requirements.txt"
ok "pip packages installed"

echo ""
echo -e "${GREEN}Done!${NC} Scripts are in: $INSTALL_DIR"
echo ""
echo "Run a script:"
echo "  $VENV_DIR/bin/python $INSTALL_DIR/compressor.py --help"
echo ""
echo "To update later, just re-run the same install command."
