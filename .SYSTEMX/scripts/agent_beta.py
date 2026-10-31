"""Opt-in local BOT/DOT workspace coordinator; no online bot runtime."""

import json
from pathlib import Path
import re

import agent_standards as records
import project_memory as memory


AGENT = "agent.b"
ROLE = "bot-coordinator"
COMMANDS = {"agent-beta"}
SEEDS = ("README.md", "AGENTB.MD", "MEMORY.md", "BOTS.json", ".gitignore")
REQUIRED = ("scripts/agent_beta.py", "tests/test_agent_beta.py") + tuple(
    "AGENTB/" + name for name in SEEDS
) + tuple(
    "templates/agentb/" + name for name in SEEDS
)
INDEX = "AGENTB/BOTS.json"
MEMORY = "AGENTS/agent.b/MEMORY.md"
MAX_FILE_BYTES = 256 * 1024
MAX_BOTS = 100
NAME = re.compile(r"[A-Z][A-Z0-9_]{0,31}\Z")
PROVIDER = re.compile(r"[a-z][a-z0-9-]{0,31}\Z")
IDENTITY = re.compile(r"[A-Za-z][A-Za-z0-9._@:-]{0,127}\Z")
ACCESS_ID = re.compile(r"ACC-[0-9]{3,12}\Z")
BLANK_MEMORY = ("# Agent Beta memory seed\n\n"
                "No project context, bot assignments, credentials, or decisions are stored in\n"
                "this reusable seed.\n")
BLANK_GITIGNORE = "/.SYSTEMXB-*/\n"
LIMIT = ("Local BOT/DOT records only. Names and task references are advisory. "
         "No model, process, tool, network connection, bot activation, or task acceptance is started.")


def _text(root, relative):
    path = records.safe(root, relative)
    if not path.is_file() or path.stat().st_size > MAX_FILE_BYTES:
        raise ValueError("Missing or oversized Agent Beta file: " + relative)
    raw = path.read_bytes()
    if len(raw) > MAX_FILE_BYTES or b"\x00" in raw:
        raise ValueError("Agent Beta files must be bounded UTF-8 text without NUL bytes: " + relative)
    return raw.decode("utf-8")


def _json(root, relative):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate Agent Beta JSON key: " + key)
            result[key] = value
        return result

    def invalid(value):
        raise ValueError("Non-finite Agent Beta number: " + value)

    try:
        return json.loads(_text(root, relative), object_pairs_hook=unique, parse_constant=invalid)
    except RecursionError as error:
        raise ValueError("Agent Beta JSON nesting exceeds the supported parser depth") from error


def _write(root, relative, value):
    content = json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    if len(content.encode("utf-8")) > MAX_FILE_BYTES:
        raise ValueError("Agent Beta record exceeds its 256 KiB limit")
    records.safe(root, relative)
    memory.atomic_write(Path(root), relative, content)


def _name(value):
    if not isinstance(value, str) or not NAME.fullmatch(value):
        raise ValueError("BOT_NAME must be 1-32 uppercase ASCII letters, digits, or underscores; start with a letter")
    return value


def _relative(name):
    return "AGENTB/.SYSTEMXB-" + _name(name)


def _bot_files(name):
    relative = _relative(name)
    return (relative + "/BOT.json", relative + "/MEMORY.md", relative + "/README.md",
            relative + "/Rules.MD")


def _access_decisions(root):
    relative = "GLOBAL/ACCESS-MATRIX.json"
    if not records.safe(root, relative).is_file():
        return {}
    import agenda_access
    data = agenda_access.validate_access(records.read(root, relative))
    return {row["id"]: row for row in data["decisions"]}


def _access_ids(root):
    return set(_access_decisions(root))


def _linked_decision(root, name, access_decision_id, decisions=None):
    """Bind a bot only to its own reviewed intent, never to a grant or another actor."""
    if (not isinstance(access_decision_id, str) or not ACCESS_ID.fullmatch(access_decision_id) or
            int(access_decision_id.split("-", 1)[1]) == 0):
        raise ValueError("Access Matrix reference must be a positive ACC-000 style ID")
    if decisions is None:
        import agenda_access
        agenda, access = agenda_access._load(root)
        if agenda is None:
            raise ValueError("Initialize Agenda and Access Matrix in this scope before linking access")
        decisions = {item["id"]: item for item in access["decisions"]}
    row = decisions.get(access_decision_id)
    if row is None:
        raise ValueError("Agent Beta access decision must exist in the selected-scope Access Matrix")
    if row["actor"] != "agentb:" + _name(name) or row["decision"] != "reviewed-intent":
        raise ValueError("Agent Beta access link requires this BOT/DOT actor's reviewed intent")
    return row


