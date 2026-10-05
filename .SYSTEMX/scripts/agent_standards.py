"""Local records for standard roles. No worker runtime, scheduler, or network I/O."""

import json
import hashlib
from pathlib import Path
import re
import uuid

import project_memory as memory

ROLES = {"agent.x": "event-time", "agent.z": "review"}
COMMANDS = {"roles-init", "agent-x", "agent-z"}
MAX_RECORD_BYTES = 32 * 1024 * 1024
REQUIRED = ("scripts/agent_standards.py", "scripts/agent_x.py", "scripts/agent_z.py",
            "config/agent-z-policy.json", "AGENTS/agent.x/README.md", "AGENTS/agent.z/README.md",
            "templates/AGENT-X-MEMORY.md", "templates/AGENT-Z-MEMORY.md",
            "docs/AGENT-X.md", "docs/AGENT-Z.md", "tests/test_agent_standards.py")


def encoded(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def fingerprint(value):
    return hashlib.sha256(encoded(value).encode("utf-8")).hexdigest()


def safe(root, relative):
    """Apply the same path, link, and exact-case checks to root and child records."""
    if (not isinstance(relative, str) or "\\" in relative or ":" in relative or "\x00" in relative or
            any(part in {"", ".", ".."} for part in relative.split("/"))):
        raise ValueError("Use a contained canonical record path")
    path = memory.managed(Path(root), relative)
    parent = Path(root)
    for part in relative.split("/"):
        if parent.exists():
            matches = [p.name for p in parent.iterdir() if p.name.casefold() == part.casefold()]
            if matches and matches != [part]:
                raise ValueError("Exact-case conflict in record path: " + relative)
        parent /= part
    if path.exists() and not path.is_file():
        raise ValueError("A directory occupies a record file: " + relative)
    return path


def read(root, relative):
    path = safe(root, relative)
    if not path.is_file() or path.stat().st_size > MAX_RECORD_BYTES:
        raise ValueError("Missing or oversized record (maximum 32 MiB): " + relative)
    def unique(pairs):
        data = {}
        for key, value in pairs:
            if key in data:
                raise ValueError("Duplicate JSON key: " + key)
            data[key] = value
        return data
    def invalid(value):
        raise ValueError("Non-finite JSON number: " + value)
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique, parse_constant=invalid)


def write(root, relative, value):
    safe(root, relative)
    content = json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    if len(content.encode("utf-8")) > MAX_RECORD_BYTES:
        raise ValueError("Record would exceed maximum 32 MiB; archive or partition records before adding more")
    memory.atomic_write(Path(root), relative, content)


def enabled(root, role):
    _, registry = memory.load(root)
    if not any(item["id"] == role for item in registry["agents"]):
        raise ValueError("Initialize standard roles in this scope with roles-init --apply first")


def task_ids(root, values):
    memory.strings(values, "Task references")
    if len(values) != len(set(values)):
        raise ValueError("Duplicate task references")
    ledger, _ = memory.load(root)
    known = {item["id"] for item in ledger["tasks"]}
    if any(value not in known for value in values):
        raise ValueError("Task references must exist in the selected scope")


def token(value, prefix):
    if not isinstance(value, str) or not re.fullmatch(re.escape(prefix) + r"-[a-f0-9]{20}", value):
        raise ValueError("Invalid " + prefix + " record ID")
    return value


def initialize(root, defaults, apply=False):
    import agent_z
    root, defaults = Path(root), Path(defaults)
    _, registry = memory.load(root)
    policy = agent_z.validate_policy(read(defaults, "config/agent-z-policy.json"))
    seeds = {"EVENTS/EVENTS.json": {"schemaVersion": 1, "events": []},
             "EVENTS/SCHEDULE.json": {"schemaVersion": 1, "items": []},
             "REVIEWS/POLICY.json": policy}
    for agent in ROLES:
        name = "templates/AGENT-" + agent[-1].upper() + "-MEMORY.md"
        seeds["AGENTS/" + agent + "/MEMORY.md"] = safe(defaults, name).read_text(encoding="utf-8")
    known = {item["id"] for item in registry["agents"]}
    additions = [agent for agent in ROLES if agent not in known]
    missing = [name for name in seeds if not safe(root, name).exists()]
    result = {"applied": apply, "register": additions, "add": missing,
              "preserve": [name for name in seeds if name not in missing],
              "runtimeStarted": False, "scope": str(root)}
    if not apply or not (additions or missing):
        return result
    with memory.coordination_lock(root):
        # Refresh the plan after taking the same lock as all scope writers.
        planned = initialize(root, defaults)
        _, registry = memory.load(root)
        log = "logs/roles/" + uuid.uuid4().hex + ".json"
        receipt = {"schemaVersion": 1, "operation": "roles-init", "at": memory.now(), "state": "started"}
        write(root, log, receipt)
        try:
            for name in planned["add"]:
                value = seeds[name]
                if isinstance(value, str):
                    safe(root, name)
                    memory.atomic_write(root, name, value)
                else:
                    write(root, name, value)
            for agent in planned["register"]:
                registry["agents"].append({"id": agent, "role": ROLES[agent],
                                           "memory": "AGENTS/" + agent + "/MEMORY.md"})
            write(root, "AGENTS/REGISTRY.json", registry)
            receipt["state"] = "complete"
        except BaseException:
            receipt["state"] = "failed"
            raise
        finally:
            write(root, log, receipt)
        return {**planned, "applied": True, "receipt": log}


def validate_optional(root):
    """Old scopes without these optional records remain valid after an update."""
    import agent_x
    import agent_z
    _, registry = memory.load(root)
    active = {item["id"] for item in registry["agents"]}
    required = {
        "agent.x": ("EVENTS/EVENTS.json", "EVENTS/SCHEDULE.json", "AGENTS/agent.x/MEMORY.md"),
        "agent.z": ("REVIEWS/POLICY.json", "AGENTS/agent.z/MEMORY.md"),
    }
    for role, paths in required.items():
        if role in active:
            for relative in paths:
                if not safe(root, relative).is_file():
                    raise ValueError("Activated " + role + " is missing required record: " + relative)
    if safe(root, "EVENTS/EVENTS.json").exists():
        agent_x.load_events(root)
    if safe(root, "EVENTS/SCHEDULE.json").exists():
        agent_x.load_schedule(root)
    if safe(root, "REVIEWS/POLICY.json").exists():
        agent_z.validate_policy(read(root, "REVIEWS/POLICY.json"))


def add_cli(subparsers, scope=None):
    import agent_x
    import agent_z
    scope = scope or (lambda parser: parser)
    command = scope(subparsers.add_parser("roles-init", help="preview standard Agent X/Z record setup"))
    command.add_argument("--apply", action="store_true")
    for name, module in (("agent-x", agent_x), ("agent-z", agent_z)):
        parent = subparsers.add_parser(name, help=module.__doc__)
        module.add_cli(parent.add_subparsers(dest="standard_action", required=True), scope)


def dispatch(root, defaults, args):
    import agent_x
    import agent_z
    if args.action == "roles-init":
        result = initialize(root, defaults, args.apply)
    elif args.action == "agent-x":
        enabled(root, "agent.x")
        result = agent_x.dispatch(root, args)
    else:
        if args.standard_action != "policy":
            enabled(root, "agent.z")
        result = agent_z.dispatch(root, defaults, args)
    result.setdefault("scope", str(root))
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    return 0
