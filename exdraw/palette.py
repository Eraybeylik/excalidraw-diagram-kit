"""Color palette.

Colors are Excalidraw *light-theme* values. Scenes are saved with theme="dark"; Excalidraw
inverts them on screen, which yields the muted-on-dark look. Pick colors by meaning, not taste:
the same color must mean the same thing in every diagram (see SKILL.md, "Color semantics").
"""
from typing import NamedTuple


class Color(NamedTuple):
    stroke: str
    fill: str


TEXT = "#1e1e1e"
MUTED = "#6b7280"
LINE = "#ced4da"
BG = "#ffffff"

BLUE = Color("#1971c2", "#d0ebff")
PURPLE = Color("#6741d9", "#e5dbff")
GREEN = Color("#2f9e44", "#d3f9d8")
ORANGE = Color("#e8590c", "#ffe8cc")
RED = Color("#e03131", "#ffe3e3")
TEAL = Color("#0c8599", "#c5f6fa")
YELLOW = Color("#b08900", "#fff3bf")
GRAY = Color("#868e96", "#f1f3f5")
NEUTRAL = Color("#adb5bd", "#f8f9fa")

# Softer fills for large containers (zones, groups, boundaries) so nested boxes stay readable.
SOFT = {
    BLUE: "#e7f5ff", PURPLE: "#f3f0ff", GREEN: "#ebfbee", ORANGE: "#fff4e6",
    RED: "#fff5f5", TEAL: "#e3fafc", YELLOW: "#fff9db", GRAY: "#f8f9fa", NEUTRAL: "#f8f9fa",
}
