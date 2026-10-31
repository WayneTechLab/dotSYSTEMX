"""Optional ROOT planning references and observed harness/bot deltas; no external execution."""

from datetime import datetime, timezone
import json
from pathlib import Path
import re
import uuid

import project_memory as memory
import agent_standards as records


COMMANDS = {"root"}
PLAN = "ROOT/PLAN.json"
MIRRORS = "ROOT/MIRRORS.json"
SEEDS = ("SX-RULES.md", "SX-MILESTONE.md", "PLAN.json", "MIRRORS.json")
BLANK_PLAN = {"schemaVersion": 1, "requests": [], "nodes": []}
BLANK_MIRRORS = {"schemaVersion": 1, "bindings": [], "observations": [], "cards": []}
MAX_BYTES = 4 * 1024 * 1024
MAX_TEXT_BYTES = 64 * 1024
MAX_REFERENCES = 100
MAX_REQUESTS = 1000
MAX_NODES = 5000
MAX_BINDINGS = 2000
MAX_OBSERVATIONS = 10000
MAX_CARDS = 2000
MAX_PACKET_BYTES = 64 * 1024
MAX_OUTPUT_BYTES = 128 * 1024
MAX_ROSTER_ROWS = 5000
ROSTER_PAGE_LIMIT = 50
ROSTER_SETUP_COMMANDS = (
    "roles-init --help",
    "agent-1 setup --help",
    "autobot init --help",
    "agent-beta setup --help",
    "agent-beta bot-add --help",
    "agent-add --help",
    "agent-y providers",
    "service status",
    "service start --help",
    "onboard status",
    "onboard plan --help",
    "onboard bridge --help",
    "agent-y prepare --help",
    "agenda init --help",
    "agenda decision-add --help",
)
# Host toolchains are navigation targets, not actors or Agent Y providers.
# Every host must opt into the portable CLI or JSON-lines subprocess itself.
TOOLCHAIN_OPTIONS = ("vscode", "codex", "cursor", "kiro", "jetbrains")
KINDS = ("milestone", "wave", "phase", "group", "task", "subtask", "action")
STATES = ("pending", "running", "blocked", "completed", "cancelled", "unknown", "unavailable")
REQUIRED = ("scripts/root_coordination.py", "tests/test_root_coordination.py") + tuple(
    prefix + name for prefix in ("ROOT/", "templates/root/") for name in SEEDS)
LIMIT = ("Local reference records and attested observations only. No harness/cloud connector, "
         "tool execution, scheduler, automatic synchronization, identity authentication, or task acceptance.")


def _text(value, label, maximum=2048, empty=False):
    memory.string(value, label, nonempty=not empty)
    if len(value.encode("utf-8")) > maximum:
        raise ValueError(label + " exceeds its bounded text limit")
    if any(ord(character) < 32 and character not in "\n\t" for character in value):
        raise ValueError(label + " contains an unsupported control character")


def _list(value, label, maximum=MAX_REFERENCES, required=False):
    memory.strings(value, label, nonempty=required)
    if len(value) > maximum or len(value) != len(set(value)):
        raise ValueError(label + " contains too many or duplicate references")
    for item in value:
        _text(item, label + " entry")


def _schema(value, keys, label):
    memory.fields(value, ("schemaVersion", *keys), label)
    if type(value["schemaVersion"]) is not int or value["schemaVersion"] != 1:
        raise ValueError(label + " schemaVersion must be the integer 1")


def _rows(value, label, maximum):
    if not isinstance(value, list) or len(value) > maximum:
        raise ValueError(label + " must be a bounded list")


def _read(root, relative):
    path = records.safe(root, relative)
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ValueError("Missing or oversized ROOT record (maximum 4 MiB): " + relative)
    with path.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("Oversized ROOT record (maximum 4 MiB): " + relative)

    def unique(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError("Duplicate JSON field in ROOT record: " + key)
            value[key] = item
        return value

    def invalid(value):
        raise ValueError("Non-finite JSON number in ROOT record: " + value)

    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=unique, parse_constant=invalid)
    except RecursionError as error:
        raise ValueError("ROOT JSON nesting exceeds the supported parser limit") from error


def _read_text(root, relative):
    path = records.safe(root, relative)
    if not path.is_file() or path.stat().st_size > MAX_TEXT_BYTES:
        raise ValueError("Missing or oversized ROOT guide (maximum 64 KiB): " + relative)
    with path.open("rb") as stream:
        raw = stream.read(MAX_TEXT_BYTES + 1)
    if len(raw) > MAX_TEXT_BYTES:
        raise ValueError("Oversized ROOT guide (maximum 64 KiB): " + relative)
    return raw.decode("utf-8")


def _write(root, relative, value):
    if len((records.encoded(value) + "\n").encode("utf-8")) > MAX_BYTES:
        raise ValueError("ROOT record exceeds 4 MiB; explicitly retain and partition records")
    # Check the exact indented representation before replacing the old record.
    encoded = json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    if len(encoded.encode("utf-8")) > MAX_BYTES:
        raise ValueError("ROOT record exceeds 4 MiB; explicitly retain and partition records")
    records.safe(root, relative)
    memory.atomic_write(Path(root), relative, encoded)


def _public(root, result, packet=False):
    """Check the exact final CLI response before a candidate can mutate records."""
    result = dict(result)
    result.setdefault("scope", str(root))
    result["executed"] = False
    result["limit"] = LIMIT
    # Both root and project-scoped launchers print this representation followed
    # by one newline. Compact JSON understates indented collections and UTF-8.
    serialized = json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    maximum = MAX_PACKET_BYTES if packet else MAX_OUTPUT_BYTES
    if len(serialized.encode("utf-8")) > maximum:
        if packet:
            raise ValueError("ROOT packet exceeds 64 KiB; select fewer TASK IDs or retain large evidence behind references")
        raise ValueError("ROOT output exceeds 128 KiB; request a smaller selected task set")
    return result