def _metadata(name, kind, source="local", provider="", provider_identity="", access_decision_id=""):
    if not isinstance(kind, str) or kind not in {"bot", "dot"}:
        raise ValueError("Agent Beta kind must be bot or dot")
    if not isinstance(source, str) or source not in {"local", "online-reference"}:
        raise ValueError("Agent Beta source must be local or online-reference")
    if any(not isinstance(item, str) for item in (provider, provider_identity, access_decision_id)):
        raise ValueError("Agent Beta provider references must be strings")
    if source == "local" and (provider or provider_identity):
        raise ValueError("Local BOT/DOT records cannot name a provider identity")
    if source == "online-reference" and (not isinstance(provider, str) or not PROVIDER.fullmatch(provider) or
                                         not isinstance(provider_identity, str) or not IDENTITY.fullmatch(provider_identity)):
        raise ValueError("Online references need a short provider name and non-secret identity alias")
    if provider_identity.lower().startswith(("sk-", "sk_", "ghp_", "github_pat_", "xoxb-", "xoxp-",
                                             "glpat-", "akia", "bearer")):
        raise ValueError("Provider identity must be an alias, not a credential")
    if access_decision_id and (not ACCESS_ID.fullmatch(access_decision_id) or
                               int(access_decision_id.split("-", 1)[1]) == 0):
        raise ValueError("Access Matrix reference must be a positive ACC-000 style ID")
    return {"schemaVersion": 1, "name": _name(name), "kind": kind, "source": source,
            "provider": provider, "providerIdentity": provider_identity,
            "accessDecisionId": access_decision_id, "online": False, "taskIds": []}


def _validate_metadata(root, value, name, kind, known_tasks):
    memory.fields(value, ("schemaVersion", "name", "kind", "source", "provider", "providerIdentity",
                          "accessDecisionId", "online", "taskIds"), "Agent Beta bot")
    if type(value["schemaVersion"]) is not int or value["schemaVersion"] != 1:
        raise ValueError("Agent Beta bot schemaVersion must be the integer 1")
    if value["name"] != name or value["kind"] != kind or value["online"] is not False:
        raise ValueError("Agent Beta bot identity, kind, or offline state differs from its index")
    expected = _metadata(name, kind, value["source"], value["provider"],
                         value["providerIdentity"], value["accessDecisionId"])
    if any(value[key] != expected[key] for key in ("source", "provider", "providerIdentity", "accessDecisionId")):
        raise ValueError("Agent Beta provider metadata is inconsistent")
    if value["accessDecisionId"]:
        _linked_decision(root, name, value["accessDecisionId"])
    ids = value["taskIds"]
    if not isinstance(ids, list) or len(ids) > 100 or any(not isinstance(item, str) for item in ids):
        raise ValueError("Agent Beta task IDs must be a bounded unique list")
    if len(ids) != len(set(ids)):
        raise ValueError("Agent Beta task IDs must be a bounded unique list")
    if any(not isinstance(item, str) or not re.fullmatch(r"TASK-\d{3,}", item) or
           item not in known_tasks for item in ids):
        raise ValueError("Agent Beta task references must exist in the selected scope")
    return value


def load_bots(root):
    """Read only the bounded index and fixed local bot records."""
    data = _json(root, INDEX)
    memory.fields(data, ("schemaVersion", "bots"), "Agent Beta bot index")
    if type(data["schemaVersion"]) is not int or data["schemaVersion"] != 1:
        raise ValueError("Agent Beta index schemaVersion must be the integer 1")
    if not isinstance(data["bots"], list) or len(data["bots"]) > MAX_BOTS:
        raise ValueError("Agent Beta index exceeds its 100-bot limit")
    ledger, _ = memory.load(root)
    known_tasks = {item["id"] for item in ledger["tasks"]}
    seen = set()
    for item in data["bots"]:
        memory.fields(item, ("name", "kind", "path"), "Agent Beta bot index entry")
        name = _name(item["name"])
        if (name in seen or not isinstance(item["kind"], str) or item["kind"] not in {"bot", "dot"} or
                item["path"] != _relative(name)):
            raise ValueError("Agent Beta index has duplicate or inconsistent bot identity")
        seen.add(name)
        for relative in _bot_files(name):
            _text(root, relative)
        _validate_metadata(root, _json(root, _bot_files(name)[0]), name, item["kind"], known_tasks)
    directory = memory.managed(Path(root), "AGENTB")
    if directory.exists():
        if not directory.is_dir():
            raise ValueError("AGENTB must be a directory")
        for path in directory.iterdir():
            if path.name.casefold().startswith(".systemxb-"):
                if not path.is_dir() or path.name.removeprefix(".SYSTEMXB-") not in seen:
                    raise ValueError("Agent Beta found an unindexed or invalid bot workspace: " + path.name)
    return data


