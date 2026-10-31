"""Agent Alpha settings and documented access intent; no grants or execution.

These two JSON tables are the canonical data. CSV is generated on demand and is
never read back as an authority. Agenda only selects advisory context from the
existing ten AUTOBOT slots; it does not add a bot or schedule work.
"""

import csv
import hashlib
import io
import os
from pathlib import Path
import re
import tempfile
from xml.etree import ElementTree as ET
import zipfile

import agent_standards as records
import autobots
import project_memory as memory


COMMANDS = {"agenda"}
AGENDA = "AUTOBOT/AGENDA.json"
ACCESS = "GLOBAL/ACCESS-MATRIX.json"
SETTING_CATALOG = "AUTOBOT/AGENDA-SETTINGS.json"
DECISION_CATALOG = "GLOBAL/ACCESS-DECISION-RULES.json"
SEEDS = {
    AGENDA: "templates/agenda/AGENDA.json",
    ACCESS: "templates/agenda/ACCESS-MATRIX.json",
    SETTING_CATALOG: "templates/agenda/AGENDA-SETTINGS.json",
    DECISION_CATALOG: "templates/agenda/ACCESS-DECISION-RULES.json",
}
REQUIRED = ("scripts/agenda_access.py", "tests/test_agenda_access.py", AGENDA, ACCESS,
            SETTING_CATALOG, DECISION_CATALOG, *SEEDS.values())
OPTION_COLUMNS = ("id", "botId", "setting", "value", "providerRulesPath",
                  "providerRulesSha256", "accessDecisionId", "reason", "reviewedAt", "evidence")
ACCESS_COLUMNS = ("id", "actor", "resource", "action", "environment", "decision",
                  "owner", "policyRef", "evidence", "reviewedAt", "recheck")
ROLE_COLUMNS = ("id", "actor", "kind", "instanceRule", "templateGrant",
                "requiresReview", "purpose")
TABLE_COLUMNS = OPTION_COLUMNS + ("accessDecision", "accessOwner", "accessConflict", "rulesCurrent")
SETTING_COLUMNS = ("id", "botId", "setting", "defaultValue", "allowedValues",
                   "providerRulesPath", "reviewRequired", "includeRequiresAccessDecision",
                   "reviewQuestion", "effect")
DECISION_RULE_COLUMNS = ("state", "recorded", "meaning", "policyRefRequiredForNewRecord",
                         "ownerRequired", "evidenceRequired", "identityVerifiedByTemplate",
                         "accessGrantedByTemplate")
ROSTER_COLUMNS = ("actorId", "kind", "displayName", "registrationState", "sourceRecord",
                  "workspace", "providerAlias", "taskCount", "accessDecisionIds",
                  "reviewedIntentCount", "deniedCount", "gapCount", "externalRightsVerified")
DECISIONS = ("reviewed-intent", "denied", "gap")
MAX_ROWS = 1024
MAX_RULE_BYTES = 256 * 1024
MAX_WORKBOOK_BYTES = 32 * 1024 * 1024
WORKBOOK_DEFAULT = "local/ACCESS-MATRIX-current.xlsx"

# Catalog entries document supported roles and instance naming. They do not
# activate roles or grant access. Dynamic instance patterns require a separate
# selected-scope registry/workspace record and a reviewed access decision.
STANDARD_ROLES = (
    ("agent.0", "agent", "", "Scope coordination and acceptance"),
    ("agent.1", "agent", "Opt-in security-access only if this numeric ID is free", "Security and Access review"),
    ("agent.a", "agent", "", "Agent Alpha advisory context coordinator"),
    ("agent.b", "agent", "", "Agent Beta BOT/DOT workspace coordinator"),
    ("agent.x", "agent", "", "Event and due-item records"),
    ("agent.y", "agent", "", "Assigned CLI branch and PR lane"),
    ("agent.z", "agent", "", "Bounded review policy"),
    ("agent.numeric-worker", "agent-pattern", "agent.[1-9][0-9]* in selected-scope AGENTS/REGISTRY.json", "Other optional numeric workers"),
    ("native.subagent", "subagent-pattern", "Host-assigned unique session ID with one bounded task", "Host-managed finite subagent assignments"),
    ("agentb.instance", "bot-pattern", "AGENTB/.SYSTEMXB-[A-Z][A-Z0-9_]{0,31} with a BOTS.json record", "Named BOT/DOT workspace instances"),
    ("autobot.design", "autobot", "", "Interface and accessibility references"),
    ("autobot.soul", "autobot", "", "Purpose and interaction references"),
    ("autobot.memory", "autobot", "", "Accepted context references"),
    ("autobot.rules", "autobot", "", "Project constraints and authority references"),
    ("autobot.research", "autobot", "", "Source and uncertainty references"),
    ("autobot.brand", "autobot", "", "Company and product identity references"),
    ("autobot.media", "autobot", "", "Asset and media-rights references"),
    ("autobot.tokens", "autobot", "", "Design token and theme references"),
    ("autobot.data", "autobot", "", "Dataset provenance references"),
    ("autobot.archive", "autobot", "", "Retention and recall references"),
)
ROLE_DEFAULTS = tuple({"id": "ROLE-{:03d}".format(index), "actor": actor,
                       "kind": kind, "instanceRule": rule, "templateGrant": "none",
                       "requiresReview": True, "purpose": purpose}
                      for index, (actor, kind, rule, purpose) in enumerate(STANDARD_ROLES, 1))
