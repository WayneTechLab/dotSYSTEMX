#!/usr/bin/env python3
"""Build the seven detailed agent diagrams from separately reviewed artwork.

The imagegen artwork remains in an external authoring archive. This script
embeds one compact image per diagram and adds exact, selectable SVG text.
Usage: python3 docs/media/build_detail_visuals.py --source-dir PATH
The accessible text companion is regenerated from the same reviewed role data.
"""

from __future__ import annotations

import argparse
import base64
from pathlib import Path
import stat
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / ".SYSTEMX" / "MEDIA" / "Infographics"
TEXT_OUTPUT = ROOT / ".SYSTEMX" / "MEDIA" / "Reference" / "agent-detail-guide.md"
WIDTH, HEIGHT = 1600, 900
BACKGROUND = "#061D31"

ROLES = (
    {
        "id": "0", "title": "AGENT 0", "subtitle": "Project coordination and owner acceptance",
        "accent": "#70F5A2", "art": "agent-0.jpg",
        "folders": (".SYSTEMX/AGENTS/agent.0/", ".SYSTEMX/ROOT/"),
        "prompt": ("Plan this task, assign one owner, collect evidence,", "then ask me to review acceptance."),
        "commands": ("bash .SYSTEMX/SYSTEMX.sh root --help", "Choose: init | status | packet | request",
                     "node | bind | observe | delta | card", "Tasks: task-add | task-set"),
        "flow": ("Select scope", "Add task", "Route work", "Review evidence", "Owner accepts"),
        "boundary": ("Agent 0 owns canonical task coordination and integration.",
                     "A task is accepted only by the designated owner; a card is evidence, not permission."),
        "description": "Agent 0 records the project objective, coordinates canonical tasks, observes evidence, and hands acceptance to the owner.",
    },
    {
        "id": "x", "title": "AGENT X", "subtitle": "Event history, timing, and due-item records",
        "accent": "#80BFFF", "art": "agent-x.jpg",
        "folders": (".SYSTEMX/AGENTS/agent.x/",),
        "prompt": ("Record this observed check and its time.", "Show what is due, then close the record when reviewed."),
        "commands": ("bash .SYSTEMX/SYSTEMX.sh agent-x --help", "Choose: event | list | schedule | due",
                     "close | validate"),
        "flow": ("Observe", "Record event", "Inspect due", "Close record", "Agent 0 reviews"),
        "boundary": ("Agent X records history and due status; it does not run a scheduler.",
                     "A due item does not send a notification or perform an external action."),
        "description": "Agent X records observed events, due items, and closure without executing scheduled work or sending notifications.",
    },
    {
        "id": "y", "title": "AGENT Y", "subtitle": "Bounded CLI work and pull-request handoff",
        "accent": "#FF9A9A", "art": "agent-y.jpg",
        "folders": (".SYSTEMX/AGENTS/agent.y/",),
        "prompt": ("Prepare one assigned task for an installed CLI.", "Return branch or PR evidence for review; do not merge."),
        "commands": ("bash .SYSTEMX/SYSTEMX.sh agent-y --help", "Choose: providers | prepare | list | run",
                     "show | validate | pr-ready | recover", "abandon | pr-cleanup | pr-close"),
        "flow": ("Assign task", "Prepare lane", "Run bounded", "PR handoff", "Recover / clean"),
        "boundary": ("Agent Y uses host permissions and a selected installed CLI.",
                     "A PR handoff grants no merge authority or canonical task acceptance."),
        "description": "Agent Y prepares and runs one bounded CLI task, creates review evidence, and supports recovery without merging or accepting it.",
    },
    {
        "id": "z", "title": "AGENT Z", "subtitle": "Fixed, versioned evidence review",
        "accent": "#C9A2FF", "art": "agent-z.jpg",
        "folders": (".SYSTEMX/AGENTS/agent.z/",),
        "prompt": ("Review this evidence against the fixed policy.", "Score only supported answers and show the delta."),
        "commands": ("bash .SYSTEMX/SYSTEMX.sh agent-z --help", "Choose: policy | prepare | score",
                     "compare | validate"),
        "flow": ("Evidence packet", "Prepare", "Score policy", "Compare delta", "Advise owner"),
        "boundary": ("Agent Z asks 100 fixed questions across 10 categories.",
                     "A scorecard is advisory evidence; it does not accept a task."),
        "description": "Agent Z applies a fixed 100-question policy to evidence and produces a versioned advisory scorecard.",
    },
    {
        "id": "alpha", "title": "AGENT ALPHA", "subtitle": "AUTOBOT references and optional Agenda settings",
        "accent": "#FFD474", "art": "agent-alpha.jpg",
        "folders": (".SYSTEMX/AGENTS/agent.a/", ".SYSTEMX/AUTOBOT/"),
        "prompt": ("Find the relevant AUTOBOT reference for this task.", "Keep Agenda empty unless I choose a setting."),
        "commands": ("bash .SYSTEMX/SYSTEMX.sh agent-a --help", "Choose: init | list | context | request",
                     "complete | status", "bash .SYSTEMX/SYSTEMX.sh agenda --help"),
        "flow": ("Select reference", "Request context", "Complete", "Agenda optional", "Share status"),
        "boundary": ("Agent Alpha routes up to ten bounded reference functions.",
                     "Agenda defaults to empty; no worker or scheduler starts automatically."),
        "description": "Agent Alpha routes bounded AUTOBOT reference requests while the separate Agenda settings remain empty until explicitly selected.",
    },
    {
        "id": "beta", "title": "AGENT BETA", "subtitle": "Named BOT and DOT workspace records",
        "accent": "#6EF0E2", "art": "agent-beta.jpg",
        "folders": (".SYSTEMX/AGENTB/", ".SYSTEMX/AGENTB/.SYSTEMXB-BOT_NAME/"),
        "prompt": ("Set up a named workspace for Atlas.", "Link only reviewed access intent to one task."),
        "commands": ("bash .SYSTEMX/SYSTEMX.sh agent-beta --help", "Choose: setup | bot-add | access-link",
                     "assign | status | validate"),
        "flow": ("Set up", "Add named bot", "Review link", "Assign task", "Validate", "Agent 0 reviews"),
        "boundary": ("The named folder records scope and task references only.",
                     "It does not log in, launch a provider, or grant OS or API access."),
        "description": "Agent Beta creates one ignored local workspace per named bot, links reviewed access intent, and references canonical tasks without connecting a provider.",
    },
    {
        "id": "1", "title": "AGENT 1", "subtitle": "Advisory security and access assessment",
        "accent": "#FFC96B", "art": "agent-1.jpg",
        "folders": (".SYSTEMX/SECURITY/AGENT1/", ".SYSTEMX/AGENTS/agent.1/"),
        "prompt": ("Review security evidence and inventory .env names only.", "Suggest rotations; do not print credential values."),
        "commands": ("bash .SYSTEMX/SYSTEMX.sh agent-1 --help", "Choose: setup | questions | check | review",
                     "status | env-inventory | env-sanitize", "env-migrate"),
        "flow": ("Set up", "Ask 400", "Check", "Review", "Preview env", "Advise owner"),
        "boundary": ("Twenty categories and ten event buckets yield advisory findings.",
                     "Actions is disabled here. No device-clean claim or live secret write is made."),
        "description": "Agent 1 reviews security evidence with 400 questions and a names-only environment inventory, then provides advisory recommendations.",
    },
)