def validate_optional(root):
    """Legacy scopes remain valid; a present or registered Beta panel is complete."""
    root = Path(root)
    _, registry = memory.load(root)
    active = any(item["id"] == AGENT for item in registry["agents"])
    directory = memory.managed(root, "AGENTB")
    if not directory.exists() and not active:
        return
    for name in SEEDS:
        _text(root, "AGENTB/" + name)
    data = load_bots(root)
    if data["bots"] and not active:
        raise ValueError("Agent Beta bots require explicitly registered agent.b")
    if active:
        _text(root, MEMORY)


def validate_template(root, defaults):
    validate_optional(root)
    _, registry = memory.load(root)
    if any(item["id"] == AGENT for item in registry["agents"]):
        raise ValueError("The public Agent Beta template must not register agent.b")
    for name in SEEDS:
        relative = "AGENTB/" + name
        if _text(root, relative).replace("\r\n", "\n") != _text(
                defaults, "templates/agentb/" + name).replace("\r\n", "\n"):
            raise ValueError(relative + " differs from its reviewed blank seed")
    if load_bots(root)["bots"]:
        raise ValueError("The public Agent Beta bot index must remain empty")
    if _text(root, "AGENTB/MEMORY.md") != BLANK_MEMORY or _text(root, "AGENTB/.gitignore") != BLANK_GITIGNORE:
        raise ValueError("The public Agent Beta memory and ignore rule must remain blank and canonical")
    if records.safe(root, MEMORY).exists():
        raise ValueError("The public Agent Beta template must not contain registered memory")


def _seed(defaults):
    seed = {"AGENTB/" + name: _text(defaults, "templates/agentb/" + name) for name in SEEDS}
    if _json(defaults, "templates/agentb/BOTS.json") != {"schemaVersion": 1, "bots": []}:
        raise ValueError("The Agent Beta creation seed must have an empty bot index")
    if seed["AGENTB/MEMORY.md"] != BLANK_MEMORY or seed["AGENTB/.gitignore"] != BLANK_GITIGNORE:
        raise ValueError("The Agent Beta creation seed must keep blank memory and the canonical ignore rule")
    return seed


def initialize(root, defaults, apply=False):
    """Preview or install blank Beta records in the explicitly selected scope."""
    root, defaults = Path(root), Path(defaults)
    _, registry = memory.load(root)
    seed = _seed(defaults)
    seed[MEMORY] = seed["AGENTB/MEMORY.md"]
    existing = {item["id"] for item in registry["agents"]}
    additions = [] if AGENT in existing else [AGENT]
    missing = [relative for relative in seed if not records.safe(root, relative).exists()]
    for relative in seed:
        if relative not in missing:
            _text(root, relative)
    if INDEX not in missing:
        load_bots(root)
    result = {"applied": False, "register": additions, "add": missing,
              "preserve": [relative for relative in seed if relative not in missing],
              "scope": str(root), "runtimeStarted": False, "online": False, "limit": LIMIT}
    if not apply or not (additions or missing):
        return result
    with memory.coordination_lock(root):
        planned = initialize(root, defaults)
        _, registry = memory.load(root)
        for relative in planned["add"]:
            records.safe(root, relative)
            memory.atomic_write(root, relative, seed[relative])
        if planned["register"]:
            registry["agents"].append({"id": AGENT, "role": ROLE, "memory": MEMORY})
            _write(root, "AGENTS/REGISTRY.json", registry)
    return {**planned, "applied": True}


def _active(root):
    _, registry = memory.load(root)
    if not any(item["id"] == AGENT for item in registry["agents"]):
        raise ValueError("Initialize Agent Beta in this scope with agent-beta setup --apply first")
    validate_optional(root)
    return _access_ids(root)