SETTING_DEFAULTS = tuple({
    "id": "SETTING-{:03d}".format(index), "botId": "autobot." + slug,
    "setting": "context_selection", "defaultValue": "unset",
    "allowedValues": ["include", "exclude"],
    "providerRulesPath": "AUTOBOT/" + filename,
    "reviewRequired": True, "includeRequiresAccessDecision": True,
    "reviewQuestion": "Should " + name + " reference context be included or excluded for this selected scope?",
    "effect": "Advisory context only; no worker, schedule, or permission starts."}
    for index, (slug, name, filename) in enumerate(autobots.SLOTS, 1))
DECISION_RULES = (
    {"state": "no-row", "recorded": False,
     "meaning": "No reviewed decision exists; no access is inferred.",
     "policyRefRequiredForNewRecord": False, "ownerRequired": False,
     "evidenceRequired": False, "identityVerifiedByTemplate": False,
     "accessGrantedByTemplate": False},
    {"state": "gap", "recorded": True,
     "meaning": "An access question remains open; resolve it before relying on this path.",
     "policyRefRequiredForNewRecord": False, "ownerRequired": True,
     "evidenceRequired": True, "identityVerifiedByTemplate": False,
     "accessGrantedByTemplate": False},
    {"state": "denied", "recorded": True,
     "meaning": "A reviewer recorded denial; do not use this access path.",
     "policyRefRequiredForNewRecord": False, "ownerRequired": True,
     "evidenceRequired": True, "identityVerifiedByTemplate": False,
     "accessGrantedByTemplate": False},
    {"state": "reviewed-intent", "recorded": True,
     "meaning": "A reviewer recorded intended access; verify real identity and permission at the external boundary.",
     "policyRefRequiredForNewRecord": True, "ownerRequired": True,
     "evidenceRequired": True, "identityVerifiedByTemplate": False,
     "accessGrantedByTemplate": False},
)
SETTING_POLICY = {"schemaVersion": 1, "defaultState": "unset",
                  "settings": list(SETTING_DEFAULTS)}
DECISION_POLICY = {"schemaVersion": 1, "defaultState": "no-row", "templateGrant": "none",
                   "decisionScope": ["actor", "resource", "action", "environment"],
                   "newRecordRequiredFields": ["id", "actor", "resource", "action", "environment",
                                               "decision", "owner", "evidence", "reviewedAt"],
                   "rules": list(DECISION_RULES)}


def _string(value, label, maximum=2048, required=True):
    memory.string(value, label, nonempty=required)
    if len(value.encode("utf-8")) > maximum:
        raise ValueError(label + " exceeds its UTF-8 limit")


def _evidence(value, label):
    memory.strings(value, label, nonempty=True)
    if len(value) > 16 or len(value) != len(set(value)):
        raise ValueError(label + " must contain at most 16 distinct references")
    for item in value:
        _string(item, label + " entry")


def _positive_id(value, prefix):
    if not isinstance(value, str) or not re.fullmatch(prefix + r"-[0-9]{3,12}", value) or int(value.split("-", 1)[1]) == 0:
        raise ValueError(prefix + " ID must have at least three digits and a positive number")


def _rules_path(root, relative, *, require_file=False):
    _string(relative, "Provider rules path", maximum=512)
    fixed_files = {"AUTOBOT/" + item[2] for item in autobots.SLOTS}
    allowed = relative in fixed_files or re.fullmatch(
        r"AGENTB/\.SYSTEMXB-[A-Z][A-Z0-9_]{0,31}/Rules\.MD", relative)
    if not allowed:
        raise ValueError("Provider rules must be a selected-scope AUTOBOT or AGENTB .MD file")
    path = records.safe(root, relative)
    if require_file and (not path.is_file() or path.stat().st_size > MAX_RULE_BYTES):
        raise ValueError("Missing or oversized provider rules file: " + relative)
    return path


def _rule_digest(root, relative):
    path = _rules_path(root, relative)
    if not path.is_file() or path.stat().st_size > MAX_RULE_BYTES:
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_access(data):
    if not isinstance(data, dict):
        raise ValueError("Access Matrix must be an object")
    # Legacy selected scopes may predate the standard catalog. An absent
    # catalog never implies a grant; only new distributed seeds contain it.
    memory.fields(data, (("schemaVersion", "decisions", "roleDefaults")
                         if "roleDefaults" in data else ("schemaVersion", "decisions")),
                  "Access Matrix")
    if type(data["schemaVersion"]) is not int or data["schemaVersion"] != 1:
        raise ValueError("Access Matrix schemaVersion must be 1")
    if "roleDefaults" in data and data["roleDefaults"] != list(ROLE_DEFAULTS):
        raise ValueError("Access Matrix standard roles must match the fixed default-deny catalog")
    if not isinstance(data["decisions"], list) or len(data["decisions"]) > MAX_ROWS:
        raise ValueError("Access Matrix decisions must be a bounded list")
    seen = set()
    for row in data["decisions"]:
        memory.fields(row, ACCESS_COLUMNS, "Access Matrix row")
        _positive_id(row["id"], "ACC")
        if row["id"] in seen:
            raise ValueError("Duplicate Access Matrix ID")
        seen.add(row["id"])
        for field in ("actor", "resource", "action", "environment", "owner"):
            _string(row[field], "Access Matrix " + field)
        if row["decision"] not in DECISIONS:
            raise ValueError("Access Matrix records reviewed intent, denial, or a gap; never a grant")
        _string(row["policyRef"], "Access Matrix policyRef", required=False)
        _string(row["recheck"], "Access Matrix recheck", required=False)
        _evidence(row["evidence"], "Access Matrix evidence")
        memory.timestamp(row["reviewedAt"])
    return data