def roster(root):
    """Derive Agent 0's local roster from validated records, without probing providers."""
    import agenda_access
    import agent_beta
    import agent_y
    import autobots

    root = Path(root)
    ledger, registry = memory.load(root)
    registered = {item["id"]: item for item in registry["agents"]}
    autobots.validate_optional(root)
    agent_beta.validate_optional(root)
    _, access = agenda_access._load(root)
    access = access or {"schemaVersion": 1, "decisions": []}
    catalog_path = records.safe(root, autobots.CATALOG)
    catalog = autobots.validate_catalog(records.read(root, autobots.CATALOG)) if catalog_path.is_file() else None
    bot_path = records.safe(root, agent_beta.INDEX)
    bots = agent_beta.load_bots(root) if bot_path.is_file() else {"schemaVersion": 1, "bots": []}
    job_path = records.safe(root, agent_y.JOBS)
    if "agent.y" in registered and not job_path.is_file():
        raise ValueError("Registered Agent Y is missing its selected-scope job ledger")
    jobs = agent_y.load_jobs(root)["jobs"] if job_path.is_file() else []
    task_counts = {}
    for task in ledger["tasks"]:
        task_counts[task["owner"]] = task_counts.get(task["owner"], 0) + 1

    decisions = [{key: item[key] for key in ("id", "actor", "resource", "action", "environment", "decision")}
                 for item in access["decisions"]]
    decisions.sort(key=lambda item: (int(item["id"].split("-", 1)[1]), item["id"]))
    by_actor = {}
    for decision in decisions:
        by_actor.setdefault(decision["actor"], []).append(decision)

    def row(actor, kind, name, state, source, workspace="", provider="", tasks=0,
            access_actor=None):
        matches = by_actor.get(access_actor or actor, [])
        return {"actorId": actor, "kind": kind, "displayName": name,
                "registrationState": state, "sourceRecord": source,
                "workspace": workspace, "providerAlias": provider,
                "taskCount": tasks,
                "accessDecisionIds": [item["id"] for item in matches],
                "reviewedIntentCount": sum(item["decision"] == "reviewed-intent" for item in matches),
                "deniedCount": sum(item["decision"] == "denied" for item in matches),
                "gapCount": sum(item["decision"] == "gap" for item in matches),
                "externalRightsVerified": False}

    rows = []
    role_defaults = access.get("roleDefaults", list(agenda_access.ROLE_DEFAULTS))
    catalog_names = {item["id"]: item["name"] for item in catalog["bots"]} if catalog else {}
    for role in role_defaults:
        actor, kind = role["actor"], role["kind"]
        if kind == "agent":
            state = "registered" if actor in registered else "unregistered"
            source = "AGENTS/REGISTRY.json" if actor in registered else agenda_access.ACCESS
            workspace = "AGENTS/" + actor
        elif kind == "autobot":
            state = "available-reference" if "agent.a" in registered else "catalog-only"
            source = autobots.CATALOG if catalog else agenda_access.ACCESS
            workspace = next((item["file"] for item in catalog["bots"] if item["id"] == actor), "") if catalog else ""
        else:
            state, source, workspace = "pattern-only", agenda_access.ACCESS, ""
        rows.append(row(actor, kind, catalog_names.get(actor, actor), state, source,
                        workspace, tasks=task_counts.get(actor, 0)))

    standard_ids = {item["actor"] for item in role_defaults}
    for item in sorted(registry["agents"], key=lambda agent: agent["id"]):
        if item["id"] not in standard_ids:
            rows.append(row(item["id"], "agent", item["role"], "registered",
                            "AGENTS/REGISTRY.json", "AGENTS/" + item["id"],
                            tasks=task_counts.get(item["id"], 0)))
    for item in sorted(bots["bots"], key=lambda bot: bot["name"]):
        metadata = agent_beta._json(root, item["path"] + "/BOT.json")
        rows.append(row("agentb:" + item["name"], item["kind"], item["name"],
                        "registered-offline", agent_beta.INDEX, item["path"],
                        metadata["provider"], len(metadata["taskIds"])))
    known_actors = {item["actorId"] for item in rows}
    for actor in sorted(by_actor):
        if actor in known_actors:
            continue
        if re.fullmatch(r"native-subagent:[a-z][a-z0-9-]{0,31}:[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", actor):
            rows.append(row(actor, "native-subagent", actor, "decision-only",
                            agenda_access.ACCESS))
            continue
        # An older or manually authored decision may name a human or service.
        # Show its recorded intent without inventing registration or a runtime.
        rows.append(row(actor, "access-actor", actor, "decision-only",
                        agenda_access.ACCESS))
    for job in sorted(jobs, key=lambda item: item["id"]):
        rows.append(row("agent-y-job:" + job["id"], "cli-channel", job["id"],
                        "recorded-" + job["state"], agent_y.JOBS, provider=job["provider"], tasks=1))
    if len(rows) > MAX_ROSTER_ROWS:
        raise ValueError("Agent 0 roster exceeds its 5000-row view limit")
    return {"rows": rows, "decisions": decisions,
            "counts": {"standardRoles": len(role_defaults), "registeredAgents": len(registered),
                       "registeredBots": len(bots["bots"]), "cliChannels": len(jobs),
                       "accessDecisions": len(decisions), "rows": len(rows)},
            "cliProviderOptions": ["codex", "copilot", "muse", "configured"],
            "toolchainOptions": list(TOOLCHAIN_OPTIONS),
            "portableIO": "selected-scope-cli-json-and-stdio-json-lines",
            "nativeHostBindingsInstalled": False,
            "setupCommands": list(ROSTER_SETUP_COMMANDS),
            "sourceRevision": records.fingerprint({"rows": rows, "decisions": decisions}),
            "identityVerified": False, "accessGranted": False, "runtimeStarted": False}


