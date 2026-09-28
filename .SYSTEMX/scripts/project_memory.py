"""Project task records and bounded context loading; no agent runtime or network."""

from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import tempfile

VIEWS = {
    "todo": "TODO.md", "in_progress": "WORKING-ON.md", "blocked": "BLOCKED.md",
    "needs_review": "REVIEW.md", "done": "DONE.md", "cancelled": "CANCELLED.md",
}
TRANSITIONS = {
    "todo": {"in_progress", "blocked", "cancelled"},
    "in_progress": {"todo", "blocked", "needs_review", "cancelled"},
    "blocked": {"todo", "in_progress", "cancelled"},
    "needs_review": {"in_progress", "blocked", "done", "cancelled"},
    "done": {"todo"}, "cancelled": {"todo"},
}
TASK_FIELDS = {
    "id", "title", "owner", "status", "milestone", "scope", "acceptance", "dependsOn",
    "nextAction", "blocker", "evidence", "reviewedBy", "createdAt", "updatedAt", "history",
}
REQUIRED = (
    "START-HERE.md", "AGENTS.md", "GLOBAL/README.md", "GLOBAL/CONTEXT.md",
    "PLAN/MASTER-PLAN.md", "MEMORY/README.md", "MEMORY/PROJECT.md",
    "MEMORY/sessions/README.md", "AGENTS/README.md", "AGENTS/REGISTRY.json",
    "AGENTS/agent.0/MEMORY.md", "WORK/README.md", "WORK/TASKS.json",
    "templates/AGENT-MEMORY.md", "templates/SESSION-CHECKPOINT.md",
    "templates/AGENT-ENTRYPOINT.md", "scripts/project_memory.py", "tests/test_project_memory.py",
    "CURRENT.md", "WORK/FOCUS.json", "docs/EVIDENCE.md", "docs/UPGRADING.md",
    "templates/EVIDENCE.md", "templates/WORKER-REPORT.md",
) + tuple("WORK/" + name for name in VIEWS.values())


def managed(root, relative):
    path = root / relative
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("Managed record is outside .SYSTEMX: " + str(relative))
    for part in (path, *path.parents):
        if part == root:
            break
        if part.is_symlink():
            raise ValueError("Managed record must not use symlinks: " + str(relative))
    return path


def read_json(root, relative):
    return json.loads(managed(root, relative).read_text(encoding="utf-8"))


def fields(value, required, label):
    if not isinstance(value, dict) or set(value) != set(required):
        raise ValueError(label + " has missing or unknown fields")


def string(value, label, nonempty=True):
    if not isinstance(value, str) or "\x00" in value or (nonempty and not value.strip()):
        raise ValueError(label + " must be " + ("a nonempty string" if nonempty else "a string"))


def strings(value, label, nonempty=False):
    if not isinstance(value, list) or (nonempty and not value):
        raise ValueError(label + " must be " + ("a nonempty list" if nonempty else "a list"))
    for item in value:
        string(item, label + " entry")


def timestamp(value):
    string(value, "timestamp")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Timestamps must include a timezone")
    return parsed


def milestones(root):
    text = managed(root, "PLAN/MASTER-PLAN.md").read_text(encoding="utf-8")
    return set(re.findall(r"^\|\s*(M-\d{3,})\s*\|", text, flags=re.M))


