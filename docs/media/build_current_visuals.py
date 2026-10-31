#!/usr/bin/env python3
"""Build current imagegen-backed SVG guides and a final composite atlas.

The eleven individual diagrams embed compact, privately retained artwork and
add exact selectable vector labels. Run once without --thumbnail-dir for the
individual SVGs. After visually reviewing them, render each SVG to a compact
JPEG in --thumbnail-dir and run again to assemble the atlas from those final
panels. The declared 7680 x 4320 canvas sharpens vector text; it does not add
native detail to embedded raster art. No model or network call occurs here.
"""

from __future__ import annotations

import argparse
import base64
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import struct
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[2]
SPECS = Path(__file__).with_name("current_visual_specs.json")
OUTPUT = ROOT / ".SYSTEMX" / "MEDIA" / "Infographics"
INDEX = ROOT / ".SYSTEMX" / "MEDIA" / "Reference" / "ASSETS.json"
W, H = 1600, 900
MAX_SVG_BYTES = 1_900_000  # below manager.MAX_FILE (2 MiB)
BG, PANEL, FLOW = "#061D31", "#0D2D45", "#123B55"
WHITE, SOFT = "#FFFFFF", "#E2F0F7"
MAP_NAMES = (
    "systemx-map-architecture", "systemx-map-task-cycle",
    "systemx-map-governance", "systemx-map-onboarding",
)
AGENT_NAMES = tuple("systemx-agent-" + name for name in
                    ("0", "x", "y", "z", "alpha", "beta", "1"))
EXPECTED = MAP_NAMES + AGENT_NAMES


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def label(x: int, y: int, value: str, size: int, *, bg: str = BG,
          color: str = WHITE, weight: int = 400, mono: bool = False,
          anchor: str = "start") -> str:
    family = "Menlo, Consolas, monospace" if mono else "Arial, Helvetica, sans-serif"
    return (f'<text x="{x}" y="{y}" fill="{color}" data-bg="{bg}" '
            f'font-size="{size}" font-weight="{weight}" font-family="{family}" '
            f'text-anchor="{anchor}">{escape(value)}</text>')


def icon(kind: str, x: int, y: int, color: str) -> str:
    paths = {
        "folder": '<path d="M2 7h8l3 3h13v16H2z M2 7V5h9l3 3"/>',
        "route": '<circle cx="5" cy="14" r="3"/><circle cx="25" cy="5" r="3"/>'
                 '<circle cx="25" cy="25" r="3"/><path d="M8 14h8l6-8 M16 14l6 10"/>',
        "shield": '<path d="M15 2l12 5v8c0 8-5 12-12 15C8 27 3 23 3 15V7z"/>'
                  '<path d="M9 15l4 4 8-9"/>',
        "terminal": '<rect x="2" y="4" width="27" height="23" rx="3"/>'
                    '<path d="M7 11l5 5-5 5 M15 21h9"/>',
        "compass": '<circle cx="15" cy="15" r="13"/>'
                   '<path d="M18 10l-4 8-5 2 3-7z"/>',
        "clock": '<circle cx="15" cy="15" r="13"/><path d="M15 7v9l6 4"/>',
        "review": '<circle cx="13" cy="13" r="9"/>'
                  '<path d="M20 20l9 9 M9 13l3 3 6-7"/>',
        "reference": '<path d="M4 4h9l2 3 2-3h9v23h-9l-2 2-2-2H4z M15 7v20"/>',
        "bot": '<rect x="4" y="8" width="22" height="18" rx="4"/>'
               '<path d="M15 3v5 M10 16h1 M20 16h1 M10 21h10"/>',
    }
    return (f'<g transform="translate({x} {y})" fill="none" stroke="{color}" '
            'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
            + paths[kind] + '</g>')


def panel(x: int, y: int, width: int, height: int, accent: str) -> str:
    return (f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="18" '
            f'fill="{PANEL}" stroke="{accent}" stroke-opacity="0.65" '
            'stroke-width="2"/>'
            f'<path d="M{x + 20} {y + 2}h{min(width - 40, 180)}" '
            f'stroke="{accent}" stroke-opacity="0.65" stroke-width="3"/>')