def _token(value, prefix):
    return records.token(value, prefix)


def _request_id(value):
    if not isinstance(value, str) or not re.fullmatch(r"(?:RT|ST)-[a-f0-9]{20}", value):
        raise ValueError("Invalid ROOT request ID")


def _id(prefix, key):
    _text(key, "Retry key", 128)
    return prefix + "-" + records.fingerprint({"key": key})[:20]


def _at(value, label, upper=None):
    parsed = memory.timestamp(value)
    if parsed > (upper or datetime.now(timezone.utc)):
        raise ValueError(label + " cannot be in the future")
    return parsed


def _tasks(root):
    ledger, _ = memory.load(root)
    return {item["id"]: item for item in ledger["tasks"]}


def _task_refs(values, tasks, required=False):
    _list(values, "Task references", required=required)
    if any(value not in tasks for value in values):
        raise ValueError("ROOT task references must exist in the selected scope")


def _unique(items, prefix, label):
    indexed, keys = {}, set()
    for item in items:
        if not isinstance(item, dict) or "id" not in item or "key" not in item:
            raise ValueError(label + " needs an ID and retry key")
        _token(item["id"], prefix)
        _text(item["key"], label + " retry key", 128)
        if item["id"] != _id(prefix, item["key"]):
            raise ValueError(label + " ID does not match its retry key")
        if item["id"] in indexed or item["key"] in keys:
            raise ValueError(label + " IDs and retry keys must be unique")
        indexed[item["id"]] = item
        keys.add(item["key"])
    return indexed


def validate_plan(root, data, tasks=None):
    _schema(data, ("requests", "nodes"), "ROOT plan")
    _rows(data["requests"], "ROOT requests", MAX_REQUESTS)
    _rows(data["nodes"], "ROOT planning nodes", MAX_NODES)
    tasks = _tasks(root) if tasks is None else tasks
    requests, keys = {}, set()
    upper = datetime.now(timezone.utc)
    for item in data["requests"]:
        memory.fields(item, ("id", "key", "kind", "title", "sourceRef", "parent", "createdAt"), "ROOT request")
        if item["kind"] not in ("rtask", "stask"):
            raise ValueError("ROOT request kind must be rtask or stask")
        prefix = "RT" if item["kind"] == "rtask" else "ST"
        _token(item["id"], prefix)
        if item["id"] != _id(prefix, item["key"]) or item["id"] in requests or item["key"] in keys:
            raise ValueError("ROOT request IDs and retry keys must be unique and match")
        _text(item["title"], "Request title", 512)
        _text(item["sourceRef"], "Request source reference")
        _text(item["parent"], "Request parent", 64, empty=True)
        _at(item["createdAt"], "Request creation", upper)
        requests[item["id"]] = item
        keys.add(item["key"])
    for item in requests.values():
        if item["kind"] == "rtask" and item["parent"]:
            raise ValueError("RTask is an originating request and cannot have a request parent")
        if item["kind"] == "stask":
            if item["parent"] not in requests or item["parent"] == item["id"]:
                raise ValueError("STask must reference an existing distinct RTask/STask parent")
            if memory.timestamp(requests[item["parent"]]["createdAt"]) > memory.timestamp(item["createdAt"]):
                raise ValueError("STask cannot precede its parent request")
    # Iterative traversal handles long imported request chains without recursion.
    for identifier in requests:
        seen, current = set(), identifier
        while current:
            if current in seen:
                raise ValueError("ROOT request hierarchy contains a cycle")
            seen.add(current)
            current = requests[current]["parent"]
    nodes = _unique(data["nodes"], "NODE", "Planning node")
    known_milestones = memory.milestones(root)
    for item in nodes.values():
        memory.fields(item, ("id", "key", "kind", "title", "request", "parent", "milestone", "taskIds", "createdAt"), "Planning node")
        if item["kind"] not in KINDS:
            raise ValueError("Unknown ROOT planning node kind")
        _text(item["title"], "Planning node title", 512)
        _request_id(item["request"])
        if item["request"] not in requests:
            raise ValueError("Planning node request must exist in the selected scope")
        _text(item["parent"], "Planning node parent", 64, empty=True)
        _text(item["milestone"], "Milestone reference", 64, empty=True)
        if item["milestone"] and item["milestone"] not in known_milestones:
            raise ValueError("ROOT milestone must already be declared in PLAN/MASTER-PLAN.md")
        if item["kind"] == "milestone" and not item["milestone"]:
            raise ValueError("A milestone node needs an existing M-ID")
        _task_refs(item["taskIds"], tasks)
        _at(item["createdAt"], "Planning node creation", upper)
    # Validate every node shape before inspecting imported parent fields.
    for item in nodes.values():
        if item["parent"]:
            parent = nodes.get(item["parent"])
            if parent is None or KINDS.index(parent["kind"]) >= KINDS.index(item["kind"]):
                raise ValueError("Planning parents must precede their child kind; skip optional levels, never cycle")
            if memory.timestamp(parent["createdAt"]) > memory.timestamp(item["createdAt"]):
                raise ValueError("Planning node cannot precede its parent")
    for item in nodes.values():
        current, milestone = item, ""
        while current:
            if current["milestone"]:
                if milestone and milestone != current["milestone"]:
                    raise ValueError("Planning ancestors cannot disagree on milestone identity")
                milestone = current["milestone"]
            current = nodes[current["parent"]] if current["parent"] else None
        if milestone and any(tasks[identifier]["milestone"] != milestone for identifier in item["taskIds"]):
            raise ValueError("Planning task milestone disagrees with its canonical TASK record")
    return data


