"""Optional on-demand specialist context records; no autonomous bot runtime."""

from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import uuid

import agent_standards as records
import project_memory as memory

SLOTS = (
    ("design", "Design", "Design.MD"), ("soul", "Soul", "Soul.MD"),
    ("memory", "Memory", "Memory.MD"), ("rules", "Rules", "Rules.MD"),
    ("research", "Research", "Research.MD"), ("brand", "Brand", "Brand.MD"),
    ("media", "Media", "Media.MD"), ("tokens", "Tokens", "Tokens.MD"),
    ("data", "Data", "Data.MD"), ("archive", "Archive", "Archive.MD"),
)
CATALOG = "AUTOBOT/CATALOG.json"
REQUESTS = "AUTOBOT/REQUESTS.json"
CHARTER = "AUTOBOT/AGENTA.MD"
AGENT = "agent.a"
ROLE = "autobot-coordinator"
COMMANDS = {"autobot", "agent-a"}
MAX_FILE_BYTES = 256 * 1024
MAX_PACKET_BYTES = 64 * 1024
MAX_LEDGER_BYTES = 8 * 1024 * 1024
MAX_REQUESTS = 4096
SEEDS = ("README.md", "AGENTA.MD", "CATALOG.json", "REQUESTS.json") + tuple(slot[2] for slot in SLOTS)
REQUIRED = ("scripts/autobots.py", "tests/test_autobots.py", "templates/AGENT-A-MEMORY.md",
            "AGENTS/agent.a/README.md") + tuple("AUTOBOT/" + name for name in SEEDS) + tuple(
                "templates/autobot/" + name for name in SEEDS)
CALLERS = ("agent.0", "agent.x", "agent.y", "agent.z", "agent.a", "agent.b", "tools")
LIMIT = ("Advisory context only. Caller labels are local claims, not authenticated identities. "
         "No model, process, tool, network, DATA scan, task acceptance, or automatic loop is started.")


def _text(root, relative, maximum=MAX_FILE_BYTES):
    path = records.safe(root, relative)
    if not path.is_file() or path.stat().st_size > maximum:
        raise ValueError("Missing or oversized AUTOBOT file: " + relative)
    with path.open("rb") as source:
        raw = source.read(maximum + 1)
    if len(raw) > maximum:
        raise ValueError("Oversized AUTOBOT file: " + relative)
    text = raw.decode("utf-8")
    if "\x00" in text:
        raise ValueError("AUTOBOT files must be UTF-8 text without NUL bytes: " + relative)
    return text, {"path": relative, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}


def _json(root, relative, maximum=MAX_FILE_BYTES):
    text, _ = _text(root, relative, maximum)
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate AUTOBOT JSON key: " + key)
            result[key] = value
        return result
    def invalid(value):
        raise ValueError("Non-finite AUTOBOT number: " + value)
    try:
        return json.loads(text, object_pairs_hook=unique, parse_constant=invalid)
    except RecursionError as error:
        raise ValueError("AUTOBOT JSON nesting exceeds the supported parser depth: " + relative) from error


def _string(value, label, maximum=4096, nonempty=True):
    memory.string(value, label, nonempty=nonempty)
    if len(value.encode("utf-8")) > maximum:
        raise ValueError(label + " exceeds its UTF-8 byte limit")


def _strings(value, label, maximum=32, item_bytes=2048, nonempty=False):
    memory.strings(value, label, nonempty=nonempty)
    if len(value) > maximum or len(value) != len(set(value)):
        raise ValueError(label + " must be a bounded list of unique entries")
    for item in value:
        _string(item, label, item_bytes)


def _schema(value, fields, label):
    memory.fields(value, fields, label)
    if type(value["schemaVersion"]) is not int or value["schemaVersion"] != 1:
        raise ValueError(label + " schemaVersion must be the integer 1")


def validate_catalog(data):
    _schema(data, ("schemaVersion", "coordinator", "maximum", "bots"), "AUTOBOT catalog")
    if data["coordinator"] != AGENT or type(data["maximum"]) is not int or data["maximum"] != 10:
        raise ValueError("AUTOBOT uses agent.a and a fixed maximum of 10 specialist slots")
    if not isinstance(data["bots"], list) or len(data["bots"]) != 10:
        raise ValueError("Retain exactly the 10 named AUTOBOT slots; select only those needed per request")
    for item, (slug, name, filename) in zip(data["bots"], SLOTS):
        memory.fields(item, ("id", "name", "file", "functions"), "AUTOBOT slot")
        if (item["id"], item["name"], item["file"]) != ("autobot." + slug, name, "AUTOBOT/" + filename):
            raise ValueError("AUTOBOT IDs, names, exact-case files, and slot order are fixed")
        _strings(item["functions"], "AUTOBOT functions", maximum=10, item_bytes=512, nonempty=True)
    return data


