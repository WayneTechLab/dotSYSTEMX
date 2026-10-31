"""Explicit stdio session for read-only SYSTEMX checks.

The invoking CLI or IDE owns this process. It has no listener, daemon install,
shell execution, credential store, or writable state. EOF ends the session.
This fixed JSON-lines protocol is not MCP or ACP.
"""

import json
from pathlib import Path
import re
import sys


COMMANDS = {"service"}
REQUIRED = ("scripts/session_service.py", "tests/test_session_service.py", "Setup/SERVICE.md")
MAX_LINE_BYTES = 16 * 1024
MAX_RESPONSE_BYTES = 512 * 1024
MAX_REQUESTS = 64
REQUEST_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}\Z")
METHODS = ("ping", "capabilities", "assess", "roster", "settings", "onboard", "stop")


def add_cli(subparsers, scope=None):
    """Register the same command under root and explicitly selected projects."""
    scope = scope or (lambda parser: parser)
    parent = subparsers.add_parser("service", help="optional read-only stdio session")
    commands = parent.add_subparsers(dest="service_action", required=True)
    scope(commands.add_parser("status", help="show session transport capabilities"))
    start = scope(commands.add_parser("start", help="run a bounded stdio session until EOF"))
    start.add_argument("--stdio", action="store_true", required=True,
                       help="explicitly select JSON-lines standard input/output transport")


def _scope(root):
    root = Path(root)
    if root.name not in {".SYSTEMX", ".SYSTEMXP"} or root.is_symlink() or not root.is_dir():
        raise ValueError("Select a real exact-case .SYSTEMX or .SYSTEMXP record directory")
    if root.name == ".SYSTEMXP":
        siblings = [item.name for item in root.parent.iterdir()
                    if item.name.casefold() == ".systemxp"]
        if siblings != [".SYSTEMXP"]:
            raise ValueError("Selected project record directory has an exact-case conflict")
    else:
        from systemx_paths import inspect_layout
        inspect_layout(root.parent, required=True)
    return root


def status(root):
    """Describe capability, not host installation or a running background job."""
    selected = _scope(root)
    return {"schemaVersion": 1, "kind": "systemx-session-service",
            "scope": str(selected), "transport": "stdio-json-lines",
            "state": "available-on-explicit-start", "persistentInstall": False,
            "networkListener": False, "requiresElevation": False,
            "hostPrivileges": "inherited-from-launcher", "writes": False,
            "methods": list(METHODS), "maxRequestBytes": MAX_LINE_BYTES,
            "maxRequests": MAX_REQUESTS,
            "platform": "Python 3.9+ on macOS, Windows, or Linux; host integration not asserted"}


def _unique(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("Duplicate JSON request field")
        value[key] = item
    return value


def _invalid_number(value):
    raise ValueError("Non-finite JSON request number")


def _request(line):
    if len(line) > MAX_LINE_BYTES or not line.endswith(b"\n"):
        raise ValueError("Request exceeds the bounded line protocol")
    try:
        value = json.loads(line.decode("utf-8"), object_pairs_hook=_unique,
                           parse_constant=_invalid_number)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise ValueError("Invalid JSON request") from error
    if not isinstance(value, dict) or set(value) != {"id", "method"}:
        raise ValueError("Request must contain exactly id and method")
    if not isinstance(value["id"], str) or not REQUEST_ID.fullmatch(value["id"]):
        raise ValueError("Request id must be a bounded ASCII token")
    if value["method"] not in METHODS:
        raise ValueError("Unsupported read-only method")
    return value


def _respond(output, identifier, *, result=None, error=None):
    response = {"id": identifier, "ok": error is None}
    if error is None:
        response["result"] = result
    else:
        response["error"] = error
    try:
        content = json.dumps(response, ensure_ascii=False, allow_nan=False,
                             separators=(",", ":")).encode("utf-8")
    except (TypeError, ValueError):
        content = json.dumps({"id": identifier, "ok": False,
                              "error": "Read-only result could not be encoded"},
                             separators=(",", ":")).encode("utf-8")
    if len(content) > MAX_RESPONSE_BYTES:
        content = json.dumps({"id": identifier, "ok": False,
                              "error": "Read-only result exceeds response limit"},
                             separators=(",", ":")).encode("utf-8")
    output.write(content + b"\n")
    output.flush()


def _assess(root, defaults):
    # The single supported assessment has no caller-supplied path, command, or
    # credential. Agent1 owns its sanitized, bounded read-only result.
    import security_agent1
    return security_agent1.assess(root, defaults, profile="all-in-one")


def _roster(root):
    # Agent 0 owns this local, bounded role/instance view. It reports recorded
    # decisions but never verifies an external permission or starts a worker.
    import root_coordination
    return root_coordination.roster(root)


def _settings(root, defaults):
    # The compact form carries rule hashes and revision rather than rule text.
    import session_settings
    return session_settings.status(root, defaults, compact=True)


def _onboard(root):
    # No provider, dotenv file, account, or credential is selected by a packet.
    import onboarding
    return onboarding.view(root)


def serve(root, defaults, input_stream, output_stream):
    """Serve bounded requests. No session file, listening socket, or process spawn."""
    selected = _scope(root)
    handled = 0
    while handled < MAX_REQUESTS:
        line = input_stream.readline(MAX_LINE_BYTES + 1)
        if not line:
            return {"ended": "eof", "requestsHandled": handled}
        handled += 1
        try:
            request = _request(line)
        except ValueError as error:
            _respond(output_stream, None, error=str(error))
            if len(line) > MAX_LINE_BYTES or not line.endswith(b"\n"):
                return {"ended": "protocol-limit", "requestsHandled": handled}
            continue
        method, identifier = request["method"], request["id"]
        try:
            if method == "ping":
                result = {"alive": True}
            elif method == "capabilities":
                result = status(selected)
            elif method == "assess":
                result = _assess(selected, defaults)
            elif method == "roster":
                result = _roster(selected)
            elif method == "settings":
                result = _settings(selected, defaults)
            elif method == "onboard":
                result = _onboard(selected)
            else:
                result = {"ended": "requested"}
            _respond(output_stream, identifier, result=result)
        except Exception:
            # Exceptions from local checks may include private path details.
            # Return a bounded generic failure; the direct CLI has diagnostics.
            _respond(output_stream, identifier,
                     error="Read-only method unavailable; run the selected direct CLI for diagnostics")
        if method == "stop":
            return {"ended": "requested", "requestsHandled": handled}
    return {"ended": "request-limit", "requestsHandled": handled}


def dispatch(root, defaults, args):
    if args.service_action == "status":
        return status(root)
    if not args.stdio or sys.stdin.isatty() or sys.stdout.isatty():
        raise ValueError("service start requires explicit --stdio with input/output pipes")
    return serve(root, defaults, sys.stdin.buffer, sys.stdout.buffer)