def validate_mirrors(root, data, plan, tasks=None):
    _schema(data, ("bindings", "observations", "cards"), "ROOT mirrors")
    for name, maximum in (("bindings", MAX_BINDINGS), ("observations", MAX_OBSERVATIONS), ("cards", MAX_CARDS)):
        _rows(data[name], "ROOT " + name, maximum)
    tasks = _tasks(root) if tasks is None else tasks
    requests = {item["id"] for item in plan["requests"]}
    bindings = _unique(data["bindings"], "BIND", "Mirror binding")
    upper = datetime.now(timezone.utc)
    superseded, identities = set(), {}
    for item in bindings.values():
        memory.fields(item, ("id", "key", "layer", "channel", "item", "taskIds", "supersedes", "createdAt"), "Mirror binding")
        if item["layer"] not in ("harness", "bot"):
            raise ValueError("Mirror layer must be harness or bot")
        _text(item["channel"], "Mirror channel", 128)
        _text(item["item"], "External item identity", 512)
        _task_refs(item["taskIds"], tasks, required=True)
        _text(item["supersedes"], "Superseded binding", 64, empty=True)
        _at(item["createdAt"], "Mirror binding creation", upper)
    # Inspect supersession only after every imported binding has a valid shape.
    for item in bindings.values():
        created = memory.timestamp(item["createdAt"])
        if item["supersedes"]:
            previous = bindings.get(item["supersedes"])
            if previous is None or previous["id"] == item["id"] or previous["id"] in superseded:
                raise ValueError("Binding supersession must name one existing unsuperseded binding")
            if any(previous[key] != item[key] for key in ("layer", "channel")):
                raise ValueError("A corrected binding must retain its layer and channel")
            if previous["item"] != item["item"] and set(previous["taskIds"]) != set(item["taskIds"]):
                raise ValueError("Replacing an external attempt must retain its canonical TASK set")
            if memory.timestamp(previous["createdAt"]) > created:
                raise ValueError("A corrected binding cannot precede its predecessor")
            superseded.add(previous["id"])
    # A separate acyclic pass rejects imported equal-time supersession cycles.
    for identifier in bindings:
        current, seen = identifier, set()
        while current:
            if current in seen:
                raise ValueError("Mirror binding supersession contains a cycle")
            seen.add(current)
            current = bindings[current]["supersedes"]
    for item in bindings.values():
        if item["id"] in superseded:
            continue
        identity = (item["layer"], item["channel"], item["item"])
        if identity in identities:
            raise ValueError("An external item needs one active binding; explicitly supersede a corrected mapping")
        identities[identity] = item["id"]
    observations = _unique(data["observations"], "OBS", "Mirror observation")
    previous_recorded = None
    for item in observations.values():
        memory.fields(item, ("id", "key", "binding", "rawState", "state", "sourceRevision", "expectedRevision",
                            "evidence", "at", "recordedAt", "canonicalTaskFingerprints"), "Mirror observation")
        _token(item["binding"], "BIND")
        binding = bindings.get(item["binding"])
        if binding is None:
            raise ValueError("Observation binding must exist in the selected scope")
        _text(item["rawState"], "Raw observed state", 512)
        if item["state"] not in STATES:
            raise ValueError("Unknown normalized execution state")
        _text(item["sourceRevision"], "Observed source revision", 512)
        _text(item["expectedRevision"], "Expected source revision", 512, empty=True)
        _list(item["evidence"], "Observation evidence", required=True)
        recorded = _at(item["recordedAt"], "Observation recording", upper)
        _at(item["at"], "Observed occurrence", recorded)
        if recorded < memory.timestamp(binding["createdAt"]):
            raise ValueError("Observation recording cannot precede its binding")
        if previous_recorded is not None and recorded < previous_recorded:
            raise ValueError("Observation recording history must remain chronological")
        previous_recorded = recorded
        hashes = item["canonicalTaskFingerprints"]
        if not isinstance(hashes, dict) or set(hashes) != set(binding["taskIds"]):
            raise ValueError("Observation must capture every bound canonical TASK fingerprint")
        if any(not isinstance(value, str) or not re.fullmatch(r"[a-f0-9]{64}", value) for value in hashes.values()):
            raise ValueError("Invalid canonical TASK fingerprint")
    cards = _unique(data["cards"], "CARD", "Tool card")
    for item in cards.values():
        memory.fields(item, ("id", "key", "request", "taskIds", "provider", "tool", "purpose", "inputRevision",
                            "expectedEvidence", "permissionBoundary", "stopCondition", "createdAt"), "Tool card")
        _text(item["request"], "Tool card request", 64, empty=True)
        if item["request"] and item["request"] not in requests:
            raise ValueError("Tool card request must exist in the selected scope")
        _task_refs(item["taskIds"], tasks, required=True)
        for key in ("provider", "tool", "purpose", "inputRevision", "permissionBoundary", "stopCondition"):
            _text(item[key], "Tool card " + key)
        _list(item["expectedEvidence"], "Expected tool evidence", required=True)
        _at(item["createdAt"], "Tool card creation", upper)
    return data


def load(root):
    tasks = _tasks(root)
    plan = validate_plan(root, _read(root, PLAN), tasks)
    mirrors = validate_mirrors(root, _read(root, MIRRORS), plan, tasks)
    return plan, mirrors, tasks


def validate_optional(root):
    # Check the exact path even on a case-insensitive host before treating ROOT as absent.
    path = records.safe(root, PLAN)
    directory = memory.managed(Path(root), "ROOT")
    if not directory.exists() and not path.exists():
        return
    for name in SEEDS[:2]:
        _read_text(root, "ROOT/" + name)
    load(root)


