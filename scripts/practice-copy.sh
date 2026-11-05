#!/usr/bin/env bash
# Make a fresh participant copy of this workshop folder for a rehearsal or the slide 8 demo.
# Usage: bash scripts/practice-copy.sh [DEST]   (default: $TMPDIR/agentic-workshop-practice)
# An existing DEST is renamed with a timestamp, never deleted, so earlier practice work is kept.
set -euo pipefail
src=$(cd "${BASH_SOURCE[0]%/*}/.." && pwd)
dest=${1:-${TMPDIR:-/tmp}/agentic-workshop-practice}
dest=${dest%/}
case "$dest/" in "$src"/*) echo "FAIL $dest is inside the workshop folder; choose a folder outside it" >&2; exit 2;; esac

if [ -e "$dest" ]; then
  old="$dest-$(date +%Y%m%d-%H%M%S)"
  mv "$dest" "$old"
  echo "Kept the previous copy at $old"
fi
mkdir -p "$dest"
tar -C "$src" --exclude=./.git --exclude=./deliverables --exclude=./runs --exclude=__pycache__ \
  --exclude=.DS_Store --exclude=settings.local.json -cf - . | tar -C "$dest" -xf -

echo "Fresh copy: $dest"
echo "Next:"
echo "  cd \"$dest\""
echo "  bash lab/00-check.sh"
echo "  bash lab/01-reproduce.sh"