def _text(x: int, y: int, value: str, size: int = 21, *, color: str = "#E8F5FC",
          weight: int = 400, family: str = "Arial, Helvetica, sans-serif",
          anchor: str = "start") -> str:
    return (f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}" '
            f'font-family="{family}" text-anchor="{anchor}">{escape(value)}</text>')


def _icon(kind: str, x: int, y: int, color: str) -> str:
    shapes = {
        "folder": '<path d="M2 6h8l3 3h11v13H2z M2 6V4h9l3 3"/>',
        "prompt": '<path d="M4 5h20v15H9l-5 4z M8 11h12 M8 15h9"/>',
        "terminal": '<rect x="2" y="4" width="24" height="19" rx="2"/><path d="M6 10l4 4-4 4 M13 18h8"/>',
        "flow": '<path d="M2 13h6l3-7h6l3 7h6 M19 6l-3 7 3 7"/>',
        "limit": '<path d="M14 2l12 22H2z M14 9v7 M14 20v1"/>',
    }
    return (f'<g transform="translate({x} {y})" fill="none" stroke="{color}" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{shapes[kind]}</g>')


def _panel(x: int, y: int, w: int, h: int, accent: str) -> str:
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" '
            f'fill="#09263D" stroke="{accent}" stroke-opacity="0.52" stroke-width="2"/>')


