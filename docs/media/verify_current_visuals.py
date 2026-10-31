#!/usr/bin/env python3
"""Verify exact current media inventory, embedded art, SVG safety and contrast.

Usage:
  python3 -I -B docs/media/verify_current_visuals.py
  python3 -I -B docs/media/verify_current_visuals.py \
    --source-dir /private/art --thumbnail-dir /private/art/thumbnails
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import struct
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INDEX = ROOT / ".SYSTEMX" / "MEDIA" / "Reference" / "ASSETS.json"
DEFAULT_IMAGES = ROOT / ".SYSTEMX" / "MEDIA" / "Infographics"
MAX_SVG_BYTES = 1_900_000
EXPECTED = (
    "systemx-map-architecture", "systemx-map-task-cycle",
    "systemx-map-governance", "systemx-map-onboarding",
    "systemx-agent-0", "systemx-agent-x", "systemx-agent-y",
    "systemx-agent-z", "systemx-agent-alpha",
    "systemx-agent-beta", "systemx-agent-1", "systemx-atlas",
)
ALLOWED_TAGS = {
    "svg", "title", "desc", "metadata", "g", "rect", "circle", "path",
    "image", "text",
}
ALLOWED_ATTRIBUTES = {
    "aria-labelledby", "cx", "cy", "d", "data-bg", "fill",
    "font-family", "font-size", "font-weight", "height", "href", "id",
    "preserveAspectRatio", "r", "role", "rx", "stroke",
    "stroke-linecap", "stroke-linejoin", "stroke-opacity", "stroke-width",
    "text-anchor", "transform", "viewBox", "width", "x", "y",
}
VIDEO = {".mp4", ".mov", ".m4v", ".webm", ".mkv", ".avi", ".wmv"}
FIRST_CURRENT_MEDIA_VERSION = "1.11.0-beta.3"


def version_order(value: str) -> tuple[int, int, int, int, int]:
    """Order supported release IDs without treating an art baseline as HEAD."""
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)(?:-(alpha|beta)\.(\d+))?", value)
    if not match:
        raise ValueError("Invalid media or template release version: " + value)
    major, minor, patch, channel, sequence = match.groups()
    return (int(major), int(minor), int(patch),
            {"alpha": 0, "beta": 1, None: 2}[channel], int(sequence or 0))


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def luminance(color: str) -> float:
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", color):
        raise ValueError("SVG overlay color must use a six-digit hexadecimal value")
    channels = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
              for v in channels]
    return sum(a * b for a, b in zip(linear, (0.2126, 0.7152, 0.0722)))


def contrast(foreground: str, background: str) -> float:
    high, low = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (high + 0.05) / (low + 0.05)


def verify_file(path: Path, *, expected_bytes: int, expected_sha: str) -> bytes:
    if not path.is_file() or path.is_symlink():
        raise ValueError("Missing ordinary file: " + str(path))
    data = path.read_bytes()
    if len(data) != expected_bytes or sha(data) != expected_sha:
        raise ValueError("Exact-byte mismatch: " + str(path))
    return data


def image_size(data: bytes, mime: str) -> tuple[int, int]:
    """Read intrinsic dimensions independently of the authoring builder."""
    if mime == "image/png":
        if not data.startswith(b"\x89PNG\r\n\x1a\n") or len(data) < 24:
            raise ValueError("Incomplete embedded PNG")
        return struct.unpack(">II", data[16:24])
    if mime != "image/jpeg" or not data.startswith(b"\xff\xd8") or \
            not data.endswith(b"\xff\xd9"):
        raise ValueError("Incomplete embedded JPEG")
    i = 2
    while i < len(data) - 4:
        if data[i] != 0xff:
            i += 1
            continue
        marker = data[i + 1]
        i += 2
        if marker in (0xd8, 0xd9, 0x01) or 0xd0 <= marker <= 0xd7:
            continue
        length = int.from_bytes(data[i:i + 2], "big")
        if length < 2 or i + length > len(data):
            raise ValueError("Malformed JPEG marker")
        if marker in (0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7,
                      0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf):
            height = int.from_bytes(data[i + 3:i + 5], "big")
            width = int.from_bytes(data[i + 5:i + 7], "big")
            return width, height
        i += length
    raise ValueError("JPEG dimensions not found")


def verify_text(root: ET.Element, name: str) -> float:
    minimum = float("inf")
    count = 0
    for node in root.iter():
        if local(node.tag) != "text":
            continue
        count += 1
        value = "".join(node.itertext()).strip()
        if not value:
            raise ValueError(name + ": empty text element")
        fill = node.attrib.get("fill", "")
        bg = node.attrib.get("data-bg", "")
        ratio = contrast(fill, bg)
        minimum = min(minimum, ratio)
        size = float(node.attrib.get("font-size", "0"))
        if size < 14:
            raise ValueError(name + ": text below 14 viewBox units")
        x = float(node.attrib["x"])
        y = float(node.attrib["y"])
        if not (0 <= x <= 1600 and 0 <= y <= 900):
            raise ValueError(name + ": text origin outside canvas")
        # Conservative advance estimate catches gross clipping without claiming
        # an exact font layout engine. Rendered previews remain a separate gate.
        width = len(value) * size * (0.60 if "monospace" in node.attrib.get(
            "font-family", "") else 0.56)
        anchor = node.attrib.get("text-anchor", "start")
        left = x - width if anchor == "end" else x - width / 2 if anchor == "middle" else x
        right = x if anchor == "end" else x + width / 2 if anchor == "middle" else x + width
        if left < -2 or right > 1602:
            raise ValueError(name + ": estimated text line crosses canvas")
    if count < (20 if name != "systemx-atlas" else 25):
        raise ValueError(name + ": required selectable labels are missing")
    if minimum < 7:
        raise ValueError(name + f": overlay text contrast {minimum:.2f}:1 below 7:1")
    return minimum


def verify_svg(data: bytes, item: dict, names: tuple[str, ...],
               index: dict, svg_bytes: dict[str, bytes],
               source_dir: Path | None, thumbnail_dir: Path | None) -> float:
    name = item["id"]
    if len(data) > MAX_SVG_BYTES:
        raise ValueError(name + ": exceeds compact SVG bound")
    if b"<!DOCTYPE" in data or b"<!ENTITY" in data or b"url(" in data:
        raise ValueError(name + ": external XML/CSS reference")
    root = ET.fromstring(data)
    if (local(root.tag), root.attrib.get("width"), root.attrib.get("height"),
            root.attrib.get("viewBox"), root.attrib.get("role")) != (
            "svg", "7680", "4320", "0 0 1600 900", "img"):
        raise ValueError(name + ": wrong SVG canvas or role")
    if root.attrib.get("aria-labelledby") != name + "-title " + name + "-desc":
        raise ValueError(name + ": missing accessible title/description binding")
    elements = list(root.iter())
    tags = [local(node.tag) for node in elements]
    if any(tag not in ALLOWED_TAGS for tag in tags):
        raise ValueError(name + ": active or unsupported SVG element")
    titles = [node for node in elements if local(node.tag) == "title"]
    descs = [node for node in elements if local(node.tag) == "desc"]
    if len(titles) != 1 or len(descs) != 1:
        raise ValueError(name + ": expected one title and one description")
    if titles[0].attrib.get("id") != name + "-title" or \
            descs[0].attrib.get("id") != name + "-desc" or \
            len("".join(titles[0].itertext()).strip()) < 10 or \
            len("".join(descs[0].itertext()).strip()) < 30:
        raise ValueError(name + ": incomplete accessible metadata")
    for node in elements:
        for key, value in node.attrib.items():
            attr = local(key)
            if attr not in ALLOWED_ATTRIBUTES:
                raise ValueError(name + ": unsupported SVG attribute: " + attr)
            if attr.lower().startswith("on"):
                raise ValueError(name + ": event handler attribute")
            if attr == "href" and not (
                    value.startswith("data:image/jpeg;base64,") or
                    value.startswith("data:image/png;base64,")):
                raise ValueError(name + ": nonembedded image reference")
            if re.search(r"https?://|file://|javascript:", value, re.IGNORECASE):
                raise ValueError(name + ": external reference in attribute")
    images = [node for node in elements if local(node.tag) == "image"]
    is_atlas = name == "systemx-atlas"
    if len(images) != (11 if is_atlas else 1):
        raise ValueError(name + ": wrong embedded image count")
    if is_atlas:
        expected_sources = {panel: sha(svg_bytes[panel]) for panel in names[:-1]}
        if item.get("sources") != expected_sources:
            raise ValueError(name + ": atlas source hashes do not match final panels")
        metadata = [node for node in elements if local(node.tag) == "metadata"]
        if len(metadata) != 1 or json.loads(metadata[0].text or "{}") != {
                "sourcePanels": expected_sources}:
            raise ValueError(name + ": atlas metadata does not lock final panels")
        thumbnails = item.get("thumbnails", {})
        if set(thumbnails) != set(names[:-1]):
            raise ValueError(name + ": atlas thumbnail manifest incomplete")
        for panel, node in zip(names[:-1], images):
            href = next(value for key, value in node.attrib.items() if local(key) == "href")
            if not href.startswith("data:image/jpeg;base64,"):
                raise ValueError(name + ": atlas thumbnails must be JPEG")
            raw = base64.b64decode(href.split(",", 1)[1], validate=True)
            meta = thumbnails[panel]
            if len(raw) != meta["bytes"] or sha(raw) != meta["sha256"] or \
                    not raw.startswith(b"\xff\xd8") or not raw.endswith(b"\xff\xd9"):
                raise ValueError(name + ": thumbnail checksum or format mismatch")
            if image_size(raw, "image/jpeg") != (meta["width"], meta["height"]):
                raise ValueError(name + ": thumbnail dimensions mismatch")
            if thumbnail_dir:
                verify_file(thumbnail_dir / meta["fileName"],
                            expected_bytes=meta["bytes"], expected_sha=meta["sha256"])
    else:
        art = item.get("embeddedArt", {})
        node = images[0]
        href = next(value for key, value in node.attrib.items() if local(key) == "href")
        mime = art.get("mime")
        if not href.startswith("data:" + str(mime) + ";base64,"):
            raise ValueError(name + ": art MIME mismatch")
        raw = base64.b64decode(href.split(",", 1)[1], validate=True)
        if len(raw) != art.get("bytes") or sha(raw) != art.get("sha256"):
            raise ValueError(name + ": embedded art checksum mismatch")
        if mime == "image/jpeg" and not (
                raw.startswith(b"\xff\xd8") and raw.endswith(b"\xff\xd9")):
            raise ValueError(name + ": incomplete embedded JPEG")
        if mime == "image/png" and not raw.startswith(b"\x89PNG\r\n\x1a\n"):
            raise ValueError(name + ": incomplete embedded PNG")
        if image_size(raw, mime) != (art.get("width"), art.get("height")):
            raise ValueError(name + ": embedded art dimensions mismatch")
        if source_dir:
            verify_file(source_dir / art["fileName"],
                        expected_bytes=art["bytes"], expected_sha=art["sha256"])
    return verify_text(root, name)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--infographics-dir", type=Path, default=DEFAULT_IMAGES)
    parser.add_argument("--source-dir", type=Path)
    parser.add_argument("--thumbnail-dir", type=Path)
    args = parser.parse_args()
    index = json.loads(args.index.read_text(encoding="utf-8"))
    if any(marker in args.index.read_text(encoding="utf-8")
           for marker in ("/Volumes/", "/Users/", "file://")):
        raise ValueError("Public asset index contains a private host path")
    if index.get("schemaVersion") != 4 or index.get("product") != ".SYSTEMX":
        raise ValueError("Current media requires schemaVersion 4")
    baseline = index.get("softwareBaseline")
    current = (ROOT / ".SYSTEMX" / "VERSION").read_text(encoding="utf-8").strip()
    if not isinstance(baseline, str) or not (
            version_order(FIRST_CURRENT_MEDIA_VERSION) <= version_order(baseline)
            <= version_order(current)):
        raise ValueError("Media baseline must be between its first publication and the current template")
    assets = index.get("assets", [])
    if tuple(item["id"] for item in assets) != EXPECTED:
        raise ValueError("Expected four maps, seven agents and one atlas in fixed order")
    expected_files = {name + ".svg" for name in EXPECTED}
    actual = {path.name for path in args.infographics_dir.iterdir() if path.is_file()}
    if actual != expected_files:
        missing, extra = sorted(expected_files - actual), sorted(actual - expected_files)
        raise ValueError(f"Current infographic inventory mismatch: missing={missing}, extra={extra}")
    if args.infographics_dir.resolve() == DEFAULT_IMAGES.resolve():
        media = ROOT / ".SYSTEMX" / "MEDIA"
        videos = [path for path in media.rglob("*") if path.is_file() and
                  path.suffix.lower() in VIDEO]
        if videos:
            raise ValueError("Video files are not allowed in public media: " + str(videos[0]))
    svg_bytes: dict[str, bytes] = {}
    for item in assets:
        name = item["id"]
        if item.get("file") != "../Infographics/" + name + ".svg" or \
                item.get("width") != 7680 or item.get("height") != 4320:
            raise ValueError(name + ": wrong file path or declared size")
        svg_bytes[name] = verify_file(
            args.infographics_dir / (name + ".svg"),
            expected_bytes=item["bytes"], expected_sha=item["sha256"])
    minimum = min(
        verify_svg(svg_bytes[item["id"]], item, EXPECTED, index, svg_bytes,
                   args.source_dir, args.thumbnail_dir)
        for item in assets
    )
    total = sum(len(data) for data in svg_bytes.values())
    if total >= 32 * 1024 * 1024:
        raise ValueError("Current infographic set exceeds distribution archive bound")
    print(f"Verified 12 current SVGs, 11 source panels and a locked composite atlas; "
          f"{total:,} bytes; minimum text contrast {minimum:.2f}:1")


if __name__ == "__main__":
    main()
