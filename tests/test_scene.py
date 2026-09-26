import json
import re

import pytest

from exdraw import BLUE, GREEN, MUTED, Scene, Sequence, callout, flow, measure, steps
from exdraw.render import load_scene, scene_size

REQUIRED = {"id", "type", "x", "y", "width", "height", "strokeColor", "backgroundColor", "seed", "version"}


def sample():
    s = Scene("Title", "Subtitle", seed=1)
    s.rect(10, 10, 100, 50, BLUE)
    s.chip(10, 80, "chip", GREEN)
    s.arrow([(0, 0), (50, 50)], MUTED, label="flows")
    flow(s, 10, 200, [("A", ["a"], BLUE), ("B", [], GREEN)], ["to"])
    seq = Sequence(s, [("x", "sub", BLUE), ("y", "sub", GREEN)], top=400)
    seq.message(0, 1, "hello", 500, step=1)
    seq.finish(560)
    callout(s, 10, 600, 300, "Note", "some wrapped body text " * 5)
    steps(s, 10, 800, 400, ["first", ("second", ["x = 1"])])
    s.legend(10, 1000, [("box", BLUE, "one"), ("arrow", MUTED, "two"), ("chip", GREEN, "three")])
    return s


def test_elements_have_required_fields_and_unique_ids():
    elements = sample().elements
    assert all(REQUIRED <= e.keys() for e in elements)
    ids = [e["id"] for e in elements]
    assert len(ids) == len(set(ids))


def test_same_seed_is_deterministic():
    assert sample().to_dict() == sample().to_dict()


def test_obsidian_markdown_roundtrip(tmp_path):
    s = sample()
    path = s.save(tmp_path / "d.excalidraw.md")
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n\nexcalidraw-plugin: parsed")
    assert text.count(" ^") >= len(s.texts)
    scene = load_scene(path)
    assert len(scene["elements"]) == len(s.elements)


def test_plain_excalidraw_roundtrip(tmp_path):
    path = sample().save(tmp_path / "d.excalidraw")
    assert json.loads(path.read_text())["type"] == "excalidraw"
    assert load_scene(path)["appState"]["theme"] == "dark"


def test_compressed_obsidian_file_is_passed_through(tmp_path):
    path = tmp_path / "c.excalidraw.md"
    path.write_text("# Excalidraw Data\n%%\n## Drawing\n```compressed-json\nAB\nCD\n```\n%%", encoding="utf-8")
    assert load_scene(path) == {"compressed": "ABCD"}


def test_rejects_unknown_extension(tmp_path):
    with pytest.raises(ValueError):
        sample().save(tmp_path / "d.svg")


def test_text_y_is_baseline():
    s = Scene()
    s.text(0, 100, "x", 20)
    element = s.elements[0]
    assert element["y"] < 100 < element["y"] + element["height"]


def test_measure_grows_with_text_and_size():
    assert measure("abcdef", 14) > measure("abc", 14) > 0
    assert measure("abc", 20) > measure("abc", 14)


def test_scene_size_covers_all_elements():
    width, height = scene_size(sample().to_dict())
    assert width > 400 and height > 1000


def test_legend_wraps_to_new_row():
    s = Scene()
    bottom = s.legend(0, 0, [("box", BLUE, "a long legend label " * 3)] * 4, max_width=400)
    assert bottom > 40
    assert len({round(e["y"]) for e in s.elements if e["type"] == "rectangle"}) > 1


def test_ids_are_obsidian_block_ref_safe():
    assert all(re.fullmatch(r"[A-Za-z0-9]{8}", e["id"]) for e in sample().elements)
