"""Render Excalidraw files to PNG with the official Excalidraw library in headless Chrome.

    python -m exdraw.render drawing.excalidraw.md [more files...] [-o OUTDIR] [--light]

Needs: Chrome/Chromium, Node >= 22 and internet access (Excalidraw is loaded from esm.sh).
Used to *verify* generated drawings: look at the PNG, fix overlaps, regenerate.
"""
import argparse
import functools
import http.server
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

EXCALIDRAW_VERSION = "0.18.0"
PAGE = """<!doctype html><html><body style="margin:0;background:%(bg)s">
<script type="module">
try {
  const { exportToSvg } = await import("https://esm.sh/@excalidraw/excalidraw@%(ver)s?bundle");
  const payload = await (await fetch("./scene.json")).json();
  let scene = payload;
  if (payload.compressed) {
    const { default: LZString } = await import("https://esm.sh/lz-string@1.5.0");
    scene = JSON.parse(LZString.decompressFromBase64(payload.compressed));
  }
  const svg = await exportToSvg({
    elements: scene.elements,
    appState: { ...scene.appState, exportWithDarkMode: %(dark)s, exportBackground: true },
    files: scene.files || {},
  });
  document.body.appendChild(svg);
  document.title = "DONE";
} catch (e) {
  document.title = "ERR " + (e && e.message ? e.message : e);
}
</script></body></html>"""
CHROMES = ("google-chrome-stable", "google-chrome", "chromium", "chromium-browser")
CAPTURE = Path(__file__).with_name("capture.mjs")


def load_scene(path):
    """Return the scene dict, or {"compressed": str} for plugin-compressed Obsidian files."""
    text = Path(path).read_text(encoding="utf-8")
    if not path.name.endswith(".md"):
        return json.loads(text)
    match = re.search(r"```json\n(.*?)\n```", text, re.S)
    if match:
        return json.loads(match.group(1))
    match = re.search(r"```compressed-json\n(.*?)\n```", text, re.S)
    if match:
        return {"compressed": re.sub(r"\s+", "", match.group(1))}
    raise ValueError(f"{path}: no Excalidraw drawing block found")


def scene_size(scene):
    """Viewport big enough for the drawing (unknown for compressed scenes)."""
    elements = [e for e in scene.get("elements", []) if not e.get("isDeleted")]
    if not elements:
        return 1400, 2400
    right = max(e["x"] + max(e["width"], 0) for e in elements)
    bottom = max(e["y"] + max(e["height"], 0) for e in elements)
    left = min(e["x"] for e in elements)
    top = min(e["y"] for e in elements)
    return int(right - left + 120), int(bottom - top + 120)


def find_chrome():
    for name in ([os.environ["CHROME"]] if os.environ.get("CHROME") else []) + list(CHROMES):
        path = shutil.which(name)
        if path:
            return path
    sys.exit("Chrome/Chromium not found (set CHROME=/path/to/chrome)")


def render(path, outdir, dark=True, chrome=None):
    path = Path(path)
    scene = load_scene(path)
    width, height = scene_size(scene)
    bg = "#121212" if dark else "#ffffff"
    stem = path.name.removesuffix(".md").removesuffix(".excalidraw").removesuffix(".json")
    out = Path(outdir) / f"{stem}.png"
    with tempfile.TemporaryDirectory() as tmp:
        Path(tmp, "scene.json").write_text(json.dumps(scene, ensure_ascii=False), encoding="utf-8")
        Path(tmp, "index.html").write_text(
            PAGE % {"bg": bg, "ver": EXCALIDRAW_VERSION, "dark": "true" if dark else "false"}, encoding="utf-8")
        handler = functools.partial(QuietHandler, directory=tmp)
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            result = subprocess.run(
                ["node", str(CAPTURE), chrome or find_chrome(),
                 f"http://127.0.0.1:{server.server_port}/index.html", str(out.resolve()),
                 str(width), str(height), "90000"],
                capture_output=True, text=True, timeout=120, check=False)
        finally:
            server.shutdown()
    if result.returncode != 0 or not out.exists():
        raise RuntimeError(f"render failed for {path}: {result.stderr.strip()}")
    return out


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("-o", "--outdir", type=Path, default=Path("."))
    parser.add_argument("--light", action="store_true", help="render in light theme")
    args = parser.parse_args(argv)
    args.outdir.mkdir(parents=True, exist_ok=True)
    chrome = find_chrome()
    for file in args.files:
        print(render(file, args.outdir, dark=not args.light, chrome=chrome))


if __name__ == "__main__":
    main()