def validate_template(root, defaults):
    validate_optional(root)
    if _read(root, PLAN) != BLANK_PLAN or _read(root, MIRRORS) != BLANK_MIRRORS:
        raise ValueError("Public ROOT planning and mirror records must remain blank")
    for name, blank in (("PLAN.json", BLANK_PLAN), ("MIRRORS.json", BLANK_MIRRORS)):
        if _read(defaults, "templates/root/" + name) != blank:
            raise ValueError("ROOT creation JSON seeds must remain blank")
    for name in SEEDS[:2]:
        current = _read_text(root, "ROOT/" + name).replace("\r\n", "\n")
        seed = _read_text(defaults, "templates/root/" + name).replace("\r\n", "\n")
        if current != seed:
            raise ValueError("ROOT/" + name + " differs from its reviewed creation seed")


def initialize(root, defaults, apply=False):
    root, defaults = Path(root), Path(defaults)
    _tasks(root)
    seeds = {"ROOT/" + name: _read_text(defaults, "templates/root/" + name) for name in SEEDS}
    for name, blank in (("PLAN.json", BLANK_PLAN), ("MIRRORS.json", BLANK_MIRRORS)):
        if _read(defaults, "templates/root/" + name) != blank:
            raise ValueError("ROOT initialization requires dedicated blank JSON seeds")
    missing = [name for name in seeds if not records.safe(root, name).exists()]
    # Validate partial existing JSONs and references with blank counterparts;
    # this permits repair by adding missing scaffolds without replacing private data.
    plan = _read(root, PLAN) if PLAN not in missing else BLANK_PLAN
    mirrors = _read(root, MIRRORS) if MIRRORS not in missing else BLANK_MIRRORS
    tasks = _tasks(root)
    validate_plan(root, plan, tasks)
    validate_mirrors(root, mirrors, plan, tasks)
    for name in seeds:
        if name not in missing:
            if name.endswith(".md"):
                _read_text(root, name)
            else:
                _read(root, name)
    result = {"applied": apply, "add": missing, "preserve": [name for name in seeds if name not in missing],
              "runtimeStarted": False}
    if not apply or not missing:
        return result
    with memory.coordination_lock(root):
        planned = initialize(root, defaults)
        log = "logs/root/" + uuid.uuid4().hex + ".json"
        # Include the eventual receipt path in the final response before the
        # first log or scaffold write; an output rejection must not install it.
        response = _public(root, {**planned, "applied": True, "receipt": log})
        receipt = {"schemaVersion": 1, "operation": "root-init", "at": memory.now(),
                   "state": "started", "add": planned["add"]}
        _write(root, log, receipt)
        try:
            for name in planned["add"]:
                records.safe(root, name)
                memory.atomic_write(root, name, seeds[name])
            receipt["state"] = "complete"
        except BaseException:
            receipt["state"] = "failed"
            raise
        finally:
            _write(root, log, receipt)
    return response


def _append(root, document, collection, prefix, key, identity, maximum, apply, build=None, response_fields=None):
    identifier = _id(prefix, key)

    def plan_write():
        plan, mirrors, tasks = load(root)
        data = plan if document == PLAN else mirrors
        previous = next((item for item in data[collection] if item["key"] == key), None)
        if previous is not None:
            # Retry identity excludes local recording timestamps/fingerprints,
            # preserving the original evidence instead of laundering freshness.
            if any(previous.get(name) != value for name, value in identity.items()):
                raise ValueError("Retry key already records different facts; retain history and use a new key")
            return data, previous, True
        if len(data[collection]) >= maximum:
            raise ValueError("ROOT " + collection + " capacity reached; explicitly retain and partition history")
        extra = build(tasks) if build else {"createdAt": memory.now()}
        item = {"id": identifier, "key": key, **identity, **extra}
        data[collection].append(item)
        validate_plan(root, plan, tasks)
        validate_mirrors(root, mirrors, plan, tasks)
        return data, item, False

    def response(item, reused):
        return _public(root, {"applied": apply, "reused": reused, "record": item, "taskAccepted": False,
                              **(response_fields or {})})

    data, item, reused = plan_write()
    result = response(item, reused)
    if apply and not reused:
        with memory.coordination_lock(root):
            data, item, reused = plan_write()
            # Recompute and check the complete public response under the scope
            # lock, before replacing the old ledger with this fresh candidate.
            result = response(item, reused)
            if not reused:
                _write(root, document, data)
    return result


def _active_bindings(mirrors):
    superseded = {item["supersedes"] for item in mirrors["bindings"] if item["supersedes"]}
    return [item for item in mirrors["bindings"] if item["id"] not in superseded]


def _limit(value, maximum=100):
    if type(value) is not int or not 1 <= value <= maximum:
        raise ValueError("Output limit must be 1 to " + str(maximum))
    return value


def _expected_states(binding, tasks):
    """Project a whole external item, not each TASK it happens to summarize."""
    states = [tasks[identifier]["status"] for identifier in binding["taskIds"]]
    remaining = [state for state in states if state != "cancelled"]
    if not remaining:
        return ["cancelled"]
    if all(state in ("done", "needs_review") for state in remaining):
        return ["completed"]
    if "blocked" in remaining:
        return ["blocked", "running"] if "in_progress" in remaining else ["blocked"]
    if "in_progress" in remaining or any(state in ("done", "needs_review") for state in remaining):
        return ["running"]
    return ["pending"]