def add_bot(root, name, kind="bot", apply=False, *, source="local", provider="",
            provider_identity="", access_decision_id=""):
    """Create an offline BOT/DOT workspace without launching or contacting it."""
    root = Path(root)
    _active(root)
    name = _name(name)
    metadata = _metadata(name, kind, source, provider, provider_identity, access_decision_id)
    if access_decision_id:
        _linked_decision(root, name, access_decision_id)

    def plan():
        data = load_bots(root)
        existing = next((item for item in data["bots"] if item["name"] == name), None)
        relative = _relative(name)
        directory = records.safe(root, relative + "/BOT.json").parent
        if existing:
            if existing["kind"] != kind:
                raise ValueError("Agent Beta bot name already exists with another kind")
            current = _json(root, _bot_files(name)[0])
            if any(current[key] != metadata[key] for key in
                   ("source", "provider", "providerIdentity", "accessDecisionId")):
                raise ValueError("Agent Beta bot name already exists with another provider mapping")
            return data, False
        if len(data["bots"]) >= MAX_BOTS:
            raise ValueError("Agent Beta index has reached its 100-bot limit")
        if directory.exists():
            raise ValueError("Agent Beta bot workspace already exists outside the index")
        return data, True

    data, create = plan()
    result = {"applied": False, "created": create, "bot": metadata,
              "path": _relative(name), "scope": str(root), "runtimeStarted": False,
              "online": False, "limit": LIMIT}
    if not apply or not create:
        return result
    with memory.coordination_lock(root):
        data, create = plan()
        if not create:
            return {**result, "created": False}
        relative = _relative(name)
        directory = records.safe(root, relative + "/BOT.json").parent
        directory.mkdir()
        _write(root, relative + "/BOT.json", metadata)
        memory.atomic_write(root, relative + "/MEMORY.md", "# " + name + " local memory\n\n")
        memory.atomic_write(root, relative + "/README.md",
                            "# " + name + " local BOT/DOT workspace\n\n"
                            "This workspace is advisory. An online source reference is not a connection. "
                            "Do not store secrets here. "
                            "Agent 0 and the user retain task acceptance and external-action authority.\n")
        memory.atomic_write(root, relative + "/Rules.MD", "# Provider rules\n\n")
        data["bots"].append({"name": name, "kind": kind, "path": relative})
        _write(root, INDEX, data)
    return {**result, "applied": True}


def link_access(root, name, access_decision_id, expected_revision="", apply=False):
    """Record a reviewed-intent reference after BOT/DOT and Access Matrix setup."""
    root = Path(root)
    _active(root)
    name = _name(name)
    if not isinstance(expected_revision, str) or (expected_revision and not re.fullmatch(
            r"[0-9a-f]{64}", expected_revision)):
        raise ValueError("Expected revision must be a lowercase SHA-256 value from access-link preview")
    if apply and not expected_revision:
        raise ValueError("Access link --apply requires --expected-revision from a fresh preview")

    def plan():
        index = load_bots(root)
        entry = next((item for item in index["bots"] if item["name"] == name), None)
        if entry is None:
            raise ValueError("Unknown Agent Beta bot in the selected scope")
        relative = _bot_files(name)[0]
        bot = _json(root, relative)
        import agenda_access
        agenda, access = agenda_access._load(root)
        if agenda is None:
            raise ValueError("Initialize Agenda and Access Matrix in this scope before linking access")
        decisions = {row["id"]: row for row in access["decisions"]}
        decision = _linked_decision(root, name, access_decision_id, decisions)
        revision = records.fingerprint({"bot": bot, "access": access})
        if expected_revision and revision != expected_revision:
            raise ValueError("Agent Beta bot or Access Matrix changed since preview; inspect and retry")
        changed = bot["accessDecisionId"] != access_decision_id
        proposed = {**bot, "accessDecisionId": access_decision_id}
        ledger, _ = memory.load(root)
        _validate_metadata(root, proposed, name, entry["kind"],
                           {item["id"] for item in ledger["tasks"]})
        return {"applied": False, "changed": changed, "bot": proposed,
                "accessDecision": {"id": decision["id"], "actor": decision["actor"],
                                   "resource": decision["resource"], "action": decision["action"],
                                   "environment": decision["environment"],
                                   "decision": decision["decision"]},
                "revisionBefore": revision,
                "revisionAfter": records.fingerprint({"bot": proposed, "access": access}),
                "scope": str(root), "runtimeStarted": False, "online": False,
                "identityVerified": False, "accessGranted": False, "limit": LIMIT}, relative

    result, relative = plan()
    if not apply or not result["changed"]:
        return result
    with memory.coordination_lock(root):
        current, relative = plan()
        if current["changed"]:
            _write(root, relative, current["bot"])
    return {**current, "applied": current["changed"]}


