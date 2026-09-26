---
name: excalidraw-diagrams
description: Draw diagrams as Excalidraw files (Obsidian .excalidraw.md or plain .excalidraw) with the exdraw Python kit, then render and visually verify them. Use whenever the user asks to draw, diagram, sketch, visualize or illustrate something — architecture, network, hierarchy, flow, sequence/protocol, timeline, comparison, or a math/physics problem and its solution ("çiz", "çizim", "diyagram", "görselleştir", "şema", "draw", "diagram", "visualize"), or asks to convert Mermaid/ASCII diagrams to Excalidraw.
---

# Excalidraw diagrams with exdraw

You write a small Python script that builds the drawing from primitives, save it as an Excalidraw
file, render it to PNG with the real Excalidraw library, **look at the PNG**, fix what is wrong,
and repeat until it is clean. Never deliver a drawing you have not looked at.

## Setup (once per session)

```bash
KIT="$(dirname "$(dirname "$(dirname "$(readlink -f ~/.claude/skills/excalidraw-diagrams/SKILL.md)")")")"
export PYTHONPATH="$KIT${PYTHONPATH:+:$PYTHONPATH}"
python3 -c "import exdraw" && echo ok      # needs Pillow
```

Rendering needs Chrome/Chromium, Node >= 22 and internet (Excalidraw loads from esm.sh).
Reference examples live in `$KIT/examples/` — read the closest one before writing a new drawing.

## Workflow

1. **Understand the subject first.** Name the parts, their relationships and what the reader must
   take away. For math/physics: solve it, then verify the answer numerically (quick simulation or
   computation) *before* drawing. Compute geometry from real coordinates, don't eyeball it.
2. **Pick a layout** (see Patterns). One idea per drawing; split if it grows past ~1300px tall.
3. **Write the generator script.** Keep it next to the output so the drawing can be regenerated:
   Obsidian project → `<project folder>/.diagrams/<name>.py` (dot-folders are hidden in Obsidian);
   code repo → `docs/diagrams/<name>.py`.
4. **Save + render + inspect:**
   ```bash
   python3 path/to/script.py                                  # writes the .excalidraw(.md)
   python3 -m exdraw.render OUT.excalidraw.md -o /tmp/preview  # prints the PNG path
   ```
   Read the PNG. Check: text overflowing boxes, labels crossing lines, overlapping shapes, arrows
   pointing at the wrong thing, legend present, nothing off-canvas. Fix coordinates, rerun.
5. **Deliver.** Embed it where it belongs and tell the user where the file and script are.

## Destination

- **Obsidian vault** (a `.obsidian/` dir exists up the tree): save as `<Name>.excalidraw.md` into the
  Excalidraw plugin folder — read `folder` from `.obsidian/plugins/obsidian-excalidraw-plugin/data.json`
  (fallback: vault root). Embed in the note with `![[<Name>.excalidraw]]`.
- **Anywhere else:** save `<name>.excalidraw` (opens on excalidraw.com / VS Code extension) and, if
  the user wants an image, keep the rendered PNG too.
