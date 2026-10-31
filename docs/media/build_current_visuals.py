#!/usr/bin/env python3
"""Build the current standalone .SYSTEMX visual guides from reviewed art.

The source directory contains one compact JPEG background per concept. Original
imagegen PNGs and the source-to-export receipt are retained outside the public
template. This script adds exact, selectable SVG text to each background; it
does not call a model, edit a source image, or require a raster library.

Usage: python3 docs/media/build_current_visuals.py --source-dir PATH
       [--output-dir PATH]
"""

from __future__ import annotations

import argparse
import base64
from pathlib import Path
import stat
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / ".SYSTEMX" / "MEDIA" / "Infographics"
WIDTH, HEIGHT = 1672, 941

VISUALS = [
    {
        "id": "systemx-guide-lifecycle",
        "kind": "guide",
        "title": "PROJECT LIFECYCLE",
        "subtitle": "Portable records, explicit roles, reviewed releases",
        "labels": ["SET UP", "SELECT SCOPE", "ACTIVATE", "REVIEW", "RELEASE", "RECOVER"],
        "footer": "Task state, release tags, and deployment receipts remain separate.",
        "description": "Six glass panels depict setup, scope selection, role activation, review, release packaging, and recovery. No step executes automatically.",
        "accent": "#70F5CD",
    },
    {
        "id": "systemx-guide-bot-workspaces",
        "kind": "guide",
        "title": "NAMED BOT WORKSPACES",
        "subtitle": "Agent Beta records scope; provider access stays external",
        "labels": ["CANONICAL TASK", "BOT / DOT WORKSPACE", "PROVIDER ACCOUNT"],
        "footer": "A registered workspace does not launch, authenticate, or grant a bot.",
        "description": "A task record points to one named BOT or DOT workspace. A broken connector separates the workspace from an external provider account.",
        "accent": "#52E7E3",
    },
    {
        "id": "systemx-guide-security-access",
        "kind": "guide",
        "title": "SECURITY AND ACCESS",
        "subtitle": "Advisory assessment, guarded key entry, explicit review",
        "labels": ["ASSESS", "HANDLE CREDENTIALS", "WARN AND REVIEW"],
        "footer": "GitHub Actions secrets cannot be read into a local .env by symlink.",
        "description": "A magnified checklist leads to a protected terminal and an advisory shield. The assessment does not prove a device is clean.",
        "accent": "#FFC96B",
    },
    {
        "id": "systemx-guide-access-matrix",
        "kind": "guide",
        "title": "ACCESS MATRIX AND AGENDA",
        "subtitle": "Canonical JSON, human workbook, concise session context",
        "labels": ["JSON DECISIONS", "XLSX REVIEW", "SESSION CONTEXT"],
        "footer": "Matrix rows record intent; host and provider controls enforce access.",
        "description": "A locked JSON decision document flows to a reviewed spreadsheet and a brief session context card with file hash pointers.",
        "accent": "#70F5CD",
    },
    {
        "id": "systemx-agent-0",
        "kind": "role",
        "title": "AGENT 0",
        "subtitle": "Project coordination and acceptance",
        "details": [
            "INPUT  Human objective and selected project scope",
            "OWNS   WORK/TASKS.json, plan, integration, acceptance",
            "LIMIT  External actions follow actual host permissions",
        ],
        "description": "Agent 0 connects a human objective, canonical tasks, and reviewed evidence. It coordinates work and retains task acceptance.",
        "accent": "#70F5A2",
    },
    {
        "id": "systemx-agent-x",
        "kind": "role",
        "title": "AGENT X",
        "subtitle": "Events, time, and due item records",
        "details": [
            "OWNS   EVENTS/EVENTS.json and EVENTS/SCHEDULE.json",
            "NOTES  Observed times, due items, and outcomes",
            "LIMIT  No scheduler execution or notification delivery",
        ],
        "description": "Agent X records event history, time, and due items, without executing a schedule or sending notifications.",
        "accent": "#80BFFF",
    },
    {
        "id": "systemx-agent-y",
        "kind": "role",
        "title": "AGENT Y",
        "subtitle": "Bounded CLI and pull request handoff",
        "details": [
            "OWNS   AGENTS/agent.y/JOBS.json for one assigned task",
            "RUNS   Selected installed CLI under host permissions",
            "LIMIT  No merge or task acceptance authority",
        ],
        "description": "Agent Y takes one assigned task through a selected command-line provider and returns bounded branch or pull request evidence.",
        "accent": "#FF8D8D",
    },
    {
        "id": "systemx-agent-z",
        "kind": "role",
        "title": "AGENT Z",
        "subtitle": "Fixed evidence review",
        "details": [
            "OWNS   Versioned review reports and scorecards",
            "CHECKS 100 questions across 10 categories",
            "LIMIT  Advisory review does not accept a task",
        ],
        "description": "Agent Z reviews evidence against its fixed 100-question policy and returns an advisory scorecard.",
        "accent": "#C9A2FF",
    },
    {
        "id": "systemx-agent-alpha",
        "kind": "role",
        "title": "AGENT ALPHA",
        "subtitle": "Selected AUTOBOT references and Agenda",
        "details": [
            "ROUTES  Up to ten reference functions on request",
            "AGENDA  Starts empty; JSON is the settings source",
            "LIMIT   No extra model workers or scheduler",
        ],
        "description": "Agent Alpha selects bounded reference material from up to ten AUTOBOT functions. Agenda starts empty and does not schedule work.",
        "accent": "#FFD474",
    },
    {
        "id": "systemx-agent-beta",
        "kind": "role",
        "title": "AGENT BETA",
        "subtitle": "Named BOT and DOT workspace records",
        "details": [
            "OWNS   AGENTB/.SYSTEMXB-BOT_NAME per named bot",
            "LINKS  Scope, identity, and canonical TASK references",
            "LIMIT  No provider login, session, or permission grant",
        ],
        "description": "Agent Beta gives each named BOT or DOT a separate local workspace record. Registration does not connect to a provider.",
        "accent": "#6EF0E2",
    },
    {
        "id": "systemx-agent-1",
        "kind": "role",
        "title": "AGENT 1",
        "subtitle": "Security and access assessment",
        "details": [
            "CHECKS 20 categories × 20 questions; 10 event buckets",
            "PLANS  Names-only .env migration and explicit secrets",
            "LIMIT  Advisory status; no device-clean guarantee",
        ],
        "description": "Agent 1 reviews 400 security and access questions, suggests credential migration, and reports advisory findings.",
        "accent": "#FFC96B",
    },
]