def delta(root, selected=None, max_age_seconds=None, limit=10, layers=None):
    plan, mirrors, tasks = load(root)
    _limit(limit)
    layers = ["harness"] if layers is None else layers
    if not isinstance(layers, list) or not layers or len(layers) != len(set(layers)) or any(
            layer not in ("harness", "bot") for layer in layers):
        raise ValueError("Select distinct harness and/or bot layers")
    requested_layers = layers
    selection = "explicit"
    if selected is None:
        focus = memory.load_focus(root, {"schemaVersion": 1, "tasks": list(tasks.values())})
        candidates = focus["taskIds"]
        selection = "focus"
        if not candidates:
            candidates = [identifier for identifier, task in tasks.items() if task["status"] not in ("done", "cancelled")]
            candidates += [identifier for identifier, task in tasks.items() if task["status"] in ("done", "cancelled")]
            selection = "active-first"
    else:
        candidates = selected
    if selected is not None:
        _task_refs(selected, tasks)
    selected = candidates[:limit]
    _task_refs(selected, tasks)
    if max_age_seconds is not None and (type(max_age_seconds) is not int or not 1 <= max_age_seconds <= 31536000):
        raise ValueError("Observation max age must be 1 to 31536000 seconds")
    latest = {}
    for observation in mirrors["observations"]:
        previous = latest.get(observation["binding"])
        ordering = (memory.timestamp(observation["at"]), memory.timestamp(observation["recordedAt"]), observation["id"])
        if previous is None or ordering > (memory.timestamp(previous["at"]), memory.timestamp(previous["recordedAt"]), previous["id"]):
            latest[observation["binding"]] = observation
    active = _active_bindings(mirrors)
    result = []
    now = datetime.now(timezone.utc)
    for identifier in selected:
        task = tasks[identifier]
        layers = {}
        for layer in ("harness", "bot"):
            if layer not in requested_layers:
                layers[layer] = {"assessment": "not_assessed", "issues": [], "bindings": []}
                continue
            bindings = [item for item in active if item["layer"] == layer and identifier in item["taskIds"]]
            entries = []
            if not bindings:
                layers[layer] = {"assessment": "recorded_only", "issues": ["unmapped"], "bindings": []}
                continue
            for binding in bindings[:10]:
                observed = latest.get(binding["id"])
                issues = []
                expected = _expected_states(binding, tasks)
                stale_tasks = []
                if observed is None:
                    issues.append("unavailable")
                else:
                    if observed["state"] in ("unknown", "unavailable"):
                        issues.append(observed["state"])
                    elif observed["state"] not in expected:
                        issues.append("state_difference")
                    stale_tasks = [value for value in binding["taskIds"]
                                   if observed["canonicalTaskFingerprints"][value] != records.fingerprint(tasks[value])]
                    if stale_tasks:
                        issues.append("stale_canonical")
                    if max_age_seconds is not None and (now - memory.timestamp(observed["at"])).total_seconds() > max_age_seconds:
                        issues.append("stale_observation")
                    if not observed["expectedRevision"]:
                        issues.append("revision_unverified")
                    elif observed["sourceRevision"] != observed["expectedRevision"]:
                        issues.append("revision_difference")
                entries.append({"binding": binding["id"], "channel": binding["channel"], "item": binding["item"],
                                "observation": observed["id"] if observed else None,
                                "state": observed["state"] if observed else "unavailable", "issues": issues,
                                "coveredTaskIds": binding["taskIds"], "expectedStates": expected,
                                "staleTaskIds": stale_tasks})
            layer_issues = {issue for item in entries for issue in item["issues"]}
            if len(bindings) > len(entries):
                layer_issues.add("truncated_bindings")
            layers[layer] = {"assessment": "recorded_only", "issues": sorted(layer_issues), "bindings": entries,
                             "totalBindings": len(bindings), "truncated": len(bindings) > len(entries)}
        issues = sorted({issue for layer in layers.values() for issue in layer["issues"]})
        result.append({"task": identifier, "canonicalStatus": task["status"],
                       "canonicalFingerprint": records.fingerprint(task), "layers": layers, "issues": issues,
                       "recordedObservationsAligned": not issues, "accepted": task["status"] == "done"})
    return {"tasks": result, "total": len(candidates), "returned": len(result), "truncated": len(candidates) > len(result),
        "selection": selection, "totalCanonicalTasks": len(tasks), "requestedLayers": requested_layers,
        "coverageComplete": len(candidates) == len(result),
        "recordedObservationsAligned": bool(result) and len(candidates) == len(result) and all(
        item["recordedObservationsAligned"] for item in result), "liveSyncVerified": False,
        "revisionNote": "Source/expected revisions are caller-supplied claims, not fetched or authenticated.",
        "freshnessNote": "Fingerprints capture canonical TASK records at recording time; retries preserve original observations.",
        "acceptanceNote": "Provider completed/exit zero never changes canonical TASK acceptance.",
        "projectionNote": "Each external item is compared with all TASKs it maps, including unselected members. Explicit supersession excludes retained older attempts only from current assessment.",
        "maxAgeSeconds": max_age_seconds, "taskAccepted": False}


def _progress(plan, tasks):
    nodes = {item["id"]: item for item in plan["nodes"]}
    milestone_tasks = {}
    for identifier, task in tasks.items():
        milestone_tasks.setdefault(task["milestone"], set()).add(identifier)
    inherited = {identifier: set() for identifier in nodes}
    for item in plan["nodes"]:
        current = item
        while current:
            inherited[current["id"]].update(item["taskIds"])
            current = nodes[current["parent"]] if current["parent"] else None
    milestones = []
    for item in plan["nodes"]:
        if item["kind"] != "milestone":
            continue
        # MASTER-PLAN milestone identities and canonical task assignments remain
        # authoritative even if an outline has not referenced every TASK yet.
        identifiers = milestone_tasks.get(item["milestone"], set()) | inherited[item["id"]]
        counts = {state: sum(tasks[identifier]["status"] == state for identifier in identifiers) for state in memory.VIEWS}
        milestones.append({"node": item["id"], "milestone": item["milestone"], "totalTasks": len(identifiers),
                           "taskCounts": counts, "allLinkedTasksAccepted": bool(identifiers) and counts["done"] == len(identifiers),
                           "milestoneAcceptanceEstablished": False})
    return {"milestones": milestones[:25], "totalMilestones": len(milestones), "truncated": len(milestones) > 25,
            "limit": "Derived canonical task progress; task completion alone does not accept a milestone outcome."}