def validate_agenda(data, access=None, root=None):
    memory.fields(data, ("schemaVersion", "options"), "Agenda")
    if type(data["schemaVersion"]) is not int or data["schemaVersion"] != 1:
        raise ValueError("Agenda schemaVersion must be 1")
    if not isinstance(data["options"], list) or len(data["options"]) > MAX_ROWS:
        raise ValueError("Agenda options must be a bounded list")
    fixed_files = {"autobot." + item[0]: "AUTOBOT/" + item[2] for item in autobots.SLOTS}
    known_access = {row["id"] for row in access["decisions"]} if access is not None else set()
    ids, settings = set(), set()
    for row in data["options"]:
        memory.fields(row, OPTION_COLUMNS, "Agenda option")
        _positive_id(row["id"], "AGA")
        if row["id"] in ids:
            raise ValueError("Duplicate Agenda ID")
        ids.add(row["id"])
        _string(row["botId"], "Agenda botId", maximum=64)
        if row["botId"] not in fixed_files:
            raise ValueError("Agenda may select only the ten fixed AUTOBOT IDs")
        if row["setting"] != "context_selection" or row["value"] not in ("include", "exclude"):
            raise ValueError("Agenda setting must be advisory context_selection include or exclude")
        key = (row["botId"], row["setting"])
        if key in settings:
            raise ValueError("Duplicate Agenda setting for one AUTOBOT")
        settings.add(key)
        _string(row["providerRulesPath"], "Agenda providerRulesPath", maximum=512)
        if (row["providerRulesPath"].startswith("AUTOBOT/") and
                row["providerRulesPath"] != fixed_files[row["botId"]]):
            raise ValueError("Agenda fixed AUTOBOT rules path must match the selected bot ID")
        if root is not None:
            _rules_path(root, row["providerRulesPath"])
        if not isinstance(row["providerRulesSha256"], str) or not re.fullmatch(
                r"[0-9a-f]{64}", row["providerRulesSha256"]):
            raise ValueError("Agenda provider rules digest must be SHA-256")
        _string(row["accessDecisionId"], "Agenda accessDecisionId", maximum=64,
                required=row["value"] == "include" or row["providerRulesPath"].startswith("AGENTB/"))
        if row["accessDecisionId"]:
            _positive_id(row["accessDecisionId"], "ACC")
            if access is not None and row["accessDecisionId"] not in known_access:
                raise ValueError("Agenda access decision must reference a row in the selected scope")
        _string(row["reason"], "Agenda reason")
        _evidence(row["evidence"], "Agenda evidence")
        memory.timestamp(row["reviewedAt"])
    return data


def _catalog_pair(root):
    """Accept absent beta.1 catalogs, but never a partial or altered pair."""
    paths = (SETTING_CATALOG, DECISION_CATALOG)
    present = [records.safe(root, relative).is_file() for relative in paths]
    if any(present) and not all(present):
        raise ValueError("Agenda and access-decision catalogs must be installed together")
    if not any(present):
        return None
    catalogs = {relative: records.read(root, relative) for relative in paths}
    if catalogs[SETTING_CATALOG] != SETTING_POLICY:
        raise ValueError("Agenda setting catalog must match the fixed default-inactive policy")
    if catalogs[DECISION_CATALOG] != DECISION_POLICY:
        raise ValueError("Access-decision rule catalog must match the fixed no-grant policy")
    return catalogs


def _load(root):
    root = Path(root)
    _catalog_pair(root)
    agenda_exists, access_exists = records.safe(root, AGENDA).is_file(), records.safe(root, ACCESS).is_file()
    if agenda_exists != access_exists:
        raise ValueError("Agenda and Access Matrix JSON must be initialized together")
    if not agenda_exists:
        return None, None
    access = validate_access(records.read(root, ACCESS))
    agenda = validate_agenda(records.read(root, AGENDA), access, root)
    return agenda, access


def validate_optional(root):
    _load(root)


def _blank_seeds(defaults):
    """Read dedicated distribution templates, never mutable scope records."""
    seeds = {relative: records.read(defaults, template) for relative, template in SEEDS.items()}
    validate_access(seeds[ACCESS])
    validate_agenda(seeds[AGENDA], seeds[ACCESS])
    if seeds[AGENDA] != {"schemaVersion": 1, "options": []} or seeds[ACCESS] != {
            "schemaVersion": 1, "roleDefaults": list(ROLE_DEFAULTS), "decisions": []}:
        raise ValueError("Agenda templates must have blank options and decisions with fixed default-deny roles")
    if seeds[SETTING_CATALOG] != SETTING_POLICY or seeds[DECISION_CATALOG] != DECISION_POLICY:
        raise ValueError("Agenda templates must have fixed default-inactive and no-grant catalogs")
    return seeds


def validate_template(root, defaults=None):
    seeds = _blank_seeds(defaults or root)
    agenda, access = _load(root)
    catalogs = _catalog_pair(root)
    if (agenda != seeds[AGENDA] or access != seeds[ACCESS] or catalogs is None or
            any(catalogs[relative] != seeds[relative] for relative in (SETTING_CATALOG, DECISION_CATALOG))):
        raise ValueError("Public Agenda and Access Matrix records must match blank distribution templates")


def _alpha_active(root):
    _, registry = memory.load(Path(root))
    if not any(agent["id"] == "agent.a" for agent in registry["agents"]):
        raise ValueError("Activate Agent Alpha in this selected scope before editing Agenda")