def render(role: dict, art: bytes) -> bytes:
    media_type = "image/png" if role["art"].endswith(".png") else "image/jpeg"
    if media_type == "image/png" and not art.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("Expected PNG: " + role["art"])
    if media_type == "image/jpeg" and not (art.startswith(b"\xff\xd8") and art.endswith(b"\xff\xd9")):
        raise ValueError("Expected complete JPEG: " + role["art"])
    identifier = "systemx-agent-" + role["id"] + "-detail"
    accent = role["accent"]
    title_id, desc_id = identifier + "-title", identifier + "-desc"
    img = base64.b64encode(art).decode("ascii")
    pieces = [
        '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="7680" height="4320" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" '
        f'aria-labelledby="{title_id} {desc_id}">',
        f'<title id="{title_id}">.SYSTEMX — {escape(role["title"])} detailed field guide</title>',
        f'<desc id="{desc_id}">{escape(role["description"])} This image also lists the exact folder, '
        'example prompt, CLI surfaces, five or six process steps, and role boundary.</desc>',
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{BACKGROUND}"/>',
        '<rect x="0" y="0" width="1600" height="160" fill="#061D31"/>',
        f'<rect x="42" y="154" width="1516" height="4" fill="{accent}"/>',
        _text(44, 48, ".SYSTEMX", 29, color=accent, weight=700),
        _text(1556, 48, "DETAILED AGENT FIELD GUIDE", 23, color="#DAEAF4", weight=700,
              anchor="end"),
        _text(44, 106, role["title"], 53, color="#FFFFFF", weight=700),
        _text(47, 143, role["subtitle"], 26, color="#DAEAF4"),
        _panel(42, 184, 718, 106, accent),
        _icon("folder", 60, 201, accent),
        _text(103, 224, "01  RECORD LOCATION", 23, color=accent, weight=700),
    ]
    for i, line in enumerate(role["folders"]):
        pieces.append(_text(65, 251 + i * 27, line, 20, color="#FFFFFF",
                            family="Menlo, Consolas, monospace"))
    pieces.extend([
        _panel(42, 304, 718, 115, accent),
        _icon("prompt", 60, 321, accent),
        _text(103, 344, "02  EXAMPLE PROMPT", 23, color=accent, weight=700),
    ])
    for i, line in enumerate(role["prompt"]):
        pieces.append(_text(65, 374 + i * 29, line, 21, color="#FFFFFF"))
    pieces.extend([
        _panel(42, 433, 718, 154, accent),
        _icon("terminal", 60, 449, accent),
        _text(103, 472, "03  CLI COMMAND / CONTROL", 23, color=accent, weight=700),
    ])
    for i, line in enumerate(role["commands"]):
        pieces.append(_text(65, 504 + i * 23, line, 19, color="#FFFFFF",
                            family="Menlo, Consolas, monospace"))
    pieces.extend([
        _panel(778, 184, 780, 403, accent),
        f'<image x="791" y="195" width="754" height="380" preserveAspectRatio="xMidYMid meet" '
        f'xlink:href="data:{media_type};base64,{img}"/>',
        _panel(42, 604, 1516, 178, accent),
        _icon("flow", 61, 622, accent),
        _text(103, 645, "04  PROCESS FLOW", 23, color=accent, weight=700),
    ])
    steps = role["flow"]
    step_w = 221 if len(steps) == 6 else 272
    gap = 25 if len(steps) == 6 else 32
    total = len(steps) * step_w + (len(steps) - 1) * gap
    start = (WIDTH - total) // 2
    for i, label in enumerate(steps):
        x = start + i * (step_w + gap)
        pieces.append(f'<rect x="{x}" y="672" width="{step_w}" height="69" rx="13" '
                      f'fill="#103A57" stroke="{accent}" stroke-width="1.7"/>')
        pieces.append(_text(x + 14, 714, f"{i + 1:02d}  {label}", 19, color="#FFFFFF", weight=700))
        if i + 1 < len(steps):
            arrow_x = x + step_w + 6
            pieces.append(f'<path d="M{arrow_x} 706h14m-5-5 5 5-5 5" fill="none" '
                          f'stroke="{accent}" stroke-width="3" stroke-linecap="round" '
                          'stroke-linejoin="round"/>')
    pieces.extend([
        _panel(42, 797, 1516, 82, accent),
        _icon("limit", 60, 813, accent),
        _text(103, 836, "BOUNDARY", 22, color=accent, weight=700),
        _text(260, 832, role["boundary"][0], 20, color="#FFFFFF"),
        _text(260, 858, role["boundary"][1], 20, color="#FFFFFF"),
        '</svg>',
    ])
    return ("\n".join(pieces) + "\n").encode("utf-8")