def _scope(root):
    root = Path(root)
    return {"kind": "project", "name": root.parent.name} if root.name == ".SYSTEMXP" else {
        "kind": "root", "name": ".SYSTEMX"}


def _selected(bots):
    _strings(bots, "Selected AUTOBOTs", maximum=10, item_bytes=64, nonempty=True)
    known = {"autobot." + slot[0] for slot in SLOTS}
    if any(item not in known for item in bots):
        raise ValueError("Select fixed autobot.<name> IDs; AUTOBOT requests cannot nest or call another coordinator")
    return sorted(bots)


def _caller(root, caller, known=None):
    if caller not in CALLERS:
        raise ValueError("Caller must be a registered agent.0/a/b/x/y/z role or tools")
    if known is None:
        _, registry = memory.load(root)
        known = {item["id"] for item in registry["agents"]}
    if caller != "tools" and caller not in known:
        raise ValueError("The claimed caller must be registered in the selected scope")


def _active(root):
    _, registry = memory.load(root)
    if not any(item["id"] == AGENT for item in registry["agents"]):
        raise ValueError("Initialize AGENTA in this scope with autobot init --apply first")


def context(root, bots):
    """Load explicit specialist files and the charter, never arbitrary paths or DATA."""
    catalog = validate_catalog(_json(root, CATALOG))
    selected = _selected(bots)
    charter, provenance = _text(root, CHARTER)
    sources = [{**provenance, "content": charter}]
    for item in catalog["bots"]:
        if item["id"] in selected:
            content, provenance = _text(root, item["file"])
            sources.append({"id": item["id"], **provenance, "content": content})
    packet = {"coordinator": AGENT, "scope": _scope(root), "selected": selected,
              "policyHash": records.fingerprint(catalog), "sources": sources,
              "executed": False, "limit": LIMIT}
    if len(records.encoded(packet).encode("utf-8")) > MAX_PACKET_BYTES:
        raise ValueError("Selected AUTOBOT context exceeds 64 KiB; reduce selected content before requesting")
    return packet


def _identity(root, args):
    _caller(root, args.caller)
    _string(args.purpose, "Request purpose", maximum=4096)
    _string(args.input_revision, "Input revision", maximum=1024)
    _string(args.task or "", "Task", maximum=128, nonempty=False)
    records.task_ids(root, [args.task] if args.task else [])
    packet = context(root, args.bot)
    identity = {"scope": packet["scope"], "caller": args.caller, "purpose": args.purpose,
                "inputRevision": args.input_revision, "task": args.task or "",
                "selected": packet["selected"], "policyHash": packet["policyHash"],
                "files": [{key: source[key] for key in ("path", "sha256", "bytes")}
                          for source in packet["sources"]]}
    return identity, packet


def _check_identity(root, value, known_agents, known_tasks):
    memory.fields(value, ("scope", "caller", "purpose", "inputRevision", "task", "selected",
                          "policyHash", "files"), "AUTOBOT request identity")
    if value["scope"] != _scope(root):
        raise ValueError("AUTOBOT request belongs to a different root or project scope")
    _caller(root, value["caller"], known_agents)
    for key, size, nonempty in (("purpose", 4096, True), ("inputRevision", 1024, True), ("task", 128, False)):
        _string(value[key], "Request " + key, size, nonempty)
    if value["task"] and value["task"] not in known_tasks:
        raise ValueError("AUTOBOT task reference must exist in the selected scope")
    if value["selected"] != _selected(value["selected"]):
        raise ValueError("AUTOBOT selection must use canonical sorted IDs")
    if not isinstance(value["policyHash"], str) or not re.fullmatch(r"[a-f0-9]{64}", value["policyHash"]):
        raise ValueError("Invalid AUTOBOT policy hash")
    expected = [CHARTER] + ["AUTOBOT/" + filename for slug, _, filename in SLOTS
                            if "autobot." + slug in value["selected"]]
    if not isinstance(value["files"], list) or len(value["files"]) != len(expected):
        raise ValueError("AUTOBOT file provenance must match selected context")
    for source, relative in zip(value["files"], expected):
        memory.fields(source, ("path", "sha256", "bytes"), "AUTOBOT file provenance")
        if (source["path"] != relative or not isinstance(source["sha256"], str) or
                not re.fullmatch(r"[a-f0-9]{64}", source["sha256"]) or type(source["bytes"]) is not int or
                not 0 <= source["bytes"] <= MAX_FILE_BYTES):
            raise ValueError("Invalid AUTOBOT selected-file provenance")


