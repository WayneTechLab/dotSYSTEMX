#!/usr/bin/env python3
"""Verify current media hashes, SVG safety, labels, and optional 8K exports.

Usage: python3 -I -B docs/media/verify_current_visuals.py
       [--raster-dir /path/to/8k-exports]
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / ".SYSTEMX" / "MEDIA" / "Reference" / "ASSETS.json"
BACKGROUND = "#061D31"
FORBIDDEN = {"script", "foreignObject", "iframe", "object", "animate", "set"}


def check_file(path: Path, recorded: dict) -> None:
    data = path.read_bytes()
    if len(data) != recorded["bytes"] or hashlib.sha256(data).hexdigest() != recorded["sha256"]:
        raise ValueError("Exact-byte asset mismatch: " + str(path))


def luminance(value: str) -> float:
    if len(value) != 7 or value[0] != "#":
        raise ValueError("Overlay text must use a six-digit color")
    channels = [int(value[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
              for c in channels]
    return sum(a * b for a, b in zip(linear, (0.2126, 0.7152, 0.0722)))


def contrast(a: str, b: str) -> float:
    light, dark = sorted((luminance(a), luminance(b)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def verify_svg(path: Path, item: dict) -> float:
    root = ET.parse(path).getroot()
    if (root.attrib.get("width"), root.attrib.get("height"), root.attrib.get("role")) != (
            "7680", "4320", "img") or not root.attrib.get("aria-labelledby"):
        raise ValueError("SVG size or accessible root metadata mismatch: " + path.name)
    elements = list(root.iter())
    names = [element.tag.rsplit("}", 1)[-1] for element in elements]
    if any(name in FORBIDDEN for name in names) or any(names.count(name) != 1 for name in
                                                 ("title", "desc", "image")):
        raise ValueError("SVG contains an unsafe or missing semantic element: " + path.name)
    bands = [(element.attrib.get("y"), element.attrib.get("height"))
             for element in elements if element.tag.endswith("rect") and
             element.attrib.get("fill") == BACKGROUND and
             "fill-opacity" not in element.attrib]
    detail = item.get("kind") == "agent-detail"
    if detail:
        if not any(element.tag.endswith("rect") and element.attrib.get("width") == "1600" and
                   element.attrib.get("height") == "900" and element.attrib.get("fill") == BACKGROUND
                   for element in elements):
            raise ValueError("Opaque detailed-sheet canvas missing: " + path.name)
        if sum(element.tag.endswith("rect") and element.attrib.get("fill") == "#09263D"
               for element in elements) < 5:
            raise ValueError("Detailed-sheet text panels missing: " + path.name)
    elif ("0", "162") not in bands or ("754", "187") not in bands:
        raise ValueError("Opaque title/caption bands missing: " + path.name)
    observed = []
    for element in elements:
        for key, value in element.attrib.items():
            name = key.rsplit("}", 1)[-1]
            if name.lower().startswith("on"):
                raise ValueError("SVG event handler found: " + path.name)
            if name == "href":
                if not value.startswith("data:image/jpeg;base64,"):
                    raise ValueError("SVG image must be an embedded JPEG: " + path.name)
                data = base64.b64decode(value.split(",", 1)[1], validate=True)
                if not data.startswith(b"\xff\xd8") or not data.endswith(b"\xff\xd9"):
                    raise ValueError("Embedded JPEG is incomplete: " + path.name)
                if hashlib.sha256(data).hexdigest() != item["embeddedBackground"]["sha256"]:
                    raise ValueError("Embedded JPEG checksum mismatch: " + path.name)
        if element.tag.endswith("text"):
            backgrounds = (BACKGROUND, "#09263D", "#103A57") if detail else (BACKGROUND,)
            observed.extend(contrast(element.attrib["fill"], background) for background in backgrounds)
    if not observed or min(observed) < 4.5:
        raise ValueError("Overlay text contrast below WCAG AA normal-text ratio: " + path.name)
    return min(observed)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raster-dir", type=Path,
                        help="optional directory containing separate 8K JPEG release exports")
    args = parser.parse_args()
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    if index.get("schemaVersion") != 3 or len(index.get("assets", [])) != 22:
        raise ValueError("Expected the 4+11+7 current asset inventory")
    ids = set()
    minimum = float("inf")
    for item in index["assets"]:
        asset_id = item["id"]
        if asset_id in ids:
            raise ValueError("Duplicate visual ID: " + asset_id)
        ids.add(asset_id)
        file = item["export"]["file"]
        name = Path(file).name
        allowed = {asset_id + ".svg", asset_id + "-4k.jpg"}
        if not file.startswith("../Infographics/") or name not in allowed:
            raise ValueError("Asset file is outside the current infographic inventory")
        path = (INDEX.parent / file).resolve()
        if path.parent != ROOT / ".SYSTEMX" / "MEDIA" / "Infographics":
            raise ValueError("Asset path escaped the infographic directory")
        check_file(path, item["export"])
        if path.suffix == ".svg":
            minimum = min(minimum, verify_svg(path, item))
            if args.raster_dir:
                raster = args.raster_dir / item["rasterExport"]["fileName"]
                check_file(raster, item["rasterExport"])
    print(f"Verified {len(ids)} current assets; 18 SVGs; minimum overlay contrast {minimum:.2f}:1")
    if args.raster_dir:
        print("Verified 18 separate 8K raster export hashes")


if __name__ == "__main__":
    main()