def validate_records(root, ledger, registry):
    fields(ledger, ("schemaVersion", "tasks"), "Task ledger")
    fields(registry, ("schemaVersion", "agents"), "Agent registry")
    for document, key in ((ledger, "tasks"), (registry, "agents")):
        if type(document["schemaVersion"]) is not int or document["schemaVersion"] != 1:
            raise ValueError("Coordination schemaVersion must be the integer 1")
        if not isinstance(document[key], list):
            raise ValueError(key + " must be a list")
    agents = {}
    for agent in registry["agents"]:
        fields(agent, ("id", "role", "memory"), "Agent record")
        string(agent["id"], "Agent ID")
        if not re.fullmatch(r"agent\.(?:0|[1-9]\d*)", agent["id"]) or agent["id"] in agents:
            raise ValueError("Agent IDs must be unique and use agent.0, agent.1, etc.")
        string(agent["role"], "Agent role")
        expected = "AGENTS/{}/MEMORY.md".format(agent["id"])
        if agent["memory"] != expected or not managed(root, expected).is_file():
            raise ValueError("Missing or invalid memory path for " + agent["id"])
        agents[agent["id"]] = agent
    if "agent.0" not in agents or agents["agent.0"]["role"] != "coordinator":
        raise ValueError("The registry must include agent.0 as coordinator")
    tasks = {}
    known_milestones = milestones(root)
    for task in ledger["tasks"]:
        fields(task, TASK_FIELDS, "Task record")
        string(task["id"], "Task ID")
        if not re.fullmatch(r"TASK-\d{3,}", task["id"]) or task["id"] in tasks:
            raise ValueError("Task IDs must be unique and use TASK-001 or higher")
        if int(task["id"].split("-")[1]) < 1:
            raise ValueError("Task numbering begins at TASK-001")
        for key in ("title", "owner", "status"):
            string(task[key], key)
        for key in ("milestone", "nextAction", "blocker", "reviewedBy"):
            string(task[key], key, nonempty=False)
        for key in ("scope", "acceptance", "dependsOn", "evidence"):
            strings(task[key], key, nonempty=(key == "acceptance"))
        if task["owner"] not in agents or task["status"] not in VIEWS:
            raise ValueError(task["id"] + " has an unknown owner or status")
        if task["milestone"] and task["milestone"] not in known_milestones:
            raise ValueError(task["id"] + " references a milestone not declared in the master plan")
        if task["status"] == "in_progress" and not task["nextAction"].strip():
            raise ValueError(task["id"] + " needs a concrete next action")
        if task["status"] == "blocked" and not task["blocker"].strip():
            raise ValueError(task["id"] + " needs an explicit blocker")
        if task["reviewedBy"] not in {"", "agent.0", "user"}:
            raise ValueError("Completion reviewer must be agent.0 or user")
        if task["status"] != "done" and task["reviewedBy"]:
            raise ValueError("Only completed tasks may have a completion reviewer")
        if task["status"] != "blocked" and task["blocker"]:
            raise ValueError("Only blocked tasks may have a current blocker")
        if task["status"] in {"done", "cancelled"} and task["nextAction"]:
            raise ValueError("Terminal tasks must not have a current next action")
        if task["status"] == "done" and (not task["evidence"] or not task["reviewedBy"]):
            raise ValueError(task["id"] + " cannot be done without evidence and a reviewer")
        created_at = timestamp(task["createdAt"])
        timestamp(task["updatedAt"])
        if not isinstance(task["history"], list) or not task["history"]:
            raise ValueError(task["id"] + " needs transition history")
        previous_status = None
        previous_at = created_at
        for event in task["history"]:
            fields(event, ("at", "status", "owner", "note", "evidence", "reviewedBy"), "History event")
            event_at = timestamp(event["at"])
            if event_at < previous_at or (previous_status is None and event_at != created_at):
                raise ValueError("Task history must begin at createdAt and remain chronological")
            previous_at = event_at
            string(event["status"], "History status")
            string(event["owner"], "History owner")
            if event["status"] not in VIEWS or event["owner"] not in agents:
                raise ValueError("History contains an unknown status or owner")
            string(event["note"], "History note", nonempty=False)
            strings(event["evidence"], "History evidence")
            string(event["reviewedBy"], "History reviewer", nonempty=False)
            if event["reviewedBy"] not in {"", "agent.0", "user"}:
                raise ValueError("Invalid history reviewer")
            if event["status"] != "done" and event["reviewedBy"]:
                raise ValueError("Only completed history events may have a reviewer")
            if previous_status is None and event["status"] != "todo":
                raise ValueError("Task history must start at todo")
            if previous_status is not None and event["status"] != previous_status:
                if event["status"] not in TRANSITIONS[previous_status]:
                    raise ValueError("Task history contains an invalid transition")
            if event["status"] == "done" and (not event["evidence"] or not event["reviewedBy"]):
                raise ValueError("Completed history needs evidence and a reviewer")
            previous_status = event["status"]
        latest = task["history"][-1]
        if any(latest[key] != task[key] for key in ("status", "owner", "evidence", "reviewedBy")) or latest["at"] != task["updatedAt"]:
            raise ValueError(task["id"] + " and its latest history event disagree")
        if task["status"] == "cancelled" and not task["history"][-1]["note"].strip():
            raise ValueError(task["id"] + " needs a cancellation reason")
        tasks[task["id"]] = task
    for task in tasks.values():
        if len(task["dependsOn"]) != len(set(task["dependsOn"])):
            raise ValueError(task["id"] + " has duplicate dependencies")
        for dependency in task["dependsOn"]:
            if dependency not in tasks:
                raise ValueError(task["id"] + " has an unknown dependency")
            if task["status"] in {"in_progress", "needs_review", "done"} and tasks[dependency]["status"] != "done":
                raise ValueError(task["id"] + " depends on unfinished " + dependency)
    # Iterative traversal also supports long imported chains without depending
    # on Python's recursion limit or the order of records in the ledger.
    remaining = {task_id: len(task["dependsOn"]) for task_id, task in tasks.items()}
    dependents = {task_id: [] for task_id in tasks}
    for task_id, task in tasks.items():
        for dependency in task["dependsOn"]:
            dependents[dependency].append(task_id)
    ready = [task_id for task_id, count in remaining.items() if count == 0]
    visited = 0
    while ready:
        task_id = ready.pop()
        visited += 1
        for dependent in dependents[task_id]:
            remaining[dependent] -= 1
            if remaining[dependent] == 0:
                ready.append(dependent)
    if visited != len(tasks):
        raise ValueError("Task dependencies contain a cycle")
    return tasks, agents