def _completion(value):
    memory.fields(value, ("completedAt", "summary", "responseRevision", "evidence"), "AUTOBOT completion")
    memory.timestamp(value["completedAt"])
    _string(value["summary"], "Response summary", maximum=8192)
    _string(value["responseRevision"], "Response revision", maximum=1024)
    _strings(value["evidence"], "Original evidence references", maximum=32, item_bytes=2048, nonempty=True)
    if len(records.encoded(value).encode("utf-8")) > MAX_PACKET_BYTES:
        raise ValueError("AUTOBOT completion exceeds the 64 KiB response limit")


def load_requests(root):
    data = _json(root, REQUESTS, MAX_LEDGER_BYTES)
    _schema(data, ("schemaVersion", "requests"), "AUTOBOT request ledger")
    if not isinstance(data["requests"], list) or len(data["requests"]) > MAX_REQUESTS:
        raise ValueError("AUTOBOT request ledger exceeds its bounded capacity")
    ledger, registry = memory.load(root)
    known_agents = {item["id"] for item in registry["agents"]}
    known_tasks = {item["id"] for item in ledger["tasks"]}
    seen = set()
    latest = datetime.now(timezone.utc) + timedelta(minutes=5)
    for request in data["requests"]:
        memory.fields(request, ("id", "createdAt", "identity", "state", "completion"), "AUTOBOT request")
        records.token(request["id"], "ABR")
        _check_identity(root, request["identity"], known_agents, known_tasks)
        if request["id"] != "ABR-" + records.fingerprint(request["identity"])[:20] or request["id"] in seen:
            raise ValueError("AUTOBOT request identity is duplicate or inconsistent")
        seen.add(request["id"])
        created = memory.timestamp(request["createdAt"])
        if created > latest:
            raise ValueError("AUTOBOT creation timestamp is in the future")
        if request["state"] == "requested":
            if request["completion"] is not None:
                raise ValueError("Requested AUTOBOT record cannot contain completion")
        elif request["state"] == "complete":
            _completion(request["completion"])
            completed = memory.timestamp(request["completion"]["completedAt"])
            if completed < created or completed > latest:
                raise ValueError("AUTOBOT completion time must follow creation and not be in the future")
        else:
            raise ValueError("Unknown AUTOBOT request state")
    return data


def _write(root, relative, data, maximum=MAX_LEDGER_BYTES):
    records.safe(root, relative)
    content = json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    if len(content.encode("utf-8")) > maximum:
        raise ValueError("AUTOBOT record exceeds its bounded capacity; retain history and partition explicitly")
    memory.atomic_write(root, relative, content)


def _fresh(root, request):
    packet = context(root, request["identity"]["selected"])
    current = [{key: source[key] for key in ("path", "sha256", "bytes")} for source in packet["sources"]]
    return packet["policyHash"] == request["identity"]["policyHash"] and current == request["identity"]["files"]


def _public(root, request):
    current = _fresh(root, request)
    return {**request, "contextCurrent": current,
            "resultFresh": current and request["state"] == "complete",
            "inputRevisionNote": "Freshness also requires the caller to supply a truthful current input revision"}


def request(root, args):
    _active(root)
    def plan():
        identity, packet = _identity(root, args)
        data = load_requests(root)
        identifier = "ABR-" + records.fingerprint(identity)[:20]
        previous = next((entry for entry in data["requests"] if entry["id"] == identifier), None)
        if previous is not None and previous["identity"] != identity:
            raise ValueError("AUTOBOT request ID collides with different input facts; retain both inputs for review")
        item = previous or {"id": identifier, "createdAt": memory.now(), "identity": identity,
                            "state": "requested", "completion": None}
        return data, item, packet, previous is not None
    data, item, packet, reused = plan()
    if args.apply and not reused:
        with memory.coordination_lock(root):
            data, item, packet, reused = plan()
            if not reused:
                if len(data["requests"]) >= MAX_REQUESTS:
                    raise ValueError("AUTOBOT request capacity reached; retain and partition explicitly")
                data["requests"].append(item)
                _write(root, REQUESTS, data)
    return {"applied": args.apply, "reused": reused, "request": _public(root, item),
            "context": packet, "executed": False, "limit": LIMIT}


