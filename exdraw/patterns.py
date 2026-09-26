"""Reusable layouts on top of Scene primitives."""
from . import palette as P
from .fonts import measure, wrap


def flow(scene, x, y, nodes, labels=(), direction="right", w=180, h=90, gap=60, arrow_color=P.MUTED):
    """Chain of boxes joined by labeled arrows.

    nodes:  [(title, [detail lines], Color), ...]
    labels: arrow labels between consecutive nodes ("" for none).
    Returns the list of node rectangles as (x, y, w, h).
    """
    if direction == "right" and labels:
        gap = max(gap, max(measure(label, 12) for label in labels) + 24)
    rects = []
    for i, (title, lines, color) in enumerate(nodes):
        nx, ny = (x + i * (w + gap), y) if direction == "right" else (x, y + i * (h + gap))
        scene.box(nx, ny, w, h, color, title, lines)
        rects.append((nx, ny, w, h))
    for i in range(len(rects) - 1):
        (ax, ay, _, _), (bx, by, _, _) = rects[i], rects[i + 1]
        label = labels[i] if i < len(labels) else ""
        if direction == "right":
            pts = [(ax + w + 3, ay + h / 2), (bx - 3, by + h / 2)]
            scene.arrow(pts, arrow_color, width=1.8)
            if label:
                scene.text((pts[0][0] + pts[1][0]) / 2, ay + h / 2 - 9, label, 12, P.MUTED, align="center")
        else:
            pts = [(ax + w / 2, ay + h + 3), (bx + w / 2, by - 3)]
            scene.arrow(pts, arrow_color, width=1.8)
            if label:
                scene.text(ax + w / 2 + 12, (pts[0][1] + pts[1][1]) / 2 + 4, label, 12, P.MUTED)
    return rects


class Sequence:
    """Sequence diagram: participants as lanes, messages as horizontal arrows.

    seq = Sequence(scene, [("alice", "user", P.GREEN), ("WS01", "LSASS", P.BLUE)], x=130, spacing=300, top=100)
    seq.message(0, 1, "password", step=1)
    seq.reply(1, 0, "desktop")
    seq.finish(bottom_y)
    """

    def __init__(self, scene, lanes, x=130, spacing=300, top=100, lane_w=200):
        self.scene, self.lanes, self.xs = scene, lanes, [x + i * spacing for i in range(len(lanes))]
        self.top, self.lane_w = top, lane_w
        for lx, (name, sub, color) in zip(self.xs, lanes):
            scene.rect(lx - lane_w / 2, top, lane_w, 58, color)
            scene.text(lx, top + 26, name, 17, align="center")
            scene.text(lx, top + 47, sub, 13, P.MUTED, align="center")

    def message(self, a, b, text, y, step=None, reply=False):
        s, x1, x2 = self.scene, self.xs[a], self.xs[b]
        off = 8 if x2 > x1 else -8
        s.arrow([(x1 + off, y), (x2 - off, y)], P.MUTED if reply else P.TEXT, dashed=reply, width=1.8)
        if step is None:
            s.text((x1 + x2) / 2, y - 10, text, 13, P.MUTED, align="center")
        else:
            nx = max((x1 + x2) / 2 - measure(text, 14) / 2 - 16, min(x1, x2) + 26)
            s.number(nx, y - 16, step, r=10)
            s.text(nx + 16, y - 11, text, 14)

    def reply(self, a, b, text, y):
        self.message(a, b, text, y, reply=True)

    def event(self, lane, y, text, color=P.RED, dx=10):
        """Tag right of a lane (e.g. the log event a step produces). Use dx=110 beside a note()."""
        self.scene.chip(self.xs[lane] + dx, y, text, color, h=26, size=13)

    def note(self, lane, y, lines, step=None, color=P.BLUE):
        """Box on a lane (self-action)."""
        s, cx = self.scene, self.xs[lane]
        h = 20 + 18 * len(lines)
        s.rect(cx - 100, y, 200, h, color)
        if step is not None:
            s.number(cx - 84, y + h / 2, step, color, r=10)
        for i, line in enumerate(lines):
            s.text(cx + 10, y + 22 + i * 18, line, 14, align="center")
        return y + h

    def finish(self, bottom):
        for lx, (_, _, color) in zip(self.xs, self.lanes):
            self.scene.line([(lx, self.top + 58), (lx, bottom)], color.stroke, dashed=True, opacity=0.6)


def callout(scene, x, y, w, title, body, color=P.YELLOW, size=14, mono=False):
    """Titled box with wrapped body text (string or list of paragraphs). Returns bottom y."""
    paragraphs = [body] if isinstance(body, str) else list(body)
    lines = [line for p in paragraphs for line in (wrap(p, size, w - 40, mono) or [""])]
    h = 50 + len(lines) * size * 1.5 + 10
    scene.rect(x, y, w, h, color, soft=True)
    scene.text(x + 20, y + 30, title, 16, color.stroke)
    for i, line in enumerate(lines):
        scene.text(x + 20, y + 58 + i * size * 1.5, line, size, mono=mono)
    return y + h


def steps(scene, x, y, w, items, color=P.BLUE, size=14, gap=12):
    """Numbered step list (derivations, procedures). items: [str | (text, [mono formula lines])].

    Each step is a row: number bubble, wrapped text, optional monospace formula lines.
    Returns bottom y.
    """
    for i, item in enumerate(items, 1):
        text, formulas = (item, []) if isinstance(item, str) else item
        lines = wrap(text, size, w - 56)
        h = 16 + len(lines) * size * 1.45 + len(formulas) * 22 + (6 if formulas else 0)
        scene.rect(x, y, w, h, P.NEUTRAL, soft=True)
        scene.number(x + 22, y + 22, i, color, r=11)
        for j, line in enumerate(lines):
            scene.text(x + 44, y + 27 + j * size * 1.45, line, size)
        fy = y + 27 + len(lines) * size * 1.45 + 4
        for j, formula in enumerate(formulas):
            scene.text(x + 56, fy + j * 22, formula, 14, P.TEXT, mono=True)
        y += h + gap
    return y
