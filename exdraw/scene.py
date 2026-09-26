"""Scene: an Excalidraw drawing built from simple primitives.

Coordinates are pixels, origin top-left, y grows downward. For text, `y` is the *baseline*,
so a 15px label at y=100 sits visually just above 100 — the same convention as SVG.
"""
import json
import math
import random
from pathlib import Path

from . import palette as P
from .fonts import measure, wrap

HAND, MONO_FONT = 5, 3  # Excalidraw fontFamily ids: 5 = Excalifont, 3 = Cascadia (monospace)
SOURCE = "https://github.com/zsviczian/obsidian-excalidraw-plugin"
ID_CHARS = "abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"


class Scene:
    def __init__(self, title=None, subtitle=None, theme="dark", seed=None, roughness=1):
        self.elements, self.texts = [], []
        self.theme, self.roughness = theme, roughness
        self._rng = random.Random(seed if seed is not None else (title or "scene"))
        if title:
            self.text(32, 46, title, 27)
        if subtitle:
            self.text(32, 76, subtitle, 15, P.MUTED)

    # ------------------------------------------------------------------ internals
    def _id(self):
        return "".join(self._rng.choice(ID_CHARS) for _ in range(8))

    def _element(self, kind, x, y, w, h, stroke, fill="transparent", dashed=False, width=1.5,
                 opacity=1.0, rounded=None):
        element = {
            "id": self._id(), "type": kind, "x": x, "y": y, "width": w, "height": h, "angle": 0,
            "strokeColor": stroke, "backgroundColor": fill, "fillStyle": "solid", "strokeWidth": width,
            "strokeStyle": "dashed" if dashed else "solid", "roughness": self.roughness,
            "opacity": round(opacity * 100), "groupIds": [], "frameId": None, "roundness": rounded,
            "seed": self._rng.randint(1, 2**31 - 1), "version": 1,
            "versionNonce": self._rng.randint(1, 2**31 - 1), "isDeleted": False,
            "boundElements": None, "updated": 1, "link": None, "locked": False,
        }
        self.elements.append(element)
        return element

    def _points(self, kind, points, color, dashed, width, opacity, start=None, end=None, closed=False,
                fill="transparent"):
        x0, y0 = points[0]
        rel = [[px - x0, py - y0] for px, py in points]
        if closed:
            rel.append([0, 0])
        xs, ys = [p[0] for p in rel], [p[1] for p in rel]
        element = self._element(kind, x0, y0, max(xs) - min(xs), max(ys) - min(ys), color, fill, dashed,
                                width, opacity, {"type": 2} if len(points) == 2 else None)
        element.update({"points": rel, "lastCommittedPoint": None, "startBinding": None,
                        "endBinding": None, "startArrowhead": start, "endArrowhead": end, "elbowed": False})
        if kind == "line":
            element["polygon"] = closed
        return element

    # ------------------------------------------------------------------ text
    def text(self, x, y, s, size=15, color=P.TEXT, mono=False, align="left", angle=0.0):
        """Single-line text. `y` is the baseline. `align`: left | center | right (relative to x)."""
        w = measure(s, size, mono)
        left = {"left": x, "center": x - w / 2, "right": x - w}[align]
        element = self._element("text", left, y - size * 1.02, w, size * 1.25, color)
        element.update({"text": s, "originalText": s, "fontSize": size,
                        "fontFamily": MONO_FONT if mono else HAND, "textAlign": align,
                        "verticalAlign": "top", "containerId": None, "autoResize": True,
                        "lineHeight": 1.25, "angle": angle})
        self.texts.append((s, element["id"]))
        return w

    def rotated_text(self, cx, cy, s, size=13, color=P.TEXT, degrees=-90):
        """Text rotated around its own center (cx, cy), e.g. a vertical label beside a bracket."""
        self.text(cx, cy + size * 0.4, s, size, color, align="center", angle=math.radians(degrees))

    def inline(self, x, y, segments):
        """Consecutive text runs on one baseline: [(text, size, color, mono), ...]. Returns end x."""
        for s, size, color, mono in segments:
            body = s.lstrip(" ")
            x += measure(" " * (len(s) - len(body)), size, mono)
            x += self.text(x, y, body, size, color, mono)
        return x

    def paragraph(self, x, y, s, size=14, max_width=700, color=P.TEXT, line_height=None, mono=False):
        """Word-wrapped text. Returns the baseline y after the last line."""
        line_height = line_height or size * 1.45
        lines = wrap(s, size, max_width, mono)
        for i, line in enumerate(lines):
            self.text(x, y + i * line_height, line, size, color, mono)
        return y + len(lines) * line_height

    def label(self, cx, cy, s, size=13, color=P.MUTED):
        """Text centered on (cx, cy) with a background patch — for labels sitting on arrows."""
        w = measure(s, size) + 14
        self.rect(cx - w / 2, cy - 11, w, 22, color=None, stroke="transparent", fill=P.BG, rounded=True)
        self.text(cx, cy + 4.5, s, size, color, align="center")

    # ------------------------------------------------------------------ shapes
    def rect(self, x, y, w, h, color=P.NEUTRAL, stroke=None, fill=None, dashed=False, width=1.5,
             rounded=True, soft=False):
        """Rectangle. `color` is a palette Color; `soft=True` uses the lighter container fill."""
        stroke = stroke or (color.stroke if color else P.LINE)
        if fill is None:
            fill = (P.SOFT.get(color, color.fill) if soft else color.fill) if color else P.BG
        return self._element("rectangle", x, y, w, h, stroke, fill, dashed, width,
                             rounded={"type": 3} if rounded else None)

    def box(self, x, y, w, h, color, title, lines=(), size=15, dashed=False, soft=False):
        """Rectangle with a centered title and optional muted detail lines."""
        self.rect(x, y, w, h, color, dashed=dashed, soft=soft)
        block = size + len(lines) * 19
        ty = y + (h - block) / 2 + size
        self.text(x + w / 2, ty, title, size, align="center")
        for i, line in enumerate(lines):
            self.text(x + w / 2, ty + 20 + i * 19, line, 13, P.MUTED, align="center")

    def chip(self, x, y, s, color, h=28, size=14, stroke=None, dashed=False, mono=False):
        """Small pill with a label; width fits the text. Returns the width."""
        w = measure(s, size, mono) + 24
        self.rect(x, y, w, h, color, stroke=stroke, dashed=dashed, width=2 if stroke else 1.4)
        self.text(x + w / 2, y + h / 2 + size * 0.4, s, size, align="center", mono=mono)
        return w

    def chips(self, x, y, items, gap=10, **kw):
        """Row of chips: items are (label, Color) or (label, Color, {chip kwargs}). Returns end x."""
        for item in items:
            extra = item[2] if len(item) > 2 else {}
            x += self.chip(x, y, item[0], item[1], **{**kw, **extra}) + gap
        return x

    def ellipse(self, cx, cy, rx, ry=None, color=P.NEUTRAL, fill="transparent", dashed=False, width=1.5):
        ry = rx if ry is None else ry
        return self._element("ellipse", cx - rx, cy - ry, 2 * rx, 2 * ry, color.stroke, fill, dashed, width)

    def dot(self, x, y, color=P.TEXT, r=4):
        self._element("ellipse", x - r, y - r, 2 * r, 2 * r, color, color, width=1)

    def polygon(self, points, color=P.NEUTRAL, fill="transparent", width=2):
        return self._points("line", points, color.stroke, False, width, 1.0, closed=True, fill=fill)

    def line(self, points, color=P.LINE, dashed=False, width=1.5, opacity=1.0):
        return self._points("line", points, color, dashed, width, opacity)

    def arrow(self, points, color=P.MUTED, dashed=False, width=2, start=False, end=True, opacity=1.0,
              label=None, label_at=0.5):
        """Arrow through `points`. Optional `label` is placed on the segment at fraction `label_at`."""
        self._points("arrow", points, color, dashed, width, opacity,
                     "triangle" if start else None, "triangle" if end else None)
        if label:
            (x1, y1), (x2, y2) = points[0], points[-1]
            self.label(x1 + (x2 - x1) * label_at, y1 + (y2 - y1) * label_at, label)

    def number(self, cx, cy, n, color=P.BLUE, r=12):
        """Filled circle with a number — for numbered steps."""
        self._element("ellipse", cx - r, cy - r, 2 * r, 2 * r, color.stroke, color.stroke)
        self.text(cx, cy + 5, str(n), 14, P.BG, align="center")

    def check(self, cx, cy, done=True, color=P.LINE, r=12):
        """Status circle: green with a tick when done, empty ring otherwise."""
        if done:
            self._element("ellipse", cx - r, cy - r, 2 * r, 2 * r, P.GREEN.stroke, P.GREEN.stroke)
            self._points("line", [(cx - 5.5, cy + 0.5), (cx - 1.5, cy + 4.5), (cx + 6, cy - 4.5)],
                         P.BG, False, 2.5, 1.0)
        else:
            self._element("ellipse", cx - r, cy - r, 2 * r, 2 * r, color, width=2)

    # ------------------------------------------------------------------ legend
    def legend(self, x, y, items, title="Legend", max_width=790):
        """Key explaining the notation. items: (kind, Color|hex, label).

        kind: box | dashed-box | chip | arrow | dashed-arrow
        Returns the y below the legend.
        """
        start = x + measure(title, 14) + 18
        self.text(x, y + 18, title, 14, P.MUTED)
        cx, cy = start, y
        for kind, color, s in items:
            stroke = color.stroke if isinstance(color, P.Color) else color
            if kind == "chip":
                need = measure(s, 13) + 38
            else:
                need = 40 + measure(s, 13) + 22
            if cx + need > x + max_width:
                cx, cy = start, cy + 32
            if kind in ("box", "dashed-box"):
                self.rect(cx, cy + 4, 30, 20, color if isinstance(color, P.Color) else None,
                          stroke=stroke, dashed=kind == "dashed-box")
            elif kind in ("arrow", "dashed-arrow"):
                self.arrow([(cx, cy + 14), (cx + 30, cy + 14)], stroke, dashed=kind == "dashed-arrow", width=1.8)
            if kind == "chip":
                cx += self.chip(cx, cy + 1, s, color, h=26, size=13) + 14
            else:
                self.text(cx + 40, cy + 19, s, 13)
                cx += need
        return cy + 40

    # ------------------------------------------------------------------ output
    def to_dict(self):
        return {
            "type": "excalidraw", "version": 2, "source": SOURCE, "elements": self.elements,
            "appState": {"theme": self.theme, "viewBackgroundColor": P.BG, "currentItemFontFamily": HAND,
                         "gridSize": None},
            "files": {},
        }

    def to_obsidian_md(self):
        """Obsidian Excalidraw plugin format (uncompressed; the plugin compresses on first save)."""
        text_section = "".join(f"{s} ^{element_id}\n\n" for s, element_id in self.texts)
        return (
            "---\n\nexcalidraw-plugin: parsed\ntags: [excalidraw]\n\n---\n"
            "==⚠  Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this document. ⚠==\n\n\n"
            "# Excalidraw Data\n\n## Text Elements\n" + text_section
            + "%%\n## Drawing\n```json\n" + json.dumps(self.to_dict(), ensure_ascii=False, indent=1) + "\n```\n%%"
        )

    def save(self, path):
        """Write by extension: `.excalidraw.md` (Obsidian), `.excalidraw` or `.json` (plain scene)."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.name.endswith(".excalidraw.md"):
            path.write_text(self.to_obsidian_md(), encoding="utf-8")
        elif path.suffix in (".excalidraw", ".json"):
            path.write_text(json.dumps(self.to_dict(), ensure_ascii=False), encoding="utf-8")
        else:
            raise ValueError(f"unsupported extension: {path.name} (use .excalidraw.md, .excalidraw or .json)")
        return path