def complete(root, args):
    _active(root)
    records.token(args.id, "ABR")
    proposed = {"completedAt": memory.now(), "summary": args.summary,
                "responseRevision": args.response_revision, "evidence": args.evidence}
    _completion(proposed)
    def plan():
        data = load_requests(root)
        current = next((item for item in data["requests"] if item["id"] == args.id), None)
        if current is None:
            raise ValueError("Unknown AUTOBOT request in selected scope")
        if not _fresh(root, current):
            raise ValueError("AUTOBOT inputs or policy changed; retain the old request and create a new request")
        if current["completion"] is not None:
            if {**proposed, "completedAt": current["completion"]["completedAt"]} != current["completion"]:
                raise ValueError("AUTOBOT completion is immutable; conflicting completion must use a new input revision")
            return data, current, False
        if memory.timestamp(proposed["completedAt"]) < memory.timestamp(current["createdAt"]):
            raise ValueError("Local clock precedes the AUTOBOT request; correct the clock first")
        updated = {**current, "state": "complete", "completion": proposed}
        data["requests"][data["requests"].index(current)] = updated
        return data, updated, True
    data, item, changed = plan()
    if args.apply and changed:
        with memory.coordination_lock(root):
            data, item, changed = plan()
            if changed:
                _write(root, REQUESTS, data)
    return {"applied": args.apply, "changed": changed, "request": _public(root, item),
            "taskAccepted": False, "executed": False, "limit": LIMIT}


def initialize(root, defaults, apply=False):
    root, defaults = Path(root), Path(defaults)
    _, registry = memory.load(root)
    # Always seed from reviewed blank creation templates, never adopted root memory/branding.
    seeds = {}
    for name in SEEDS:
        text, _ = _text(defaults, "templates/autobot/" + name)
        seeds["AUTOBOT/" + name] = text
    validate_catalog(_json(defaults, "templates/autobot/CATALOG.json"))
    if _json(defaults, "templates/autobot/REQUESTS.json") != {"schemaVersion": 1, "requests": []}:
        raise ValueError("AUTOBOT creation template must have an empty request ledger")
    seeds["AGENTS/agent.a/MEMORY.md"] = _text(defaults, "templates/AGENT-A-MEMORY.md")[0]
    existing = {item["id"] for item in registry["agents"]}
    additions = [] if AGENT in existing else [AGENT]
    missing = [name for name in seeds if not records.safe(root, name).exists()]
    for name in seeds:
        if name not in missing:
            _text(root, name, MAX_LEDGER_BYTES if name == REQUESTS else MAX_FILE_BYTES)
    if records.safe(root, CATALOG).exists():
        validate_catalog(_json(root, CATALOG))
    if records.safe(root, REQUESTS).exists():
        load_requests(root)
    result = {"applied": apply, "register": additions, "add": missing,
              "preserve": [name for name in seeds if name not in missing], "scope": str(root),
              "runtimeStarted": False, "limit": LIMIT}
    if not apply or not (additions or missing):
        return result
    with memory.coordination_lock(root):
        planned = initialize(root, defaults)
        _, registry = memory.load(root)
        log = "logs/autobot/" + uuid.uuid4().hex + ".json"
        receipt = {"schemaVersion": 1, "operation": "autobot-init", "at": memory.now(),
                   "state": "started", "add": planned["add"], "register": planned["register"]}
        _write(root, log, receipt)
        try:
            for name in planned["add"]:
                records.safe(root, name)
                memory.atomic_write(root, name, seeds[name])
            if planned["register"]:
                registry["agents"].append({"id": AGENT, "role": ROLE, "memory": "AGENTS/agent.a/MEMORY.md"})
                _write(root, "AGENTS/REGISTRY.json", registry)
            receipt["state"] = "complete"
        except BaseException:
            receipt["state"] = "failed"
            raise
        finally:
            _write(root, log, receipt)
    return {**planned, "applied": True, "receipt": log}