def packet(root, selected=None, limit=10):
    _limit(limit, 10)
    plan, mirrors, tasks = load(root)
    if selected is None:
        ledger = {"schemaVersion": 1, "tasks": list(tasks.values())}
        focus = memory.load_focus(root, ledger)
        candidates = focus["taskIds"] or [identifier for identifier, item in tasks.items() if item["status"] not in ("done", "cancelled")]
    else:
        _task_refs(selected, tasks)
        candidates = selected
    chosen = candidates[:limit]
    nodes = {item["id"]: item for item in plan["nodes"]}
    node_ids = {item["id"] for item in plan["nodes"] if set(item["taskIds"]) & set(chosen)}
    for identifier in list(node_ids):
        current = nodes[identifier]
        while current["parent"]:
            node_ids.add(current["parent"])
            current = nodes[current["parent"]]
    selected_nodes = sorted((nodes[identifier] for identifier in node_ids),
                            key=lambda item: (KINDS.index(item["kind"]), item["createdAt"], item["id"]))
    cards = [item for item in mirrors["cards"] if set(item["taskIds"]) & set(chosen)]
    requests = {item["id"]: item for item in plan["requests"]}
    request_ids = {item["request"] for item in selected_nodes} | {item["request"] for item in cards if item["request"]}
    depths = {}
    for identifier in list(request_ids):
        current, lineage = requests[identifier], []
        while current:
            request_ids.add(current["id"])
            lineage.append(current["id"])
            current = requests[current["parent"]] if current["parent"] else None
        for depth, value in enumerate(reversed(lineage)):
            depths[value] = depth
    selected_requests = sorted((requests[identifier] for identifier in request_ids),
                               key=lambda item: (depths[item["id"]], item["createdAt"], item["id"]))
    result = {"tasks": [tasks[identifier] for identifier in chosen], "totalCandidates": len(candidates),
              "truncated": len(chosen) < len(candidates), "nodes": selected_nodes[:20],
              "nodesTruncated": len(selected_nodes) > 20,
              "totalNodes": len(selected_nodes), "requests": selected_requests[:10],
              "totalRequests": len(selected_requests), "requestsTruncated": len(selected_requests) > 10,
              "cards": cards[:10], "totalCards": len(cards), "cardsTruncated": len(cards) > 10,
              "statusAuthority": "WORK/TASKS.json", "taskAccepted": False,
              "packetNote": "Selected canonical work and reference contracts only; no remote observation or tool execution."}
    return _public(root, result, packet=True)


def add_cli(subparsers, scope=None):
    scope = scope or (lambda parser: parser)
    parent = subparsers.add_parser("root", help=__doc__)
    commands = parent.add_subparsers(dest="root_action", required=True)
    command = scope(commands.add_parser("init", help="preview missing blank ROOT references; no runtime"))
    command.add_argument("--apply", action="store_true")
    scope(commands.add_parser("status", help="bounded counts and observed-record limits"))
    command = scope(commands.add_parser("roster", help="read-only Agent 0 agent, BOT, AUTOBOT, and CLI channel view"))
    command.add_argument("--actor", default="", help="show one exact actor or recorded CLI channel ID")
    command.add_argument("--offset", type=int, default=0, help="first roster row (default: 0)")
    command.add_argument("--limit", type=int, default=ROSTER_PAGE_LIMIT,
                         help="roster rows per page (1-50)")
    command.add_argument("--decision-offset", type=int, default=0,
                         help="first scoped access decision (default: 0)")
    command.add_argument("--decision-limit", type=int, default=ROSTER_PAGE_LIMIT,
                         help="scoped access decisions per page (1-50)")
    command = scope(commands.add_parser("packet", help="bounded selected work packet, maximum 10 tasks and 64 KiB"))
    command.add_argument("--task", action="append")
    command.add_argument("--limit", type=int, default=10)
    command = scope(commands.add_parser("request", help="retain an originating RTask or delegated STask reference"))
    command.add_argument("--key", required=True)
    command.add_argument("--kind", choices=("rtask", "stask"), required=True)
    command.add_argument("--title", required=True)
    command.add_argument("--source-ref", required=True)
    command.add_argument("--parent", default="")
    command.add_argument("--apply", action="store_true")
    command = scope(commands.add_parser("node", help="retain hierarchy references; no duplicate TASK statuses"))
    command.add_argument("--key", required=True)
    command.add_argument("--kind", choices=KINDS, required=True)
    command.add_argument("--title", required=True)
    command.add_argument("--request", required=True)
    command.add_argument("--parent", default="")
    command.add_argument("--milestone", default="")
    command.add_argument("--task", action="append", default=[])
    command.add_argument("--apply", action="store_true")
    command = scope(commands.add_parser("bind", help="map a harness/bot item to canonical TASK IDs"))
    command.add_argument("--key", required=True)
    command.add_argument("--layer", choices=("harness", "bot"), required=True)
    command.add_argument("--channel", required=True)
    command.add_argument("--item", required=True)
    command.add_argument("--task", action="append", required=True)
    command.add_argument("--supersedes", default="")
    command.add_argument("--apply", action="store_true")
    command = scope(commands.add_parser("observe", help="append an immutable original external-state observation"))
    command.add_argument("--key", required=True)
    command.add_argument("--binding", required=True)
    command.add_argument("--raw-state", required=True)
    command.add_argument("--state", choices=STATES, required=True)
    command.add_argument("--revision", required=True)
    command.add_argument("--expected-revision", default="")
    command.add_argument("--evidence", action="append", required=True)
    command.add_argument("--at")
    command.add_argument("--apply", action="store_true")
    command = scope(commands.add_parser("delta", help="compare recorded mappings; never fetch or execute"))
    command.add_argument("--task", action="append")
    command.add_argument("--max-age-seconds", type=int)
    command.add_argument("--limit", type=int, default=10)
    command.add_argument("--layer", action="append", choices=("harness", "bot"))
    command = scope(commands.add_parser("card", help="retain a provider-neutral reference-only tool contract"))
    command.add_argument("--key", required=True)
    command.add_argument("--request", default="")
    command.add_argument("--task", action="append", required=True)
    for name in ("provider", "tool", "purpose", "input-revision", "permission-boundary", "stop-condition"):
        command.add_argument("--" + name, required=True)
    command.add_argument("--expected-evidence", action="append", required=True)
    command.add_argument("--apply", action="store_true")