def load(root):
    ledger = read_json(root, "WORK/TASKS.json")
    registry = read_json(root, "AGENTS/REGISTRY.json")
    validate_records(root, ledger, registry)
    load_focus(root, ledger)
    return ledger, registry


def load_focus(root, ledger):
    focus = read_json(root, "WORK/FOCUS.json")
    return validate_focus_candidate(root, ledger, focus)


def validate_focus_candidate(root, ledger, focus):
    fields(focus, ("schemaVersion", "objective", "taskIds", "checkpoint", "updatedAt"), "Project focus")
    if type(focus["schemaVersion"]) is not int or focus["schemaVersion"] != 1:
        raise ValueError("Focus schemaVersion must be the integer 1")
    for key in ("objective", "checkpoint", "updatedAt"):
        string(focus[key], "Focus " + key, nonempty=False)
    strings(focus["taskIds"], "Focus task IDs")
    if len(focus["objective"]) > 600 or len(focus["taskIds"]) > 10:
        raise ValueError("Keep focus compact: at most 600 objective characters and 10 tasks")
    if len(focus["taskIds"]) != len(set(focus["taskIds"])):
        raise ValueError("Focus task IDs must be unique")
    known = {task["id"] for task in ledger["tasks"]}
    if any(task_id not in known for task_id in focus["taskIds"]):
        raise ValueError("Focus references an unknown task")
    if not focus["objective"].strip():
        if any((focus["objective"], focus["taskIds"], focus["checkpoint"], focus["updatedAt"])):
            raise ValueError("Blank focus must have empty fields; use focus --clear")
    else:
        timestamp(focus["updatedAt"])
    if focus["checkpoint"]:
        path = Path(focus["checkpoint"])
        if (path.is_absolute() or ".." in path.parts or "\\" in focus["checkpoint"]
                or path.parts[:2] != ("MEMORY", "sessions") or path.suffix != ".md"
                or path.name == "README.md" or not managed(root, path).is_file()):
            raise ValueError("Checkpoint must name an existing Markdown file under MEMORY/sessions/")
    return focus