def assign_task(root, name, task, apply=False):
    """Record an advisory canonical task reference; never alter task state."""
    root = Path(root)
    _active(root)
    name = _name(name)
    ledger, _ = memory.load(root)
    if task not in {item["id"] for item in ledger["tasks"]}:
        raise ValueError("Agent Beta task must exist in the selected scope")

    def plan():
        data = load_bots(root)
        entry = next((item for item in data["bots"] if item["name"] == name), None)
        if entry is None:
            raise ValueError("Unknown Agent Beta bot in the selected scope")
        relative = _bot_files(name)[0]
        bot = _json(root, relative)
        if task in bot["taskIds"]:
            return bot, relative, False
        if len(bot["taskIds"]) >= 100:
            raise ValueError("Agent Beta bot has reached its 100-task reference limit")
        bot["taskIds"].append(task)
        return bot, relative, True

    bot, relative, changed = plan()
    result = {"applied": False, "changed": changed, "bot": bot,
              "scope": str(root), "runtimeStarted": False, "online": False, "limit": LIMIT}
    if not apply or not changed:
        return result
    with memory.coordination_lock(root):
        bot, relative, changed = plan()
        if changed:
            _write(root, relative, bot)
    return {**result, "applied": changed, "changed": changed, "bot": bot}


def add_cli(subparsers, scope=None):
    scope = scope or (lambda parser: parser)
    parent = subparsers.add_parser("agent-beta", help=__doc__)
    commands = parent.add_subparsers(dest="beta_action", required=True)
    command = scope(commands.add_parser("setup", help="preview blank Agent Beta setup"))
    command.add_argument("--apply", action="store_true")
    command = scope(commands.add_parser("bot-add", help="preview an offline BOT/DOT workspace"))
    command.add_argument("name", metavar="BOT_NAME")
    command.add_argument("--kind", choices=("bot", "dot"), default="bot")
    command.add_argument("--source", choices=("local", "online-reference"), default="local")
    command.add_argument("--provider", default="", help="short service name, not a credential")
    command.add_argument("--provider-identity", default="", help="non-secret provider identity alias")
    command.add_argument("--access-decision-id", default="", help="existing Access Matrix ACC- ID")
    command.add_argument("--apply", action="store_true")
    command = scope(commands.add_parser("access-link", help="preview a reviewed Access Matrix link for an existing BOT/DOT"))
    command.add_argument("name", metavar="BOT_NAME")
    command.add_argument("--access-decision-id", required=True, help="existing reviewed-intent ACC- ID for agentb:BOT_NAME")
    command.add_argument("--expected-revision", default="", help="revision from a fresh access-link preview; required with --apply")
    command.add_argument("--apply", action="store_true")
    command = scope(commands.add_parser("assign", help="preview an advisory canonical task reference"))
    command.add_argument("name", metavar="BOT_NAME")
    command.add_argument("--task", required=True)
    command.add_argument("--apply", action="store_true")
    scope(commands.add_parser("status", help="list only local BOT/DOT metadata"))
    scope(commands.add_parser("validate", help="validate Agent Beta records without writes"))


def dispatch(root, defaults, args):
    if args.beta_action == "setup":
        return initialize(root, defaults, args.apply)
    if args.beta_action == "bot-add":
        return add_bot(root, args.name, args.kind, args.apply, source=args.source,
                       provider=args.provider, provider_identity=args.provider_identity,
                       access_decision_id=args.access_decision_id)
    if args.beta_action == "access-link":
        return link_access(root, args.name, args.access_decision_id, args.expected_revision, args.apply)
    if args.beta_action == "assign":
        return assign_task(root, args.name, args.task, args.apply)
    if args.beta_action in {"status", "validate"}:
        validate_optional(root)
        directory = memory.managed(Path(root), "AGENTB")
        data = load_bots(root) if directory.exists() else {"schemaVersion": 1, "bots": []}
        _, registry = memory.load(root)
        return {"valid": True, "registered": any(item["id"] == AGENT for item in registry["agents"]),
                "bots": data["bots"], "scope": str(root), "runtimeStarted": False,
                "online": False, "limit": LIMIT}
    raise ValueError("Unknown Agent Beta action")