def initialize(root, defaults, apply=False):
    root, defaults = Path(root), Path(defaults)
    seeds = _blank_seeds(defaults)
    records_missing = [relative for relative in (AGENDA, ACCESS) if not records.safe(root, relative).exists()]
    catalogs_missing = [relative for relative in (SETTING_CATALOG, DECISION_CATALOG)
                        if not records.safe(root, relative).exists()]
    if len(records_missing) == 1:
        raise ValueError("Agenda/Access Matrix initialization is incomplete; inspect the selected scope")
    if len(catalogs_missing) == 1:
        raise ValueError("Agenda/access-decision catalog installation is incomplete; inspect the selected scope")
    missing = records_missing + catalogs_missing
    _load(root)
    preserve = [relative for relative in SEEDS if relative not in missing]
    preserve_hashes = {relative: hashlib.sha256(records.safe(root, relative).read_bytes()).hexdigest()
                       for relative in preserve}
    result = {"applied": False, "add": missing, "preserve": [relative for relative in (AGENDA, ACCESS)
                                                         if relative not in missing] +
              [relative for relative in (SETTING_CATALOG, DECISION_CATALOG) if relative not in missing],
              "catalogsInstalled": not catalogs_missing,
              "runtimeStarted": False, "accessGranted": False}
    if not apply or not missing:
        return result
    _alpha_active(root)
    with memory.coordination_lock(root):
        if any(records.safe(root, relative).exists() for relative in missing):
            raise ValueError("Agenda initialization changed during preview; retry after inspection")
        if any(hashlib.sha256(records.safe(root, relative).read_bytes()).hexdigest() != digest
               for relative, digest in preserve_hashes.items()):
            raise ValueError("Agenda initialization changed existing records during preview; retry")
        for relative in missing:
            records.write(root, relative, seeds[relative])
    return {**result, "applied": True, "catalogsInstalled": True}


def status(root):
    agenda, access = _load(root)
    catalogs = _catalog_pair(root)
    catalog_status = {"catalogsInstalled": catalogs is not None,
                      "settingDefinitions": len(catalogs[SETTING_CATALOG]["settings"]) if catalogs else 0,
                      "decisionRules": len(catalogs[DECISION_CATALOG]["rules"]) if catalogs else 0,
                      "defaultContextState": "unset" if catalogs else None,
                      "defaultAccessState": "no-row" if catalogs else None}
    if agenda is None:
        return {"initialized": False, "agendaOptions": 0, "accessDecisions": 0,
                "roleDefaults": 0,
                "agendaRevision": None, "accessRevision": None, "staleRules": 0,
                "accessConflicts": 0,
                **catalog_status,
                "executed": False, "accessGranted": False}
    stale = sum(_rule_digest(root, row["providerRulesPath"]) != row["providerRulesSha256"]
                for row in agenda["options"])
    by_id = {row["id"]: row for row in access["decisions"]}
    conflicts = sum(row["value"] == "include" and
                    by_id[row["accessDecisionId"]]["decision"] != "reviewed-intent"
                    for row in agenda["options"])
    return {"initialized": True, "agendaOptions": len(agenda["options"]),
            "accessDecisions": len(access["decisions"]), "agendaRevision": records.fingerprint(agenda),
            "roleDefaults": len(access.get("roleDefaults", [])),
            "accessRevision": records.fingerprint(access), "staleRules": stale,
            "accessConflicts": conflicts,
            **catalog_status,
            "executed": False, "accessGranted": False}


def catalog(root, defaults):
    """Read definitions, including a clearly marked preview for beta.1 scopes."""
    agenda, access = _load(root)
    installed = _catalog_pair(root)
    definitions = installed or _blank_seeds(defaults)
    return {"installed": installed is not None,
            "source": "selected-scope" if installed else "distribution-preview",
            "settingCatalog": definitions[SETTING_CATALOG],
            "decisionCatalog": definitions[DECISION_CATALOG],
            "agendaOptions": len(agenda["options"]) if agenda else 0,
            "accessDecisions": len(access["decisions"]) if access else 0,
            "executed": False, "identityVerified": False, "accessGranted": False}


def _csv_cell(value):
    value = "; ".join(value) if isinstance(value, list) else str(value)
    # A generated CSV may be opened in Excel; make untrusted formula-like text inert.
    if value.lstrip().startswith(("=", "+", "-", "@")):
        value = "'" + value
    return value


def _csv(columns, rows):
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(columns)
    for row in rows:
        writer.writerow([_csv_cell(row[column]) for column in columns])
    return output.getvalue()


def table(root, format="json"):
    if format not in ("json", "csv"):
        raise ValueError("Agenda table format must be json or csv")
    agenda, access = _load(root)
    catalogs = _catalog_pair(root)
    initialized = agenda is not None
    agenda = agenda or {"schemaVersion": 1, "options": []}
    access = access or {"schemaVersion": 1, "decisions": []}
    by_id = {row["id"]: row for row in access["decisions"]}
    rows = []
    for option in agenda["options"]:
        decision = by_id.get(option["accessDecisionId"])
        rows.append({**option, "accessDecision": decision["decision"] if decision else "",
                     "accessOwner": decision["owner"] if decision else "",
                     "accessConflict": option["value"] == "include" and
                                       decision["decision"] != "reviewed-intent",
                     "rulesCurrent": _rule_digest(root, option["providerRulesPath"]) ==
                                     option["providerRulesSha256"]})
    result = {"initialized": initialized, "agendaColumns": list(TABLE_COLUMNS),
              "accessColumns": list(ACCESS_COLUMNS), "agendaRows": rows,
              "accessRows": access["decisions"], "roleColumns": list(ROLE_COLUMNS),
              "roleRows": access.get("roleDefaults", []),
              "catalogsInstalled": catalogs is not None,
              "settingColumns": list(SETTING_COLUMNS),
              "settingRows": catalogs[SETTING_CATALOG]["settings"] if catalogs else [],
              "decisionRuleColumns": list(DECISION_RULE_COLUMNS),
              "decisionRuleRows": catalogs[DECISION_CATALOG]["rules"] if catalogs else [],
              "executed": False, "accessGranted": False}
    if format == "csv":
        return {"format": "csv", "agendaCsv": _csv(TABLE_COLUMNS, rows),
                "accessCsv": _csv(ACCESS_COLUMNS, access["decisions"]),
                "roleCsv": _csv(ROLE_COLUMNS, access.get("roleDefaults", [])),
                "catalogsInstalled": catalogs is not None,
                "settingCsv": _csv(SETTING_COLUMNS, result["settingRows"]),
                "decisionRuleCsv": _csv(DECISION_RULE_COLUMNS, result["decisionRuleRows"]),
                "executed": False, "accessGranted": False}
    return {"format": "json", **result}