def render_current(ledger, focus):
    lines = ["# Current project focus", "",
             "Generated from [WORK/FOCUS.json](WORK/FOCUS.json) and [WORK/TASKS.json](WORK/TASKS.json).",
             "Do not edit this view. Use `focus`, `task-set`, and `refresh-work`.", ""]
    if not focus["objective"]:
        lines += ["No current objective recorded. This does not establish project completion.", ""]
    else:
        lines += ["- Objective: " + escaped(focus["objective"]),
                  "- Focus selected at: " + focus["updatedAt"],
                  "- Checkpoint: " + ("`" + escaped(focus["checkpoint"]) + "`" if focus["checkpoint"] else "not recorded"), ""]
        tasks = {task["id"]: task for task in ledger["tasks"]}
        for task_id in focus["taskIds"]:
            task = tasks[task_id]
            lines += ["## {}: {}".format(task_id, escaped(task["title"])), "",
                      "- Recorded state: {} / {}".format(task["status"], task["owner"]),
                      "- Next action: " + escaped(task["nextAction"] or "not recorded"),
                      "- Blocker: " + escaped(task["blocker"] or "none recorded"),
                      "- Dependencies: " + (", ".join("{} ({})".format(dep, tasks[dep]["status"])
                                                     for dep in task["dependsOn"]) or "none"), ""]
        if not focus["taskIds"]:
            lines += ["No focus tasks selected. Read the master plan before creating or selecting work.", ""]
    lines += ["Read [START-HERE.md](START-HERE.md) and the [master plan](PLAN/MASTER-PLAN.md).",
              "This is recorded focus, not live runtime or release readiness. Recheck volatile facts.",
              "Task status, blockers, and next actions come from the ledger; dated checkpoints retain historical evidence.", ""]
    return "\n".join(lines)


def escaped(value):
    value = " ".join(value.splitlines())
    return re.sub(r"([\\`*_{}\[\]()<>|#])", r"\\\1", value)


def render_views(ledger):
    output = {}
    for status, filename in VIEWS.items():
        lines = ["# " + filename[:-3], "",
                 "Generated from [TASKS.json](TASKS.json). Do not edit this view directly.",
                 "Refresh with `bash .SYSTEMX/SYSTEMX.sh refresh-work`.", ""]
        tasks = sorted((task for task in ledger["tasks"] if task["status"] == status), key=lambda item: item["id"])
        if not tasks:
            lines += ["No tasks recorded in this state.", ""]
        for task in tasks:
            lines += ["## {}: {}".format(task["id"], escaped(task["title"])), "",
                      "- Owner: " + task["owner"], "- Updated: " + task["updatedAt"],
                      "- Milestone: " + (task["milestone"] or "unassigned"),
                      "- Dependencies: " + (", ".join(task["dependsOn"]) or "none"),
                      "- Next action: " + escaped(task["nextAction"] or "not recorded")]
            if task["blocker"]:
                lines.append("- Blocker: " + escaped(task["blocker"]))
            lines += ["- Acceptance: " + escaped("; ".join(task["acceptance"]))]
            for evidence in task["evidence"]:
                lines.append("- Evidence: " + escaped(evidence))
            if task["reviewedBy"]:
                lines.append("- Reviewed by: " + task["reviewedBy"])
            if task["history"][-1]["note"]:
                lines.append("- Latest note: " + escaped(task["history"][-1]["note"]))
            lines.append("")
        output["WORK/" + filename] = "\n".join(lines)
    return output