def dispatch(root, defaults, args):
    action = args.root_action
    if action == "init":
        result = initialize(root, defaults, args.apply)
    elif action == "status":
        plan, mirrors, tasks = load(root)
        result = {"requests": len(plan["requests"]), "nodes": len(plan["nodes"]), "canonicalTasks": len(tasks),
                  "bindings": len(mirrors["bindings"]), "activeBindings": len(_active_bindings(mirrors)),
                  "observations": len(mirrors["observations"]), "cards": len(mirrors["cards"]),
                  "liveSyncVerified": False, "statusAuthority": "WORK/TASKS.json",
                  "progress": _progress(plan, tasks)}
    elif action == "roster":
        if (args.offset < 0 or args.decision_offset < 0 or
                not 1 <= args.limit <= ROSTER_PAGE_LIMIT or
                not 1 <= args.decision_limit <= ROSTER_PAGE_LIMIT):
            raise ValueError("Roster offsets must be nonnegative and page limits must be 1-50")
        result = roster(root)
        rows = result["rows"]
        decisions = result["decisions"]
        if args.actor:
            rows = [item for item in rows if item["actorId"] == args.actor]
            decisions = [item for item in decisions if item["actor"] == args.actor]
            if not rows and not decisions:
                raise ValueError("Actor or CLI channel is absent from the selected-scope roster")
        result["rows"] = rows[args.offset:args.offset + args.limit]
        result["decisions"] = decisions[args.decision_offset:args.decision_offset + args.decision_limit]
        result["page"] = {"totalRows": len(rows), "rowOffset": args.offset,
                          "nextRowOffset": args.offset + args.limit if args.offset + args.limit < len(rows) else None,
                          "totalDecisions": len(decisions), "decisionOffset": args.decision_offset,
                          "nextDecisionOffset": args.decision_offset + args.decision_limit
                          if args.decision_offset + args.decision_limit < len(decisions) else None}
    elif action == "packet":
        result = packet(root, args.task, args.limit)
    elif action == "request":
        identity = {"kind": args.kind, "title": args.title, "sourceRef": args.source_ref, "parent": args.parent}
        result = _append(root, PLAN, "requests", "RT" if args.kind == "rtask" else "ST", args.key,
                         identity, MAX_REQUESTS, args.apply)
    elif action == "node":
        identity = {"kind": args.kind, "title": args.title, "request": args.request, "parent": args.parent,
                    "milestone": args.milestone, "taskIds": args.task}
        result = _append(root, PLAN, "nodes", "NODE", args.key, identity, MAX_NODES, args.apply)
    elif action == "bind":
        identity = {"layer": args.layer, "channel": args.channel, "item": args.item,
                    "taskIds": args.task, "supersedes": args.supersedes}
        result = _append(root, MIRRORS, "bindings", "BIND", args.key, identity, MAX_BINDINGS, args.apply)
    elif action == "observe":
        identity = {"binding": args.binding, "rawState": args.raw_state, "state": args.state,
                    "sourceRevision": args.revision, "expectedRevision": args.expected_revision, "evidence": args.evidence}
        if args.at is not None:
            # Equivalent timezone spellings describe the same original instant.
            identity["at"] = memory.timestamp(args.at).astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

        def observed(tasks):
            _, mirrors, _ = load(root)
            binding = next((item for item in _active_bindings(mirrors) if item["id"] == args.binding), None)
            if binding is None:
                raise ValueError("Observe an existing active binding in the selected scope")
            at = memory.now()
            return {"at": identity.get("at", at), "recordedAt": at,
                    "canonicalTaskFingerprints": {identifier: records.fingerprint(tasks[identifier]) for identifier in binding["taskIds"]}}
        result = _append(root, MIRRORS, "observations", "OBS", args.key, identity, MAX_OBSERVATIONS, args.apply, observed)
    elif action == "delta":
        result = delta(root, args.task, args.max_age_seconds, args.limit, args.layer)
    elif action == "card":
        identity = {"request": args.request, "taskIds": args.task, "provider": args.provider, "tool": args.tool,
                    "purpose": args.purpose, "inputRevision": args.input_revision, "expectedEvidence": args.expected_evidence,
                    "permissionBoundary": args.permission_boundary, "stopCondition": args.stop_condition}
        result = _append(root, MIRRORS, "cards", "CARD", args.key, identity, MAX_CARDS, args.apply,
                         response_fields={"toolCalled": False})
    else:
        raise ValueError("Unknown ROOT action")
    return _public(root, result, packet=action == "packet")