def _decision_actor(root, actor):
    """Bind a decision to a fixed role or a named selected-scope instance."""
    _string(actor, "Access Matrix actor", maximum=160)
    fixed = {row["actor"] for row in ROLE_DEFAULTS if row["kind"] in {"agent", "autobot"}}
    registered = None
    if actor.startswith("agent."):
        _, registry = memory.load(Path(root))
        registered = {item["id"]: item["role"] for item in registry["agents"]}
    if actor in fixed:
        if actor.startswith("agent.") and actor not in registered:
            raise ValueError("Register this agent in the selected scope before recording its decision")
        if actor == "agent.1" and registered[actor] != "security-access":
            return "numeric-instance"
        return "fixed"
    if re.fullmatch(r"agent\.[1-9][0-9]*", actor):
        if actor not in registered:
            raise ValueError("Register this numeric worker in the selected scope first")
        return "numeric-instance"
    if re.fullmatch(r"native-subagent:[a-z][a-z0-9-]{0,31}:[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", actor):
        return "native-instance"
    if re.fullmatch(r"agentb:[A-Z][A-Z0-9_]{0,31}", actor):
        import agent_beta
        name = actor.split(":", 1)[1]
        if name not in {item["name"] for item in agent_beta.load_bots(root)["bots"]}:
            raise ValueError("Record this BOT/DOT instance in the selected scope first")
        return "bot-instance"
    raise ValueError("Actor must be a fixed role, registered numeric worker, native-subagent:HOST:ID, or agentb:BOT_NAME")


def add_decision(root, args):
    agenda, access = _load(root)
    if agenda is None:
        raise ValueError("Initialize Agenda and Access Matrix in this scope first")
    before = records.fingerprint(access)
    if args.expected_revision != before:
        raise ValueError("Access Matrix changed since the observed revision; inspect current status")
    actor_kind = _decision_actor(root, args.actor)
    decision_action = getattr(args, "decision_action", None) or args.action
    row = {"id": args.id, "actor": args.actor, "resource": args.resource,
           "action": decision_action, "environment": args.environment,
           "decision": args.decision, "owner": args.owner,
           "policyRef": args.policy_ref, "evidence": args.evidence,
           "reviewedAt": args.reviewed_at, "recheck": args.recheck}
    if row["decision"] == "reviewed-intent" and not row["policyRef"]:
        raise ValueError("Reviewed intent requires a non-secret policy reference")
    if any(item["id"] == row["id"] for item in access["decisions"]):
        raise ValueError("Access Matrix ID already exists; use a new ID")
    key = (row["actor"], row["resource"], row["action"], row["environment"])
    if any((item["actor"], item["resource"], item["action"], item["environment"]) == key
           for item in access["decisions"]):
        raise ValueError("A decision for this actor/resource/action/environment already exists")
    proposed = {**access, "decisions": [*access["decisions"], row]}
    validate_access(proposed)
    result = {"applied": False, "id": row["id"], "actor": row["actor"],
              "actorKind": actor_kind, "resource": row["resource"],
              "action": row["action"], "environment": row["environment"],
              "decision": row["decision"], "owner": row["owner"],
              "policyRef": row["policyRef"], "reviewedAt": row["reviewedAt"],
              "recheck": row["recheck"], "evidenceCount": len(row["evidence"]),
              "revisionBefore": before, "revisionAfter": records.fingerprint(proposed),
              "identityVerified": False, "executed": False, "accessGranted": False}
    if not args.apply:
        return result
    with memory.coordination_lock(root):
        current_agenda, current_access = _load(root)
        if records.fingerprint(current_access) != before:
            raise ValueError("Access Matrix changed before apply; review and retry")
        _decision_actor(root, args.actor)
        if current_agenda is None:
            raise ValueError("Agenda/Access Matrix disappeared before apply")
        records.write(root, ACCESS, proposed)
    return {**result, "applied": True}


def upgrade_roles(root, args):
    """Add the fixed catalog to a legacy selected scope without changing decisions."""
    agenda, access = _load(root)
    if agenda is None:
        raise ValueError("Initialize Agenda and Access Matrix in this scope first")
    before = records.fingerprint(access)
    if args.expected_revision != before:
        raise ValueError("Access Matrix changed since the observed revision; inspect current status")
    changed = "roleDefaults" not in access
    proposed = ({"schemaVersion": 1, "roleDefaults": list(ROLE_DEFAULTS),
                 "decisions": access["decisions"]} if changed else access)
    validate_access(proposed)
    result = {"applied": False, "changed": changed, "decisionsPreserved": len(access["decisions"]),
              "roleDefaults": len(proposed["roleDefaults"]), "revisionBefore": before,
              "revisionAfter": records.fingerprint(proposed),
              "executed": False, "accessGranted": False}
    if not args.apply or not changed:
        return result
    with memory.coordination_lock(root):
        _, current = _load(root)
        if records.fingerprint(current) != before:
            raise ValueError("Access Matrix changed before apply; review and retry")
        records.write(root, ACCESS, proposed)
    return {**result, "applied": True}