def validate_optional(root):
    """Legacy scopes without AUTOBOT remain valid; activated or present records are complete."""
    _, registry = memory.load(root)
    active = any(item["id"] == AGENT for item in registry["agents"])
    present = records.safe(root, CATALOG).exists() or records.safe(root, REQUESTS).exists()
    # Also detect an incomplete subtree instead of silently ignoring it.
    directory = memory.managed(Path(root), "AUTOBOT")
    if not active and not present and not directory.exists():
        return
    for name in SEEDS:
        _text(root, "AUTOBOT/" + name, MAX_LEDGER_BYTES if name == "REQUESTS.json" else MAX_FILE_BYTES)
    validate_catalog(_json(root, CATALOG))
    data = load_requests(root)
    if data["requests"] and not active:
        raise ValueError("AUTOBOT request records require explicitly registered agent.a")
    if active:
        _text(root, "AGENTS/agent.a/MEMORY.md")


def validate_template(root, defaults):
    validate_optional(root)
    _, registry = memory.load(root)
    if any(item["id"] == AGENT for item in registry["agents"]):
        raise ValueError("The public AUTOBOT template must not register agent.a")
    for name in SEEDS:
        current, _ = _text(root, "AUTOBOT/" + name)
        expected, _ = _text(defaults, "templates/autobot/" + name)
        if current.replace("\r\n", "\n") != expected.replace("\r\n", "\n"):
            raise ValueError("AUTOBOT/" + name + " differs from its reviewed blank seed")
    if load_requests(root)["requests"]:
        raise ValueError("The public AUTOBOT request ledger must remain empty")


def add_cli(subparsers, scope=None):
    scope = scope or (lambda parser: parser)
    for name in ("autobot", "agent-a"):
        parent = subparsers.add_parser(name, help=__doc__)
        commands = parent.add_subparsers(dest="autobot_action", required=True)
        command = scope(commands.add_parser("init", help="preview blank tier-2 records and AGENTA registration"))
        command.add_argument("--apply", action="store_true")
        scope(commands.add_parser("list", help="list 10 specialist identities without loading their content"))
        command = scope(commands.add_parser("context", help="load only selected specialist files and AGENTA charter"))
        command.add_argument("--bot", action="append", required=True)
        command = scope(commands.add_parser("request", help="preview or retain a bounded request; no bot execution"))
        command.add_argument("--caller", choices=CALLERS, required=True)
        command.add_argument("--purpose", required=True)
        command.add_argument("--input-revision", required=True)
        command.add_argument("--task")
        command.add_argument("--bot", action="append", required=True)
        command.add_argument("--apply", action="store_true")
        command = scope(commands.add_parser("complete", help="retain an explicit response and original evidence references"))
        command.add_argument("id")
        command.add_argument("--summary", required=True)
        command.add_argument("--response-revision", required=True)
        command.add_argument("--evidence", action="append", required=True)
        command.add_argument("--apply", action="store_true")
        command = scope(commands.add_parser("status", help="inspect retained requests and selected-file freshness"))
        command.add_argument("id", nargs="?")


def dispatch(root, defaults, args):
    action = args.autobot_action
    if action == "init":
        result = initialize(root, defaults, args.apply)
    elif action == "list":
        result = {"catalog": validate_catalog(_json(root, CATALOG)), "executed": False, "limit": LIMIT}
    elif action == "context":
        result = context(root, args.bot)
    elif action == "request":
        result = request(root, args)
    elif action == "complete":
        result = complete(root, args)
    elif action == "status":
        validate_optional(root)
        data = load_requests(root)
        if args.id:
            records.token(args.id, "ABR")
            item = next((item for item in data["requests"] if item["id"] == args.id), None)
            if item is None:
                raise ValueError("Unknown AUTOBOT request in selected scope")
            result = {"request": _public(root, item), "executed": False, "limit": LIMIT}
        else:
            # A bounded summary does not dump all retained answers into every turn.
            summaries = [{"id": item["id"], "state": item["state"],
                          "inputRevision": item["identity"]["inputRevision"],
                          "selected": item["identity"]["selected"]} for item in data["requests"][-25:]]
            result = {"total": len(data["requests"]), "requests": summaries,
                      "truncated": len(data["requests"]) > 25, "freshnessChecked": False,
                      "executed": False, "limit": LIMIT}
    else:
        raise ValueError("Unknown AUTOBOT action")
    result.setdefault("scope", str(root))
    return result