- **Editing an existing drawing:** if the file has a ` ```compressed-json ` block, the user has edited
  it in Excalidraw. Regenerating from the script would erase their edits — ask first.

## Design rules (C4-inspired; these are what make the drawings readable)

- Every drawing has a **title** (what + scope) and usually a one-line subtitle.
- Every drawing has a **legend** (`s.legend(...)`) explaining colors, box styles and line styles.
- **Every arrow has a label** saying what it does ("sends logs · TCP 9997", "inherits", "asks"),
  unless the legend already makes it unambiguous (e.g. a plain pipeline).
- **Meaning never depends on color alone**: also use solid vs dashed, labels, or icons.
- **Colors mean the same thing in every drawing** of a project (table below).
- Group with **containers** (soft-filled boxes) for boundaries: networks, trust zones, OUs, phases.
  Dashed container = logical / planned / not-yet-existing.
- Numbered bubbles for **sequences and derivations**; the reader should be able to follow 1 → n.
- Put the takeaway in a **callout** (result, gotcha, "remember this").
- Text in the user's language; identifiers, commands and formulas stay as they are.

### Color semantics (default; keep consistent per project)

| Color | Use for |
|---|---|
| `PURPLE` | structure / identity / hierarchy (domain, OU, org unit, given figure) |
| `BLUE` | machines, nodes, main actors, given lines |
| `GREEN` | people / users / success / result |
| `ORANGE` | groups, sources, auxiliary constructions |
| `YELLOW` | policy, config, problem statement, notes |
| `TEAL` | services, data pipeline, SIEM, DNS |
| `RED` | privileged, danger, attack, failure, the unknown being solved for |
| `GRAY` | external, inactive, background |

## API cheatsheet (`from exdraw import *`)

Coordinates in px, origin top-left. **Text `y` is the baseline.** Widths come from `measure(text, size)`.

```python
s = Scene("Title", "subtitle")                       # title at y≈46, subtitle y≈76; start content at y≈100
s.text(x, y, "txt", size=15, color=TEXT, mono=False, align="left|center|right")
s.inline(x, y, [("bold-ish", 17, TEXT, False), ("   muted", 13, MUTED, False)])   # runs on one line
s.paragraph(x, y, long_text, size=14, max_width=700)  # wraps, returns next baseline
s.rect(x, y, w, h, BLUE, dashed=False, soft=False)    # soft=True: pale fill for big containers
s.box(x, y, w, h, TEAL, "Title", ["detail", "detail"])   # centered title + muted lines
w = s.chip(x, y, "label", GREEN, stroke=RED.stroke)  # pill sized to text; returns width
s.chips(x, y, [("a", GREEN), ("b", ORANGE, {"stroke": RED.stroke})])
s.arrow([(x1, y1), (x2, y2), ...], TEAL.stroke, dashed=False, label="what it does")
s.line(points, color, dashed=False, width=1.5)
s.polygon(points, PURPLE, fill=PURPLE.fill); s.ellipse(cx, cy, r, color=GRAY); s.dot(x, y)
s.label(cx, cy, "on-arrow text")                     # text with background patch
s.number(cx, cy, 3, BLUE); s.check(cx, cy, done=True)
s.rotated_text(cx, cy, "vertical", degrees=-90)
s.legend(x, y, [("box", BLUE, "machine"), ("dashed-box", RED, "planned"), ("chip", GREEN, "user"),
                ("arrow", TEAL.stroke, "log flow"), ("dashed-arrow", GRAY.stroke, "reply")], title="Legend")
s.save("Name.excalidraw.md")   # or .excalidraw / .json
```

Patterns (`exdraw.patterns`, also exported):

```python
flow(s, x, y, [(title, [lines], COLOR), ...], ["label", ...], direction="right|down", w=180, h=90)
seq = Sequence(s, [("alice", "user", GREEN), ("WS01", "LSASS", BLUE)], x=130, spacing=280, top=100)
seq.message(0, 1, "request", y, step=1); seq.reply(1, 0, "answer", y); seq.event(1, y, "4624")
seq.note(1, y, ["self action"], step=5); seq.event(1, y, "tag", dx=110); seq.finish(bottom_y)
bottom = callout(s, x, y, w, "Title", "text" or ["para", "para"], YELLOW)
bottom = steps(s, x, y, w, ["plain step", ("step with formulas", ["x = 1", "y = 2"])], BLUE)
```

Pick by subject: hierarchy → nested containers + trunk lines (`examples/ad_hierarchy.py`);
protocol / who-talks-to-whom-when → `Sequence` (`kerberos_logon.py`); data or process pipeline →
grouped boxes + `flow` (`siem_data_flow.py`); proofs / problems → figure left, `steps` right,
result `callout` (`math_langley.py`, `math_buffon.py`, `math_circle_triangle.py`).

## Layout tips and gotchas

- Canvas ~860px wide reads well in Obsidian and GitHub; grow downward, not sideways.
- Leave ≥ 20px between siblings and ≥ 16px padding inside containers; labels need room: arrow gaps
  must be wider than their label (`flow` does this automatically).
- Container header text at `y + 27`, first row of children at `y + 40`.
- Formulas: use `mono=True`; Unicode math (∫ √ π θ ≤ ⇔ ² ₀ △ ∠) renders fine.
- Sub/superscripts beyond ₀-₉/²/³: write `2^(n−1)` instead of fancy glyphs.
- The scene is saved with the dark theme: Excalidraw inverts the light palette on screen. Only use
  palette colors (`exdraw.palette`) so contrast stays right in both themes.
- Same `Scene(title=...)` → same random seed → identical output: diffs stay clean on regenerate.
- A white/`BG` shape is invisible on the dark canvas — that is how `label()` masks lines.
