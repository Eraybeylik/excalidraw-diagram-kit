"""Build every example to examples/output/*.excalidraw and (with --render) docs/previews/*.png.

    python examples/build_all.py [--render]
"""
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "examples"))

EXAMPLES = ["ad_hierarchy", "kerberos_logon", "siem_data_flow",
            "math_langley", "math_buffon", "math_circle_triangle"]


def main():
    outputs = []
    for name in EXAMPLES:
        path = importlib.import_module(name).build().save(ROOT / "examples" / "output" / f"{name}.excalidraw")
        outputs.append(path)
        print("built", path.relative_to(ROOT))
    if "--render" in sys.argv:
        from exdraw.render import find_chrome, render
        chrome = find_chrome()
        for path in outputs:
            print("rendered", render(path, ROOT / "docs" / "previews", chrome=chrome).relative_to(ROOT))


if __name__ == "__main__":
    main()