def svg_start(spec: dict, title: str) -> list[str]:
    name = spec["id"]
    return [
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" '
        'width="7680" height="4320" viewBox="0 0 1600 900" role="img" '
        f'aria-labelledby="{name}-title {name}-desc">',
        f'<title id="{name}-title">.SYSTEMX — {escape(title)}</title>',
        f'<desc id="{name}-desc">{escape(spec["description"])}</desc>',
        f'<rect width="{W}" height="{H}" fill="{BG}"/>',
    ]


def header(spec: dict, kind: str) -> list[str]:
    accent = spec["accent"]
    return [
        '<path d="M0 160h1600 M0 605h1600 M0 790h1600" '
        'fill="none" stroke="#3B748D" stroke-opacity="0.28"/>',
        f'<rect x="42" y="154" width="1516" height="4" fill="{accent}"/>',
        icon(spec["icon"], 43, 36, accent),
        label(86, 54, ".SYSTEMX", 28, color=accent, weight=700),
        label(1558, 54, kind, 22, color=SOFT, weight=700, anchor="end"),
        label(44, 108, spec["title"], 44, weight=700),
        label(46, 143, spec["subtitle"], 24, color=SOFT),
    ]


def image_tag(data: bytes, mime: str, x: int, y: int,
              width: int, height: int, *, fit: str = "slice") -> str:
    if fit not in {"slice", "meet"}:
        raise ValueError("Unknown image fit")
    encoded = base64.b64encode(data).decode("ascii")
    return (f'<image x="{x}" y="{y}" width="{width}" height="{height}" '
            f'preserveAspectRatio="xMidYMid {fit}" '
            f'xlink:href="data:{mime};base64,{encoded}"/>')


def flow_and_boundary(spec: dict) -> list[str]:
    accent = spec["accent"]
    steps = spec["flow"]
    if len(steps) != 5 or len(spec["boundary"]) != 2:
        raise ValueError(spec["id"] + " needs five flow steps and two boundary lines")
    parts = [
        panel(42, 606, 1516, 175, accent),
        icon("route", 60, 620, accent),
        label(103, 645, "04  PROCESS FLOW", 22, bg=PANEL, weight=700),
    ]
    for n, step in enumerate(steps):
        x = 56 + n * 304
        parts.extend([
            f'<rect x="{x}" y="672" width="272" height="69" rx="13" '
            f'fill="{FLOW}" stroke="{accent}" stroke-width="1.7"/>',
            label(x + 15, 714, f"{n + 1:02d}  {step}", 18,
                  bg=FLOW, weight=700),
        ])
        if n < 4:
            parts.append(f'<path d="M{x + 278} 706h18m-6-6 6 6-6 6" '
                         f'fill="none" stroke="{accent}" stroke-width="3"/>')
    parts.extend([
        panel(42, 797, 1516, 82, accent),
        icon("shield", 60, 813, accent),
        label(103, 837, "BOUNDARY", 21, bg=PANEL, weight=700),
        label(258, 832, spec["boundary"][0], 19, bg=PANEL),
        label(258, 858, spec["boundary"][1], 19, bg=PANEL),
    ])
    return parts


def render_map(spec: dict, art: bytes, mime: str) -> bytes:
    parts = svg_start(spec, spec["title"]) + header(spec, "CURRENT SYSTEM MAP")
    if len(spec["sections"]) != 3:
        raise ValueError(spec["id"] + " needs three sections")
    for n, (heading, one, two) in enumerate(spec["sections"]):
        y = 184 + n * 136
        parts.extend([
            panel(42, y, 718, 124, spec["accent"]),
            label(65, y + 37, f"0{n + 1}  {heading}", 21, bg=PANEL, weight=700),
            label(65, y + 70, one, 18, bg=PANEL,
                  mono=one.startswith(".SYSTEMX/") or one.startswith("systemx ")),
            label(65, y + 98, two, 18, bg=PANEL,
                  mono=two.startswith(".SYSTEMX/")),
        ])
    parts.extend([panel(778, 184, 780, 404, spec["accent"]),
                  image_tag(art, mime, 790, 195, 754, 380)])
    parts.extend(flow_and_boundary(spec))
    return ("\n".join(parts + ["</svg>"]) + "\n").encode("utf-8")