def _workbook_target(root, output):
    """Constrain generated workbooks to ignored selected-scope local data."""
    root = Path(root)
    candidate = Path(output or WORKBOOK_DEFAULT)
    if candidate.is_absolute():
        try:
            candidate = candidate.relative_to(root)
        except ValueError as error:
            raise ValueError("Workbook output must be inside selected-scope local/") from error
    relative = candidate.as_posix()
    if (not relative.startswith("local/") or len(candidate.parts) < 2 or
            candidate.suffix.lower() != ".xlsx"):
        raise ValueError("Workbook output must be an .xlsx file inside selected-scope local/")
    return relative, records.safe(root, relative)


def _xml_text(value):
    if isinstance(value, list):
        value = "; ".join(value)
    if isinstance(value, bool):
        return "Yes" if value else "No"
    value = str(value)
    return "".join(char if char in "\t\n\r" or 0x20 <= ord(char) <= 0xD7FF or
                   0xE000 <= ord(char) <= 0xFFFD or 0x10000 <= ord(char) <= 0x10FFFF
                   else "\uFFFD" for char in value)


def _sheet_xml(title, note, revision, columns, rows):
    namespace = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    q = lambda name: "{" + namespace + "}" + name
    ET.register_namespace("", namespace)
    worksheet = ET.Element(q("worksheet"))
    last_column = chr(ord("A") + len(columns) - 1)
    ET.SubElement(worksheet, q("dimension"), {"ref": "A1:{}{}".format(last_column, max(5, 5 + len(rows)))})
    views = ET.SubElement(worksheet, q("sheetViews"))
    view = ET.SubElement(views, q("sheetView"), {"workbookViewId": "0", "showGridLines": "0"})
    ET.SubElement(view, q("pane"), {"ySplit": "5", "topLeftCell": "A6",
                                      "activePane": "bottomLeft", "state": "frozen"})
    ET.SubElement(worksheet, q("sheetFormatPr"), {"defaultRowHeight": "18"})
    widths = ET.SubElement(worksheet, q("cols"))
    for index, header in enumerate(columns, 1):
        width = 43 if header in {"instanceRule", "purpose", "resource", "providerRulesPath"} else 29
        ET.SubElement(widths, q("col"), {"min": str(index), "max": str(index),
                                           "width": str(width), "customWidth": "1"})
    data = ET.SubElement(worksheet, q("sheetData"))

    def row(number, values, style=0, height=None):
        attributes = {"r": str(number)}
        if height is not None:
            attributes.update({"ht": str(height), "customHeight": "1"})
        element = ET.SubElement(data, q("row"), attributes)
        for index, value in enumerate(values):
            if value is None or value == "":
                continue
            cell = ET.SubElement(element, q("c"), {"r": chr(ord("A") + index) + str(number),
                                                    "s": str(style),
                                                    "t": "b" if isinstance(value, bool) else "inlineStr"})
            if isinstance(value, bool):
                ET.SubElement(cell, q("v")).text = "1" if value else "0"
            else:
                ET.SubElement(ET.SubElement(cell, q("is")), q("t")).text = _xml_text(value)

    row(1, [title], 2, 30)
    row(2, [note], 3, 24)
    row(3, ["Source revision: " + revision], 3, 24)
    row(5, columns, 1, 32)
    for number, item in enumerate(rows, 6):
        row(number, [item[column] for column in columns], 0, 30)
    ET.SubElement(worksheet, q("autoFilter"), {"ref": "A5:{}{}".format(last_column, max(5, 5 + len(rows)))})
    return ET.tostring(worksheet, encoding="utf-8", xml_declaration=True)