def validate_work(root):
    ledger, _ = load(root)
    views = render_views(ledger)
    views["CURRENT.md"] = render_current(ledger, load_focus(root, ledger))
    for relative, expected in views.items():
        path = managed(root, relative)
        if not path.is_file() or path.read_text(encoding="utf-8") != expected:
            raise ValueError(relative + " is stale; run 'refresh-work' after reviewing the ledger")


def atomic_write(root, relative, content):
    path = managed(root, relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as output:
            temporary = Path(output.name)
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


@contextmanager
def coordination_lock(root):
    lock = managed(root, "state/coordination.lock")
    lock.parent.mkdir(parents=True, exist_ok=True)
    try:
        lock.mkdir()
    except FileExistsError as error:
        raise ValueError("Coordination writer is busy or a stale lock exists; inspect state/coordination.lock") from error
    try:
        yield
    finally:
        lock.rmdir()


def refresh(root, ledger):
    views = render_views(ledger)
    views["CURRENT.md"] = render_current(ledger, load_focus(root, ledger))
    for relative, content in views.items():
        atomic_write(root, relative, content)


def save_ledger(root, ledger, registry):
    validate_records(root, ledger, registry)
    atomic_write(root, "WORK/TASKS.json", json.dumps(ledger, indent=2) + "\n")
    refresh(root, ledger)


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def event(task, note):
    return {"at": task["updatedAt"], "status": task["status"], "owner": task["owner"],
            "note": note, "evidence": list(task["evidence"]), "reviewedBy": task["reviewedBy"]}


def add_task(root, args):
    with coordination_lock(root):
        ledger, registry = load(root)
        number = max((int(task["id"].split("-")[1]) for task in ledger["tasks"]), default=0) + 1
        stamp = now()
        task = {"id": "TASK-{:03d}".format(number), "title": args.title, "owner": args.owner,
                "status": "todo", "milestone": args.milestone, "scope": args.scope,
                "acceptance": args.acceptance, "dependsOn": args.depends_on,
                "nextAction": args.next, "blocker": "", "evidence": [], "reviewedBy": "",
                "createdAt": stamp, "updatedAt": stamp, "history": []}
        task["history"].append(event(task, "Task created"))
        ledger["tasks"].append(task)
        save_ledger(root, ledger, registry)
    print("Created " + task["id"])
    return 0


def set_task(root, args):
    with coordination_lock(root):
        ledger, registry = load(root)
        task = next((item for item in ledger["tasks"] if item["id"] == args.task_id), None)
        if task is None:
            raise ValueError("Unknown task: " + args.task_id)
        if not any((args.status, args.owner, args.next is not None, args.blocker is not None,
                    args.evidence, args.reviewer, args.note)):
            raise ValueError("task-set requires a change or note")
        old = task["status"]
        new = args.status or old
        if new != old and new not in TRANSITIONS[old]:
            raise ValueError("Invalid task transition: {} -> {}".format(old, new))
        if old in {"done", "cancelled"} and new != "todo":
            raise ValueError("Reopen a terminal task to todo before editing it")
        if new == "cancelled" and not args.note.strip():
            raise ValueError("Cancellation requires --note with a reason")
        if old in {"done", "cancelled"} and new == "todo":
            task["evidence"], task["reviewedBy"] = [], ""
        task["status"] = new
        for argument, key in ((args.owner, "owner"), (args.next, "nextAction"), (args.blocker, "blocker")):
            if argument is not None:
                task[key] = argument
        if new != "blocked":
            task["blocker"] = ""
        if new != "done":
            task["reviewedBy"] = ""
        if args.reviewer:
            if new != "done":
                raise ValueError("--reviewer is recorded only when accepting done")
            task["reviewedBy"] = args.reviewer
        if new in {"done", "cancelled"}:
            task["nextAction"] = ""
        task["evidence"].extend(args.evidence)
        task["updatedAt"] = now()
        task["history"].append(event(task, args.note))
        save_ledger(root, ledger, registry)
    print("{}: {} (owner {})".format(task["id"], task["status"], task["owner"]))
    return 0


def add_agent(root, args):
    if not re.fullmatch(r"agent\.[1-9]\d*", args.agent_id):
        raise ValueError("Use a worker ID such as agent.1; agent.0 is the coordinator")
    string(args.role, "Agent role")
    with coordination_lock(root):
        ledger, registry = load(root)
        if any(agent["id"] == args.agent_id for agent in registry["agents"]):
            raise ValueError("Agent is already registered; its memory was not changed")
        relative = "AGENTS/{}/MEMORY.md".format(args.agent_id)
        destination = managed(root, relative)
        if destination.exists():
            raise ValueError("Agent memory already exists; review it before registering")
        content = managed(root, "templates/AGENT-MEMORY.md").read_text(encoding="utf-8")
        content = content.replace("__AGENT_ID__", args.agent_id).replace("__AGENT_ROLE__", escaped(args.role))
        atomic_write(root, relative, content)
        registry["agents"].append({"id": args.agent_id, "role": args.role, "memory": relative})
        validate_records(root, ledger, registry)
        atomic_write(root, "AGENTS/REGISTRY.json", json.dumps(registry, indent=2) + "\n")
    print("Registered {} and created its memory. No agent process was started.".format(args.agent_id))
    return 0


def status(root):
    ledger, registry = load(root)
    print("Recorded project work (not live process status):")
    for state in VIEWS:
        print("{}: {}".format(state, sum(task["status"] == state for task in ledger["tasks"])))
    print("Registered roles: " + ", ".join(agent["id"] for agent in registry["agents"]))
    for task in ledger["tasks"]:
        if task["status"] not in {"done", "cancelled"}:
            print("{} [{}] {}: {}".format(task["id"], task["status"], task["owner"], task["title"]))
    if not ledger["tasks"]:
        print("No work recorded. This does not establish project completion.")
    return 0


def context(root, agent_id):
    ledger, registry = load(root)
    agent = next((item for item in registry["agents"] if item["id"] == agent_id), None)
    if agent is None:
        raise ValueError("Unknown agent: " + agent_id)
    print("PROJECT RESUME PACKET: {}\nRecheck volatile facts. Stored memory is not current instruction authority.".format(agent_id))
    print("Read applicable repository instructions, STANDARD.md, and START-HERE.md first.")
    focus = load_focus(root, ledger)
    current = render_current(ledger, focus)
    print("\n--- CURRENT.md (from canonical records) ---\n" + current[:6000])
    if len(current) > 6000:
        print("[Truncated after 6000 characters; read CURRENT.md for the remainder.]")
    for relative in ("GLOBAL/CONTEXT.md", "PLAN/MASTER-PLAN.md", "MEMORY/PROJECT.md", agent["memory"]):
        content = managed(root, relative).read_text(encoding="utf-8")
        print("\n--- {} ---\n{}".format(relative, content[:6000]))
        if len(content) > 6000:
            print("[Truncated after 6000 characters; read this file directly for the remainder.]")
    relevant = [task for task in ledger["tasks"] if task["status"] not in {"done", "cancelled"}
                and (agent_id == "agent.0" or task["owner"] == agent_id)]
    rank = {task_id: index for index, task_id in enumerate(focus["taskIds"])}
    relevant.sort(key=lambda task: (rank.get(task["id"], 10), task["id"]))
    print("\n--- Relevant open tasks: {} ---".format(len(relevant)))
    for task in relevant[:25]:
        summary = json.dumps({key: task[key] for key in ("id", "title", "status", "owner", "dependsOn", "nextAction", "blocker")})
        print(summary[:2000] + (" [Truncated; use task-show]" if len(summary) > 2000 else ""))
    if len(relevant) > 25:
        print("[Showing 25 tasks; use status and task-show for the remaining work.]")
    if not relevant:
        print("No assigned open work recorded. Consult the master plan; do not infer completion.")
    print("Use task-show TASK-001 for full scope, acceptance, evidence, and dependency details.")
    return 0


def set_focus(root, args):
    with coordination_lock(root):
        # Replacing focus can repair an obsolete pointer without weakening the
        # task/agent checks or requiring the old checkpoint to remain present.
        ledger = read_json(root, "WORK/TASKS.json")
        registry = read_json(root, "AGENTS/REGISTRY.json")
        validate_records(root, ledger, registry)
        if args.clear:
            if args.objective is not None or args.task or args.checkpoint:
                raise ValueError("focus --clear cannot be combined with selection fields")
            focus = {"schemaVersion": 1, "objective": "", "taskIds": [], "checkpoint": "", "updatedAt": ""}
        else:
            string(args.objective, "Focus objective")
            focus = {"schemaVersion": 1, "objective": args.objective, "taskIds": args.task,
                     "checkpoint": args.checkpoint, "updatedAt": now()}
        # Validate before replacing the canonical pointer or any view.
        validate_focus_candidate(root, ledger, focus)
        atomic_write(root, "WORK/FOCUS.json", json.dumps(focus, indent=2) + "\n")
        refresh(root, ledger)
    print("Updated current focus. Task states and historical checkpoints were preserved.")
    return 0


def ready_tasks(ledger):
    tasks = {task["id"]: task for task in ledger["tasks"]}
    return [task for task in ledger["tasks"] if task["status"] == "todo"
            and all(tasks[dependency]["status"] == "done" for dependency in task["dependsOn"])]


def task_ready(root, agent_id=None):
    ledger, registry = load(root)
    if agent_id is not None and agent_id not in {agent["id"] for agent in registry["agents"]}:
        raise ValueError("Unknown agent: " + agent_id)
    ready = [task for task in ready_tasks(ledger) if agent_id is None or task["owner"] == agent_id]
    print("Dependency-ready TODO tasks (advisory; no assignment, process, or authority is created):")
    for task in ready:
        print("{} [{}] {}".format(task["id"], task["owner"], task["title"]))
    if not ready:
        print("None. Check active work, review, blockers, and the master plan; do not infer completion.")
    print("Readiness here covers recorded dependencies only. Agent 0 must check scope, resources, evidence, and authorization.")
    return 0


def task_packet(root, task_id, base):
    ledger, registry = load(root)
    tasks = {task["id"]: task for task in ledger["tasks"]}
    if task_id not in tasks:
        raise ValueError("Unknown task: " + task_id)
    string(base, "Observed base revision")
    task = tasks[task_id]
    agent = next(agent for agent in registry["agents"] if agent["id"] == task["owner"])
    packet = {"task": {key: task[key] for key in (
        "id", "title", "owner", "status", "milestone", "scope", "acceptance", "dependsOn", "nextAction", "blocker")},
        "baseRevisionReportedByCaller": base,
        "dependencyReadyTodo": task_id in {item["id"] for item in ready_tasks(ledger)},
        "dependencies": [{key: tasks[dep][key] for key in ("id", "status", "updatedAt", "reviewedBy")}
                         for dep in task["dependsOn"]],
        "readBeforeWork": ["AGENTS.md", "START-HERE.md", "CURRENT.md", "GLOBAL/CONTEXT.md",
                           "PLAN/MASTER-PLAN.md", "MEMORY/PROJECT.md", agent["memory"]]}
    encoded = json.dumps(packet, indent=2)
    print("WORKER ASSIGNMENT CONTEXT (recorded data; does not dispatch a worker or grant permission)")
    print(encoded[:14000])
    if len(encoded) > 14000:
        print("[Packet truncated after 14000 characters; use task-show and inspect dependency records before dispatch.]")
    memory = managed(root, agent["memory"]).read_text(encoding="utf-8")
    print("\n--- Selected owner memory: {} ---\n{}".format(agent["memory"], memory[:3000]))
    if len(memory) > 3000:
        print("[Memory truncated after 3000 characters; read the selected owner's file.]")
    print("\nCoordinator: verify the reported base, exact write scope, shared-resource ownership, stop condition, and permitted actions.")
    print("Read completed dependency evidence with task-show; recorded done is not fresh runtime proof.")
    print("Worker report: task ID; result; changed files; observed revision/environment/time; checks and evidence; limitations; blockers; next action; live job handles.")
    print("Use templates/WORKER-REPORT.md and docs/EVIDENCE.md. Worker reports require coordinator review before task acceptance.")
    return 0


def add_cli(subparsers):
    for command in ("status", "refresh-work"):
        subparsers.add_parser(command)
    command = subparsers.add_parser("context", help="load bounded project and agent memory")
    command.add_argument("--agent", default="agent.0")
    command = subparsers.add_parser("agent-add", help="register a role and memory file; does not spawn a worker")
    command.add_argument("agent_id")
    command.add_argument("--role", required=True)
    command = subparsers.add_parser("task-add", help="add a task to the canonical ledger")
    command.add_argument("--title", required=True)
    command.add_argument("--owner", default="agent.0")
    command.add_argument("--acceptance", action="append", required=True)
    command.add_argument("--scope", action="append", default=[])
    command.add_argument("--depends-on", action="append", default=[])
    command.add_argument("--milestone", default="")
    command.add_argument("--next", default="")
    command = subparsers.add_parser("task-show")
    command.add_argument("task_id")
    command = subparsers.add_parser("task-set", help="update task state and regenerate status pages")
    command.add_argument("task_id")
    command.add_argument("--status", choices=tuple(VIEWS))
    command.add_argument("--owner")
    command.add_argument("--next")
    command.add_argument("--blocker")
    command.add_argument("--evidence", action="append", default=[])
    command.add_argument("--reviewer", choices=("agent.0", "user"))
    command.add_argument("--note", default="")
    command = subparsers.add_parser("focus", help="select current objective and task pointers; does not change task states")
    command.add_argument("--objective")
    command.add_argument("--task", action="append", default=[])
    command.add_argument("--checkpoint", default="", help="existing Markdown path relative to .SYSTEMX under MEMORY/sessions/")
    command.add_argument("--clear", action="store_true")
    command = subparsers.add_parser("task-ready", help="list TODO tasks whose recorded dependencies are done")
    command.add_argument("--agent")
    command = subparsers.add_parser("task-packet", help="print bounded worker context from existing task records")
    command.add_argument("task_id")
    command.add_argument("--base", required=True, help="source revision freshly observed by the caller; not verified by this command")


COMMANDS = {"status", "refresh-work", "context", "agent-add", "task-add", "task-show", "task-set",
            "focus", "task-ready", "task-packet"}


def dispatch(root, args):
    if args.action == "focus":
        return set_focus(root, args)
    if args.action == "task-ready":
        return task_ready(root, args.agent)
    if args.action == "task-packet":
        return task_packet(root, args.task_id, args.base)
    if args.action == "status":
        return status(root)
    if args.action == "context":
        return context(root, args.agent)
    if args.action == "agent-add":
        return add_agent(root, args)
    if args.action == "task-add":
        return add_task(root, args)
    if args.action == "task-set":
        return set_task(root, args)
    if args.action == "refresh-work":
        with coordination_lock(root):
            ledger, _ = load(root)
            refresh(root, ledger)
        print("Regenerated six work views and CURRENT.md from canonical records.")
        return 0
    ledger, _ = load(root)
    task = next((item for item in ledger["tasks"] if item["id"] == args.task_id), None)
    if task is None:
        raise ValueError("Unknown task: " + args.task_id)
    print(json.dumps(task, indent=2))
    return 0