def render_agent(spec: dict, art: bytes, mime: str) -> bytes:
    accent = spec["accent"]
    parts = svg_start(spec, spec["title"] + " field guide") + header(
        spec, "CURRENT AGENT FIELD GUIDE")
    parts.extend([
        panel(42, 184, 718, 106, accent),
        icon("folder", 60, 201, accent),
        label(103, 224, "01  RECORD LOCATION", 21, bg=PANEL, weight=700),
    ])
    if len(spec["folders"]) > 2 or len(spec["prompt"]) > 2 or len(spec["commands"]) > 4:
        raise ValueError(spec["id"] + " has more text than its panel supports")
    for n, value in enumerate(spec["folders"]):
        parts.append(label(65, 251 + n * 27, value, 19, bg=PANEL, mono=True))
    parts.extend([
        panel(42, 304, 718, 115, accent),
        icon("route", 60, 321, accent),
        label(103, 344, "02  EXAMPLE PROMPT", 21, bg=PANEL, weight=700),
    ])
    for n, value in enumerate(spec["prompt"]):
        parts.append(label(65, 374 + n * 29, value, 20, bg=PANEL))
    parts.extend([
        panel(42, 433, 718, 154, accent),
        icon("terminal", 60, 449, accent),
        label(103, 472, "03  CLI COMMAND / CONTROL", 21, bg=PANEL, weight=700),
    ])
    for n, value in enumerate(spec["commands"]):
        parts.append(label(65, 504 + n * 23, value, 17, bg=PANEL, mono=True))
    parts.extend([panel(778, 184, 780, 404, accent),
                  image_tag(art, mime, 790, 195, 754, 380)])
    parts.extend(flow_and_boundary(spec))
    return ("\n".join(parts + ["</svg>"]) + "\n").encode("utf-8")


def png_size(data: bytes) -> tuple[int, int]:
    if not data.startswith(b"\x89PNG\r\n\x1a\n") or len(data) < 24:
        raise ValueError("Incomplete PNG artwork")
    return struct.unpack(">II", data[16:24])


def jpeg_size(data: bytes) -> tuple[int, int]:
    if not data.startswith(b"\xff\xd8") or not data.endswith(b"\xff\xd9"):
        raise ValueError("Incomplete JPEG artwork")
    i = 2
    while i < len(data) - 4:
        if data[i] != 0xff:
            i += 1
            continue
        marker = data[i + 1]
        i += 2
        if marker in (0xd8, 0xd9, 0x01) or 0xd0 <= marker <= 0xd7:
            continue
        count = int.from_bytes(data[i:i + 2], "big")
        if count < 2 or i + count > len(data):
            raise ValueError("Malformed JPEG marker")
        if marker in (0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7,
                      0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf):
            # SOF stores height before width.
            return (int.from_bytes(data[i + 5:i + 7], "big"),
                    int.from_bytes(data[i + 3:i + 5], "big"))
        i += count
    raise ValueError("JPEG dimensions not found")


def load_art(folder: Path, stem: str) -> tuple[Path, bytes, str, int, int]:
    choices = [folder / (stem + ext) for ext in (".jpg", ".jpeg", ".png")]
    found = [path for path in choices if path.is_file()]
    if len(found) != 1:
        raise ValueError("Need exactly one reviewed compact art file for " + stem)
    path = found[0]
    if path.is_symlink() or not path.resolve().is_relative_to(folder.resolve()):
        raise ValueError("Art must be a regular file inside source-dir")
    data = path.read_bytes()
    mime = "image/png" if path.suffix == ".png" else "image/jpeg"
    width, height = png_size(data) if mime == "image/png" else jpeg_size(data)
    if len(data) > 1_300_000 or width < 500 or height < 280:
        raise ValueError("Art needs <=1.3 MB and at least 500 x 280 pixels")
    return path, data, mime, width, height


