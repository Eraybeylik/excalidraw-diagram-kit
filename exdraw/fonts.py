"""Text width estimation.

Excalidraw needs a width for every text element, and our layouts size boxes around text.
We measure with a real system font via Pillow and scale to Excalifont's wider glyphs.
"""
import shutil
import subprocess
from functools import lru_cache

from PIL import ImageFont

HAND_SCALE = 1.12  # Excalifont is ~12% wider than Noto Sans
FALLBACK_EM = {False: 0.55, True: 0.6}


def _fc_match(pattern):
    if not shutil.which("fc-match"):
        return None
    out = subprocess.run(["fc-match", "-f", "%{file}", pattern], capture_output=True, text=True)
    return out.stdout.strip() or None


@lru_cache(maxsize=None)
def _font(size, mono):
    for pattern in (("Noto Sans Mono", "monospace") if mono else ("Noto Sans", "sans-serif")):
        path = _fc_match(pattern)
        if path:
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return None


def measure(text, size, mono=False):
    """Estimated rendered width in px of `text` at `size` (Excalifont, or Cascadia if mono)."""
    font = _font(size, mono)
    width = font.getlength(text) if font else len(text) * size * FALLBACK_EM[mono]
    return width * (1.0 if mono else HAND_SCALE)


def wrap(text, size, max_width, mono=False):
    lines, current = [], ""
    for word in text.split(" "):
        candidate = f"{current} {word}".strip()
        if measure(candidate, size, mono) <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    return lines + ([current] if current else [])