def _xlsx_bytes(root, agenda, access, roster=None):
    """Render one deterministic, formula-free OOXML view from canonical JSON."""
    # Import here because ROOT is an optional read-only view. Its roster owns
    # actor discovery; this module does not infer instances from role patterns.
    import root_coordination

    catalogs = _catalog_pair(root)
    roster = root_coordination.roster(root) if roster is None else roster
    by_id = {row["id"]: row for row in access["decisions"]}
    options = []
    rules_state = []
    for option in agenda["options"]:
        decision = by_id.get(option["accessDecisionId"])
        current_digest = _rule_digest(root, option["providerRulesPath"])
        rules_state.append((option["id"], current_digest))
        options.append({**option, "accessDecision": decision["decision"] if decision else "",
                        "accessOwner": decision["owner"] if decision else "",
                        "accessConflict": option["value"] == "include" and
                                          decision["decision"] != "reviewed-intent",
                        "rulesCurrent": current_digest == option["providerRulesSha256"]})
    revision = records.fingerprint({"agenda": agenda, "access": access,
                                    "catalogs": catalogs, "rulesState": rules_state,
                                    "rosterRevision": roster["sourceRevision"]})
    sheets = (
        ("Role defaults", "Fixed role catalog. No template grants or automatic instance permissions.",
         ROLE_COLUMNS, access.get("roleDefaults", [])),
        ("Access decisions", "Selected-scope reviewed intent, denial, or gap. A row never grants access.",
         ACCESS_COLUMNS, access["decisions"]),
        ("Agenda options", "Advisory context selection only; no bot execution or permission change.",
         TABLE_COLUMNS, options),
        ("Setting definitions", "Stock values are unset; no advisory context is selected until review.",
         SETTING_COLUMNS, catalogs[SETTING_CATALOG]["settings"] if catalogs else []),
        ("Decision rules", "No row means no grant; recorded decisions never verify external permission.",
         DECISION_RULE_COLUMNS, catalogs[DECISION_CATALOG]["rules"] if catalogs else []),
        ("Agent 0 roster", "Selected-scope actor inventory. Registration and reviewed intent do not verify external rights.",
         ROSTER_COLUMNS, roster["rows"]),
    )
    content_types = ('<?xml version="1.0" encoding="UTF-8"?>'
                     '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                     '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                     '<Default Extension="xml" ContentType="application/xml"/>'
                     '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
                     '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
                     + ''.join('<Override PartName="/xl/worksheets/sheet{}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'.format(index)
                               for index in range(1, len(sheets) + 1)) + '</Types>').encode("utf-8")
    rels = ('<?xml version="1.0" encoding="UTF-8"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
            '</Relationships>').encode("utf-8")
    workbook = ('<?xml version="1.0" encoding="UTF-8"?>'
                '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                '<sheets>' + ''.join('<sheet name="{}" sheetId="{}" r:id="rId{}"/>'.format(name, index, index)
                                   for index, (name, _, _, _) in enumerate(sheets, 1)) +
                '</sheets></workbook>').encode("utf-8")
    workbook_rels = ('<?xml version="1.0" encoding="UTF-8"?>'
                     '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                     + ''.join('<Relationship Id="rId{}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{}.xml"/>'.format(index, index)
                               for index in range(1, len(sheets) + 1)) +
                     '<Relationship Id="rId{}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'.format(len(sheets) + 1) +
                     '</Relationships>').encode("utf-8")
    styles = ('<?xml version="1.0" encoding="UTF-8"?>'
              '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
              '<fonts count="4"><font><sz val="10"/><name val="Arial"/></font>'
              '<font><b/><sz val="10"/><color rgb="FFFFFFFF"/><name val="Arial"/></font>'
              '<font><b/><sz val="14"/><color rgb="FF13273D"/><name val="Arial"/></font>'
              '<font><sz val="10"/><color rgb="FF64748B"/><name val="Arial"/></font></fonts>'
              '<fills count="3"><fill><patternFill patternType="none"/></fill>'
              '<fill><patternFill patternType="gray125"/></fill>'
              '<fill><patternFill patternType="solid"><fgColor rgb="FF1F4E78"/><bgColor indexed="64"/></patternFill></fill></fills>'
              '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
              '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
              '<cellXfs count="4"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/>'
              '<xf numFmtId="0" fontId="1" fillId="2" borderId="0" applyFont="1" applyFill="1"/>'
              '<xf numFmtId="0" fontId="2" fillId="0" borderId="0" applyFont="1"/>'
              '<xf numFmtId="0" fontId="3" fillId="0" borderId="0" applyFont="1"/></cellXfs>'
              '</styleSheet>').encode("utf-8")
    parts = [("[Content_Types].xml", content_types), ("_rels/.rels", rels),
             ("xl/workbook.xml", workbook), ("xl/_rels/workbook.xml.rels", workbook_rels),
             ("xl/styles.xml", styles)]
    for index, (name, note, columns, rows) in enumerate(sheets, 1):
        parts.append(("xl/worksheets/sheet{}.xml".format(index),
                      _sheet_xml(name, note, revision, columns, rows)))
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        for name, content in parts:
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED
            info.external_attr = 0o600 << 16
            archive.writestr(info, content)
    output = stream.getvalue()
    if len(output) > MAX_WORKBOOK_BYTES:
        raise ValueError("Generated workbook exceeds its 32 MiB limit")
    return revision, output


def _workbook_state(path, expected):
    if not path.exists():
        return False, False, None
    if path.stat().st_size > MAX_WORKBOOK_BYTES:
        raise ValueError("Existing workbook exceeds its 32 MiB limit")
    actual = path.read_bytes()
    return True, actual == expected, hashlib.sha256(actual).hexdigest()


def workbook_check(root, output=None):
    relative, path = _workbook_target(root, output)
    agenda, access = _load(root)
    if agenda is None:
        raise ValueError("Initialize Agenda and Access Matrix in this scope first")
    catalogs = _catalog_pair(root)
    import root_coordination
    roster = root_coordination.roster(root)
    revision, expected = _xlsx_bytes(root, agenda, access, roster)
    exists, current, actual_digest = _workbook_state(path, expected)
    return {"output": relative, "exists": exists, "current": current,
            "sourceRevision": revision, "expectedSha256": hashlib.sha256(expected).hexdigest(),
            "actualSha256": actual_digest, "agendaOptions": len(agenda["options"]),
            "accessDecisions": len(access["decisions"]),
            "roleDefaults": len(access.get("roleDefaults", [])),
            "catalogsInstalled": catalogs is not None,
            "settingDefinitions": len(catalogs[SETTING_CATALOG]["settings"]) if catalogs else 0,
            "decisionRules": len(catalogs[DECISION_CATALOG]["rules"]) if catalogs else 0,
            "rosterActors": len(roster["rows"]), "rosterSourceRevision": roster["sourceRevision"],
            "executed": False, "accessGranted": False}


def workbook_export(root, args):
    root = Path(root)
    relative, path = _workbook_target(root, args.output)
    preview = workbook_check(root, args.output)
    result = {**preview, "applied": False, "wouldChange": not preview["current"]}
    if not args.apply or preview["current"]:
        return result
    if args.expected_revision != preview["sourceRevision"]:
        raise ValueError("Workbook source changed since preview; inspect current status")
    with memory.coordination_lock(root):
        agenda, access = _load(root)
        revision, expected = _xlsx_bytes(root, agenda, access)
        if revision != args.expected_revision:
            raise ValueError("Workbook source changed before apply; preview again")
        _, path = _workbook_target(root, relative)
        exists, current, _ = _workbook_state(path, expected)
        if current:
            return {**result, "exists": exists, "current": True, "wouldChange": False}
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="wb", dir=path.parent, delete=False) as stream:
                temporary = Path(stream.name)
                os.chmod(temporary, 0o600)
                stream.write(expected)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()
    return {**result, "applied": True, "exists": True, "current": True,
            "actualSha256": result["expectedSha256"]}