def text(x: int, y: int, value: str, size: int, *, weight: int = 400,
         color: str = "#FFFFFF", anchor: str = "start") -> str:
    return (f'<text x="{x}" y="{y}" fill="{color}" font-family="Arial, Helvetica, sans-serif" '
            f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" '
            f'letter-spacing="0.3">{escape(value)}</text>')


def render(item: dict, jpeg: bytes) -> bytes:
    if not jpeg.startswith(b"\xff\xd8") or not jpeg.endswith(b"\xff\xd9"):
        raise ValueError(item["id"] + " source must be a complete JPEG")
    image_data = base64.b64encode(jpeg).decode("ascii")
    title_id = item["id"] + "-title"
    desc_id = item["id"] + "-desc"
    pieces = [
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="7680" height="4320" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" '
        f'aria-labelledby="{title_id} {desc_id}">',
        f'<title id="{title_id}">.SYSTEMX — {escape(item["title"])}</title>',
        f'<desc id="{desc_id}">{escape(item["description"])}</desc>',
        f'<image x="0" y="0" width="{WIDTH}" height="{HEIGHT}" preserveAspectRatio="none" '
        f'xlink:href="data:image/jpeg;base64,{image_data}"/>',
        '<rect x="0" y="0" width="1672" height="162" fill="#061D31"/>',
        '<rect x="0" y="754" width="1672" height="187" fill="#061D31"/>',
        f'<rect x="70" y="156" width="1532" height="4" fill="{item["accent"]}"/>',
        text(72, 52, ".SYSTEMX", 28, weight=700, color=item["accent"]),
        text(1600, 52, "FIELD GUIDE" if item["kind"] == "guide" else "AGENT ROLE",
             24, weight=700, color="#D5E9F5", anchor="end"),
        text(72, 111, item["title"], 53, weight=700),
        text(74, 146, item["subtitle"], 26, color="#DBEBF4"),
    ]
    if item["kind"] == "guide":
        labels = item["labels"]
        centers = [168, 438, 704, 972, 1238, 1502] if len(labels) == 6 else [279, 836, 1393]
        pieces.append('<rect x="0" y="694" width="1672" height="60" fill="#061D31"/>')
        for center, label in zip(centers, labels):
            pieces.append(text(center, 736, label, 24, weight=700, color=item["accent"], anchor="middle"))
        pieces.append(text(836, 846, item["footer"], 27, color="#FFFFFF", anchor="middle"))
        pieces.append(text(836, 899, "SELECTED SCOPE  •  HUMAN REVIEW  •  EVIDENCE",
                           22, color="#D5E9F5", anchor="middle"))
    else:
        for y, line in zip((797, 844, 891), item["details"]):
            pieces.append(text(74, y, line, 25, color="#FFFFFF"))
    pieces.append('</svg>')
    return ("\n".join(pieces) + "\n").encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True,
                        help="directory with ID-background.jpg files")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for item in VISUALS:
        path = args.source_dir / (item["id"] + "-background.jpg")
        detail = path.lstat()
        if not stat.S_ISREG(detail.st_mode) or detail.st_size > 4 * 1024 * 1024:
            raise ValueError("Source must be a regular JPEG under 4 MiB: " + str(path))
        output = args.output_dir / (item["id"] + ".svg")
        payload = render(item, path.read_bytes())
        if len(payload) > 2 * 1024 * 1024:
            raise ValueError("Standalone SVG exceeds 2 MiB: " + item["id"])
        output.write_bytes(payload)
        print(f"{output.name}: {len(payload)} bytes")


if __name__ == "__main__":
    main()