def render_companion() -> str:
    lines = [
        "# Detailed agent field guides",
        "",
        "These seven diagrams provide readable folder, prompt, CLI, process, and boundary text for",
        "the second .SYSTEMX infographic set. Each SVG has a 7680 × 4320 canvas with exact vector",
        "labels. The generated artwork has fewer native pixels; the canvas size does not create",
        "native 8K illustration detail. The paths below are relative to an adopted project root.",
        "",
        "From the project root on macOS/Linux, run `bash .SYSTEMX/SYSTEMX.sh ROLE --help`.",
        "On Windows, run `pwsh -File .SYSTEMX/SYSTEMX.ps1 ROLE --help`. The installed",
        "`systemx` package entry point does not expose these agent commands. In each SVG",
        "panel, the first line is a copyable help command; `|` separates alternative",
        "subcommands and is **not** a shell operator to paste. Replace `--help` with one",
        "chosen subcommand and its required arguments. Preview first; `--apply` is explicit",
        "where supported.",
        "This repository has GitHub Actions disabled and includes no workflow.",
        "",
    ]
    for role in ROLES:
        image = "../Infographics/systemx-agent-" + role["id"] + "-detail.svg"
        help_name = {"0": "root", "alpha": "agent-a"}.get(role["id"], "agent-" + role["id"])
        lines.extend([
            "## " + role["title"],
            "",
            "[Open the detailed SVG](" + image + ") — " + role["subtitle"] + ".",
            "",
            "**Record location:** " + "; ".join("`" + path + "`" for path in role["folders"]) + ".",
            "",
            "**Example prompt:** “" + " ".join(role["prompt"]) + "”",
            "",
            "**CLI help:** `bash .SYSTEMX/SYSTEMX.sh " + help_name + " --help`.",
            "",
            "**Command panel:** " + "; ".join("`" + item + "`" for item in role["commands"]) + ".",
            "",
            "**Process:** " + " → ".join(role["flow"]) + ".",
            "",
            "**Boundary:** " + " ".join(role["boundary"]),
            "",
        ])
        if role["id"] == "y":
            lines.extend(["Native Windows `agent-y run --apply` is disabled in this beta pending",
                          "process-termination verification.", ""])
        if role["id"] == "1":
            lines.extend(["On native Windows, metadata first setup, status, questions, and",
                          "warning-only filename checks remain available. Dotenv inventory,",
                          "sanitize, and migrate; answer-file review; and setup reconfiguration",
                          "fail closed. Actions remains disabled in this repository.", ""])
    lines.extend([
        "Agent Beta's named folder and Agent 1's `agent.1` record are generated local state;",
        "neither is a second portable source copy. The Access Matrix records reviewed intent and",
        "does not grant OS or provider permission. Agent 1's `.env` commands use names-only shared",
        "records; sensitive file operations fail closed on native Windows in this beta.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    parser.add_argument("--text-output", type=Path, default=TEXT_OUTPUT)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for role in ROLES:
        source = args.source_dir / role["art"]
        detail = source.lstat()
        if not stat.S_ISREG(detail.st_mode) or detail.st_size > 3 * 1024 * 1024:
            raise ValueError("Art must be a regular file below 3 MiB: " + str(source))
        output = args.output_dir / ("systemx-agent-" + role["id"] + "-detail.svg")
        payload = render(role, source.read_bytes())
        if len(payload) > 2 * 1024 * 1024:
            raise ValueError("Portable SVG exceeds 2 MiB: " + output.name)
        output.write_bytes(payload)
        print(output.name + ": " + str(len(payload)) + " bytes")
    args.text_output.parent.mkdir(parents=True, exist_ok=True)
    args.text_output.write_text(render_companion(), encoding="utf-8")
    print(args.text_output.name + ": " + str(args.text_output.stat().st_size) + " bytes")


if __name__ == "__main__":
    main()
