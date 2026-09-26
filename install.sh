#!/usr/bin/env bash
# Link the Claude Code skill and check runtime requirements.
set -euo pipefail

KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
TARGET="$SKILLS_DIR/excalidraw-diagrams"

mkdir -p "$SKILLS_DIR"
if [ -e "$TARGET" ] && [ ! -L "$TARGET" ]; then
  echo "error: $TARGET exists and is not a symlink; move it away first" >&2
  exit 1
fi
ln -sfn "$KIT/skills/excalidraw-diagrams" "$TARGET"
echo "skill linked: $TARGET -> $KIT/skills/excalidraw-diagrams"

missing=0
python3 -c "import PIL" 2>/dev/null || { echo "missing: Pillow (pip install pillow / pacman -S python-pillow)"; missing=1; }
node -e "if (typeof WebSocket !== 'function') process.exit(1)" 2>/dev/null \
  || { echo "missing: Node >= 22 (needed for rendering)"; missing=1; }
command -v google-chrome-stable >/dev/null || command -v google-chrome >/dev/null \
  || command -v chromium >/dev/null || [ -n "${CHROME:-}" ] \
  || { echo "missing: Chrome/Chromium (or set CHROME=/path/to/chrome)"; missing=1; }
[ "$missing" -eq 0 ] && echo "all requirements found"
