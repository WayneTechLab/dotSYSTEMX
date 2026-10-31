"""One bounded, read-only status packet for a selected SYSTEMX record scope.

This combines existing owners' status views. It does not make an access
decision, read rules content into the result, start a bot, or execute a check.
"""

import hashlib
from pathlib import Path

import agent_beta
import agent_standards as records
import agenda_access
import autobots
import project_memory as memory
import security_agent1


COMMANDS = {"session-settings"}
REQUIRED = ("scripts/session_settings.py", "tests/test_session_settings.py")
MAX_RULE_BYTES = 256 * 1024
MAX_TOTAL_RULE_BYTES = 32 * 1024 * 1024


def _scope(root):
    root = Path(root)
    if root.name == ".SYSTEMX":
        return {"kind": "root", "name": ".SYSTEMX"}
    if root.name == ".SYSTEMXP":
        return {"kind": "project", "name": root.parent.name}
    raise ValueError("Select an exact-case .SYSTEMX or .SYSTEMXP record scope")


def _rule(root, relative, owner, identifier, budget):
    path = records.safe(root, relative)
    if not path.exists():
        return {"owner": owner, "id": identifier, "path": relative,
                "state": "absent", "sha256": None, "bytes": 0}
    if not path.is_file():
        raise ValueError("Canonical rules path is not a regular file: " + relative)
    size = path.stat().st_size
    if size > MAX_RULE_BYTES or budget[0] + size > MAX_TOTAL_RULE_BYTES:
        raise ValueError("Canonical rules exceed the bounded status read")
    digest = hashlib.sha256()
    count = 0
    with path.open("rb") as stream:
        while True:
            chunk = stream.read(64 * 1024)
            if not chunk:
                break
            count += len(chunk)
            if count > MAX_RULE_BYTES or budget[0] + count > MAX_TOTAL_RULE_BYTES:
                raise ValueError("Canonical rules changed or exceeded the bounded status read")
            digest.update(chunk)
    if count != size or path.stat().st_size != size:
        raise ValueError("Canonical rules changed during status read")
    budget[0] += count
    return {"owner": owner, "id": identifier, "path": relative,
            "state": "present", "sha256": digest.hexdigest(), "bytes": count}


def status(root, defaults=None, *, compact=False):
    """Aggregate local metadata without exposing configuration or rule text."""
    root = Path(root)
    identity = _scope(root)
    # The existing role and optional-record validators retain their ownership.
    memory.load(root)
    agent_beta.validate_optional(root)
    agenda_access.validate_optional(root)
    bot_index = (agent_beta.load_bots(root) if records.safe(root, "AGENTB/BOTS.json").is_file()
                 else {"schemaVersion": 1, "bots": []})
    _, registry = memory.load(root)
    beta_registered = any(item["id"] == agent_beta.AGENT for item in registry["agents"])

    security = security_agent1.status(root)
    registration = security["registration"]
    agenda = agenda_access.status(root)
    budget = [0]
    rules = [_rule(root, "AUTOBOT/" + filename, "agent.a", "autobot." + slug, budget)
             for slug, _name, filename in autobots.SLOTS]
    for bot in sorted(bot_index["bots"], key=lambda item: item["name"]):
        rules.append(_rule(root, bot["path"] + "/Rules.MD", "agent.b",
                           "agentb." + bot["name"], budget))

    result = {"schemaVersion": 1, "scope": identity,
            "agentBeta": {"registered": beta_registered, "botCount": len(bot_index["bots"]),
                          "activeConnections": 0},
            "agent1": {"configured": security["configured"],
                       "registered": registration["registered"],
                       "roleConflict": registration["conflict"],
                       "missingQuestionCount": len(security["missingQuestions"]),
                       "mode": "warning-only"},
            "agenda": {"initialized": agenda["initialized"],
                       "optionCount": agenda["agendaOptions"],
                       "accessDecisionCount": agenda["accessDecisions"],
                       "catalogsInstalled": agenda["catalogsInstalled"],
                       "settingDefinitions": agenda["settingDefinitions"],
                       "decisionRules": agenda["decisionRules"],
                       "defaultContextState": agenda["defaultContextState"],
                       "defaultAccessState": agenda["defaultAccessState"],
                       "agendaRevision": agenda["agendaRevision"],
                       "accessRevision": agenda["accessRevision"],
                       "staleRules": agenda["staleRules"],
                       "accessConflicts": agenda["accessConflicts"]},
            "canonicalRules": rules,
            "rulesReadBytes": budget[0], "executed": False, "accessGranted": False,
            "limit": "Selected-scope metadata and rules hashes only; no rule content, secret value, "
                     "provider account, OS permission, bot session, or live cloud state was verified."}
    if compact:
        # Keep the full view available for diagnostics. A coordinator can use
        # this revision to notice changed rule metadata without loading ten
        # individual path/hash records into every new model session.
        result.pop("canonicalRules")
        result["rulesSummary"] = {
            "count": len(rules),
            "absent": [item["id"] for item in rules if item["state"] == "absent"],
            "revision": records.fingerprint(rules),
        }
    return result


def add_cli(subparsers, scope=None):
    scope = scope or (lambda parser: parser)
    command = scope(subparsers.add_parser("session-settings", help="read-only scoped agent, agenda, and rules hash status"))
    command.add_argument("--compact", action="store_true",
                         help="summarize rules by revision for a smaller model context packet")


def dispatch(root, defaults, args):
    return status(root, defaults, compact=args.compact)