def record(spec: dict, content: bytes, kind: str,
           art: tuple[Path, bytes, str, int, int] | None = None) -> dict:
    entry = {
        "id": spec["id"], "kind": kind, "title": spec["title"],
        "description": spec["description"],
        "file": "../Infographics/" + spec["id"] + ".svg",
        "width": 7680, "height": 4320,
        "bytes": len(content), "sha256": digest(content),
    }
    if art:
        path, data, mime, width, height = art
        entry["embeddedArt"] = {
            "fileName": path.name, "mime": mime,
            "width": width, "height": height,
            "bytes": len(data), "sha256": digest(data),
            "note": "Compact derivative; imagegen master remains outside the template.",
        }
    return entry


def render_atlas(specs: dict, panels: list[dict], thumbs: dict[str, tuple[bytes, int, int]]) -> bytes:
    if tuple(item["id"] for item in panels) != EXPECTED or set(thumbs) != set(EXPECTED):
        raise ValueError("Atlas requires eleven final panels and eleven exact thumbnails")
    sources = {item["id"]: item["sha256"] for item in panels}
    meta = escape(json.dumps({"sourcePanels": sources}, sort_keys=True,
                             separators=(",", ":")))
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'xmlns:xlink="http://www.w3.org/1999/xlink" width="7680" height="4320" '
        'viewBox="0 0 1600 900" role="img" '
        'aria-labelledby="systemx-atlas-title systemx-atlas-desc">',
        '<title id="systemx-atlas-title">.SYSTEMX — combined system atlas</title>',
        '<desc id="systemx-atlas-desc">A true visual composite of four current '
        'system map panels and seven current agent guide panels. Open each '
        'full-size SVG and the text companion for readable details.</desc>',
        f'<metadata>{meta}</metadata>',
        f'<rect width="{W}" height="{H}" fill="{BG}"/>',
        label(42, 55, ".SYSTEMX", 29, color="#70F5CD", weight=700),
        label(1558, 55, "COMBINED ATLAS / 11 LOCKED PANELS", 21,
              color=SOFT, weight=700, anchor="end"),
        label(42, 109, "ONE SYSTEM / FOUR MAPS / SEVEN AGENTS", 42, weight=700),
        label(44, 143, "Zoom into the full-size panels for paths, commands and boundaries",
              21, color=SOFT),
    ]
    for n, spec in enumerate(specs["maps"]):
        x = 42 + n * 389
        data, _, _ = thumbs[spec["id"]]
        parts.extend([
            panel(x, 174, 365, 270, spec["accent"]),
            image_tag(data, "image/jpeg", x + 10, 185, 345, 194),
            label(x + 15, 412, f"0{n + 1}  {spec['title'].split(' / ', 1)[1]}",
                  18, bg=PANEL, weight=700),
        ])
    parts.append('<path d="M800 446v26 M100 472h1400" fill="none" '
                 'stroke="#70F5CD" stroke-width="3"/>')
    role_notes = (
        "TASK + ACCEPTANCE", "EVENTS + DUE", "SELECTED CLI",
        "FIXED REVIEW", "10 REFERENCES", "OFFLINE BOT", "WARNING-ONLY",
    )
    for n, spec in enumerate(specs["agents"]):
        x = 42 + n * 219
        data, _, _ = thumbs[spec["id"]]
        parts.extend([
            panel(x, 490, 202, 280, spec["accent"]),
            image_tag(data, "image/jpeg", x + 9, 502, 184, 145, fit="meet"),
            label(x + 14, 689, spec["title"], 19, bg=PANEL, weight=700),
            label(x + 14, 718, role_notes[n], 15, bg=PANEL),
            label(x + 14, 751, spec["id"].removeprefix("systemx-") + ".svg",
                  14, bg=PANEL, mono=True),
        ])
    parts.extend([
        label(42, 839,
              "SELECT SCOPE  →  READ TASK  →  ROUTE WORK  →  REVIEW EVIDENCE  →  OWNER ACCEPTS",
              23, weight=700),
        label(1558, 880,
              "The atlas is navigation; no role, workbook row or provider label grants access.",
              17, color=SOFT, anchor="end"),
        "</svg>",
    ])
    return ("\n".join(parts) + "\n").encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", required=True, type=Path)
    parser.add_argument("--thumbnail-dir", type=Path,
                        help="eleven JPEG thumbnails of final individual SVGs; assembles atlas")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    parser.add_argument("--index-output", type=Path)
    parser.add_argument("--generated-on", default=date.today().isoformat())
    args = parser.parse_args()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.generated_on):
        parser.error("--generated-on must be YYYY-MM-DD")
    specs = json.loads(SPECS.read_text(encoding="utf-8"))
    if specs.get("schemaVersion") != 1 or tuple(
            item["id"] for item in specs["maps"] + specs["agents"]) != EXPECTED:
        raise ValueError("Current visual spec inventory is not exactly 4 maps plus 7 agents")
    source = args.source_dir.resolve(strict=True)
    if not source.is_dir() or source.is_symlink():
        raise ValueError("source-dir must be a real directory")
    built: dict[str, bytes] = {}
    entries: list[dict] = []
    for kind, group in (("system-map", specs["maps"]), ("agent-guide", specs["agents"])):
        for spec in group:
            art = load_art(source, spec["art"])
            content = (render_map(spec, art[1], art[2]) if kind == "system-map"
                       else render_agent(spec, art[1], art[2]))
            if len(content) > MAX_SVG_BYTES:
                raise ValueError(spec["id"] + " exceeds the compact SVG bound")
            built[spec["id"] + ".svg"] = content
            entries.append(record(spec, content, kind, art))
    if args.thumbnail_dir:
        thumb_dir = args.thumbnail_dir.resolve(strict=True)
        if not thumb_dir.is_dir():
            raise ValueError("thumbnail-dir must be a real directory")
        thumbs: dict[str, tuple[bytes, int, int]] = {}
        for name in EXPECTED:
            path = thumb_dir / (name + ".jpg")
            if path.is_symlink() or not path.is_file():
                raise ValueError("Missing ordinary final-panel thumbnail: " + path.name)
            data = path.read_bytes()
            width, height = jpeg_size(data)
            if len(data) > 110_000 or width < 300 or height < 160:
                raise ValueError("Thumbnail must be <=110 KB and at least 300 x 160")
            thumbs[name] = (data, width, height)
        atlas_spec = {"id": "systemx-atlas", "title": "Combined atlas",
                      "description": "Four current system maps and seven current agent guides superimposed into one navigational composition."}
        atlas = render_atlas(specs, entries, thumbs)
        if len(atlas) > MAX_SVG_BYTES:
            raise ValueError("Combined atlas exceeds the compact SVG bound")
        built["systemx-atlas.svg"] = atlas
        atlas_entry = record(atlas_spec, atlas, "atlas")
        atlas_entry["sources"] = {item["id"]: item["sha256"] for item in entries}
        atlas_entry["thumbnails"] = {
            name: {"fileName": name + ".jpg", "bytes": len(thumbs[name][0]),
                   "width": thumbs[name][1], "height": thumbs[name][2],
                   "sha256": digest(thumbs[name][0])}
            for name in EXPECTED}
        entries.append(atlas_entry)
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    for name, content in built.items():
        (out / name).write_bytes(content)
    if args.thumbnail_dir:
        index_path = args.index_output or (
            INDEX if out.resolve() == OUTPUT.resolve() else out / "ASSETS.json")
        baseline = (ROOT / ".SYSTEMX" / "VERSION").read_text(encoding="utf-8").strip()
        index = {
            "schemaVersion": 4, "generatedOn": args.generated_on,
            "product": ".SYSTEMX", "softwareBaseline": baseline,
            "scope": "four current maps, seven current agent guides, one combined atlas",
            "canvas": {"width": 7680, "height": 4320,
                       "note": "Vector labels are crisp; embedded art retains recorded native dimensions."},
            "assets": entries,
        }
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n",
                              encoding="utf-8")
        print(f"Built 12 SVGs and {index_path}; {sum(map(len, built.values())):,} bytes")
    else:
        print("Built 11 individual SVGs; atlas awaits reviewed final-panel thumbnails")


if __name__ == "__main__":
    main()