def set_option(root, args):
    _alpha_active(root)
    agenda, access = _load(root)
    if agenda is None:
        raise ValueError("Initialize Agenda in this scope before setting an option")
    if args.expected_revision != records.fingerprint(agenda):
        raise ValueError("Agenda changed since the observed revision; inspect current status")
    rules = _rules_path(root, args.provider_rules, require_file=True)
    row = {"id": args.id, "botId": args.bot, "setting": "context_selection", "value": args.value,
           "providerRulesPath": args.provider_rules,
           "providerRulesSha256": hashlib.sha256(rules.read_bytes()).hexdigest(),
           "accessDecisionId": args.access_decision_id, "reason": args.reason,
           "reviewedAt": args.reviewed_at, "evidence": args.evidence}
    if row["value"] == "include":
        decision = next((item for item in access["decisions"] if item["id"] == row["accessDecisionId"]), None)
        if decision is None or decision["decision"] != "reviewed-intent":
            raise ValueError("Agenda include requires a reviewed-intent Access Matrix decision")
    existing = next((item for item in agenda["options"] if item["id"] == args.id), None)
    if existing and (existing["botId"], existing["setting"]) != (row["botId"], row["setting"]):
        raise ValueError("Agenda ID already belongs to a different option")
    proposed = {"schemaVersion": 1, "options": [row if item["id"] == args.id else item
                                               for item in agenda["options"]]}
    if existing is None:
        proposed["options"].append(row)
    validate_agenda(proposed, access, root)
    changed = proposed != agenda
    result = {"applied": False, "changed": changed, "revisionBefore": records.fingerprint(agenda),
              "revisionAfter": records.fingerprint(proposed), "option": row,
              "executed": False, "accessGranted": False}
    if not args.apply or not changed:
        return result
    with memory.coordination_lock(root):
        current, current_access = _load(root)
        if records.fingerprint(current) != args.expected_revision or records.fingerprint(current_access) != records.fingerprint(access):
            raise ValueError("Agenda or Access Matrix changed before apply; review and retry")
        if _rule_digest(root, args.provider_rules) != row["providerRulesSha256"]:
            raise ValueError("Provider rules changed before apply; review and retry")
        records.write(root, AGENDA, proposed)
    return {**result, "applied": True}


def add_cli(subparsers, scope=None):
    scope = scope or (lambda parser: parser)
    parent = subparsers.add_parser("agenda", help=__doc__)
    commands = parent.add_subparsers(dest="agenda_action", required=True)
    command = scope(commands.add_parser("init", help="preview or add blank records and fixed catalogs"))
    command.add_argument("--apply", action="store_true")
    scope(commands.add_parser("status", help="read-only option and access summary"))
    scope(commands.add_parser("catalog", help="read-only stock settings, values, and decision rules"))
    command = scope(commands.add_parser("table", help="read-only Agenda/Access Matrix table export"))
    command.add_argument("--format", choices=("json", "csv"), default="json")
    command = scope(commands.add_parser("set", help="preview or record one advisory context-selection option"))
    command.add_argument("--id", required=True)
    command.add_argument("--bot", required=True)
    command.add_argument("--value", choices=("include", "exclude"), required=True)
    command.add_argument("--provider-rules", required=True)
    command.add_argument("--access-decision-id", default="")
    command.add_argument("--reason", required=True)
    command.add_argument("--reviewed-at", required=True)
    command.add_argument("--evidence", action="append", required=True)
    command.add_argument("--expected-revision", required=True)
    command.add_argument("--apply", action="store_true")
    command = scope(commands.add_parser("roles-upgrade", help="preview or add fixed role defaults to a legacy scope"))
    command.add_argument("--expected-revision", required=True)
    command.add_argument("--apply", action="store_true")
    command = scope(commands.add_parser("workbook-check", help="compare selected-scope XLSX view with current JSON"))
    command.add_argument("--output", default=WORKBOOK_DEFAULT,
                         help=".xlsx path inside selected-scope local/")
    command = scope(commands.add_parser("workbook-export", help="preview or write a formula-free XLSX view in local/"))
    command.add_argument("--output", default=WORKBOOK_DEFAULT,
                         help=".xlsx path inside selected-scope local/")
    command.add_argument("--expected-revision", default="",
                         help="sourceRevision from workbook-export preview; required with --apply")
    command.add_argument("--apply", action="store_true")
    command = scope(commands.add_parser("decision-add", help="preview or record one selected-scope access decision"))
    command.add_argument("--id", required=True)
    command.add_argument("--actor", required=True)
    command.add_argument("--resource", required=True)
    # Keep the top-level CLI action ('agenda') separate from this matrix field.
    command.add_argument("--action", dest="decision_action", required=True)
    command.add_argument("--environment", required=True)
    command.add_argument("--decision", choices=DECISIONS, required=True)
    command.add_argument("--owner", required=True)
    command.add_argument("--policy-ref", default="")
    command.add_argument("--evidence", action="append", required=True)
    command.add_argument("--reviewed-at", required=True)
    command.add_argument("--recheck", default="")
    command.add_argument("--expected-revision", required=True)
    command.add_argument("--apply", action="store_true")


def dispatch(root, defaults, args):
    action = args.agenda_action
    if action == "init":
        result = initialize(root, defaults, args.apply)
    elif action == "status":
        result = status(root)
    elif action == "catalog":
        result = catalog(root, defaults)
    elif action == "table":
        result = table(root, args.format)
    elif action == "set":
        result = set_option(root, args)
    elif action == "decision-add":
        result = add_decision(root, args)
    elif action == "roles-upgrade":
        result = upgrade_roles(root, args)
    elif action == "workbook-check":
        result = workbook_check(root, args.output)
    elif action == "workbook-export":
        result = workbook_export(root, args)
    else:
        raise ValueError("Unknown Agenda action")
    result.setdefault("scope", str(root))
    return result
