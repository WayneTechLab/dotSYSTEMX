"""Agent X: explicit event history and due-item tracking; no job execution."""

from datetime import datetime, timezone

import project_memory as memory
import agent_standards as records

ACTORS = ("human", "agent", "bot", "automation", "system")
KINDS = ("work", "check", "deploy", "runtime", "communication", "schedule", "review", "decision", "incident")
STAGES = ("planned", "implemented", "checked", "deployed", "live_verified", "failed", "cancelled", "observed")
EVENTS = "EVENTS/EVENTS.json"
SCHEDULE = "EVENTS/SCHEDULE.json"


def utc(value):
    try:
        return memory.timestamp(value).astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    except OverflowError as error:
        raise ValueError("Timestamp is outside the supported UTC range") from error


def actor(value):
    memory.fields(value, ("kind", "id"), "Actor")
    if value["kind"] not in ACTORS:
        raise ValueError("Unknown actor kind")
    memory.string(value["id"], "Actor ID")


def load_events(root):
    data = records.read(root, EVENTS)
    memory.fields(data, ("schemaVersion", "events"), "Event ledger")
    if type(data["schemaVersion"]) is not int or data["schemaVersion"] != 1 or not isinstance(data["events"], list):
        raise ValueError("Invalid event ledger schema")
    seen = set()
    ledger, _ = memory.load(root)
    known_tasks = {item["id"] for item in ledger["tasks"]}
    for event in data["events"]:
        memory.fields(event, ("id", "key", "at", "recordedAt", "actor", "kind", "stage",
                              "summary", "tasks", "revision", "evidence"), "Event")
        records.token(event["id"], "EVT")
        for name in ("key", "summary", "revision"):
            memory.string(event[name], "Event " + name)
        if event["id"] != "EVT-" + records.fingerprint(event["key"])[:20] or event["id"] in seen:
            raise ValueError("Duplicate or inconsistent event identity")
        seen.add(event["id"])
        utc(event["at"])
        utc(event["recordedAt"])
        actor(event["actor"])
        if event["kind"] not in KINDS or event["stage"] not in STAGES:
            raise ValueError("Unknown event kind or evidence stage")
        memory.strings(event["evidence"], "Event evidence")
        memory.strings(event["tasks"], "Event tasks")
        if len(event["tasks"]) != len(set(event["tasks"])) or any(task not in known_tasks for task in event["tasks"]):
            raise ValueError("Event task references must be unique and local to this scope")
        if event["stage"] in {"checked", "deployed", "live_verified"} and not event["evidence"]:
            raise ValueError("Checked/deployed/live-verified claims need original evidence references")
    return data


def add_event(root, args):
    records.task_ids(root, args.task)
    item = {"id": "EVT-" + records.fingerprint(args.key)[:20], "key": args.key,
            "at": utc(args.at), "recordedAt": memory.now(),
            "actor": {"kind": args.actor_kind, "id": args.actor_id}, "kind": args.kind,
            "stage": args.stage, "summary": args.summary, "tasks": args.task,
            "revision": args.revision, "evidence": args.evidence}
    with memory.coordination_lock(root):
        data = load_events(root)
        original = next((event for event in data["events"] if event["id"] == item["id"]), None)
        if original:
            proposed = {**item, "recordedAt": original["recordedAt"]}
            if original != proposed:
                raise ValueError("Event key already records different facts; retain it and use a new attempt/correction key")
            return {"created": False, "event": original}
        # Validate the proposed shape before changing the ledger.
        for name in ("key", "summary", "revision"):
            memory.string(item[name], "Event " + name)
        actor(item["actor"])
        if item["stage"] in {"checked", "deployed", "live_verified"} and not item["evidence"]:
            raise ValueError("This evidence stage requires --evidence")
        memory.strings(item["evidence"], "Event evidence")
        data["events"].append(item)
        records.write(root, EVENTS, data)
    return {"created": True, "event": item}


def load_schedule(root):
    data = records.read(root, SCHEDULE)
    memory.fields(data, ("schemaVersion", "items"), "Schedule ledger")
    if type(data["schemaVersion"]) is not int or data["schemaVersion"] != 1 or not isinstance(data["items"], list):
        raise ValueError("Invalid schedule ledger schema")
    seen = set()
    ledger, _ = memory.load(root)
    known_tasks = {item["id"] for item in ledger["tasks"]}
    for item in data["items"]:
        memory.fields(item, ("id", "key", "title", "dueAt", "createdAt", "owner", "tasks",
                            "externalRef", "state", "closedAt", "note", "evidence"), "Scheduled item")
        records.token(item["id"], "SCH")
        for name in ("key", "title", "owner"):
            memory.string(item[name], "Schedule " + name)
        if item["id"] != "SCH-" + records.fingerprint(item["key"])[:20] or item["id"] in seen:
            raise ValueError("Duplicate or inconsistent schedule identity")
        seen.add(item["id"])
        utc(item["dueAt"])
        utc(item["createdAt"])
        memory.strings(item["tasks"], "Schedule tasks")
        if len(item["tasks"]) != len(set(item["tasks"])) or any(task not in known_tasks for task in item["tasks"]):
            raise ValueError("Schedule task references must be unique and local to this scope")
        memory.strings(item["evidence"], "Schedule evidence")
        for name in ("externalRef", "closedAt", "note"):
            memory.string(item[name], "Schedule " + name, nonempty=False)
        if item["state"] not in ("open", "complete", "cancelled"):
            raise ValueError("Unknown schedule state")
        if item["state"] == "open":
            if item["closedAt"] or item["note"] or item["evidence"]:
                raise ValueError("Open items cannot contain closure evidence")
        elif not item["note"].strip() or memory.timestamp(item["closedAt"]) < memory.timestamp(item["createdAt"]):
            raise ValueError("Closed items need a reason and a valid closure timestamp")
        if item["state"] == "complete" and not item["evidence"]:
            raise ValueError("Completed schedule items need evidence")
    return data


def add_schedule(root, args):
    records.task_ids(root, args.task)
    for name in ("key", "title", "owner"):
        memory.string(getattr(args, name), "Schedule " + name)
    memory.string(args.external_ref, "External reference", nonempty=False)
    item = {"id": "SCH-" + records.fingerprint(args.key)[:20], "key": args.key,
            "title": args.title, "dueAt": utc(args.due), "createdAt": memory.now(),
            "owner": args.owner, "tasks": args.task, "externalRef": args.external_ref,
            "state": "open", "closedAt": "", "note": "", "evidence": []}
    with memory.coordination_lock(root):
        data = load_schedule(root)
        previous = next((entry for entry in data["items"] if entry["id"] == item["id"]), None)
        if previous:
            stable = ("id", "key", "title", "dueAt", "owner", "tasks", "externalRef")
            if any(previous[key] != item[key] for key in stable):
                raise ValueError("Schedule key exists with different facts; cancel/supersede explicitly with a new key")
            return {"created": False, "item": previous, "jobCreated": False}
        data["items"].append(item)
        records.write(root, SCHEDULE, data)
    return {"created": True, "item": item, "jobCreated": False}


def close_schedule(root, args):
    records.token(args.id, "SCH")
    memory.string(args.note, "Closure reason")
    memory.strings(args.evidence, "Closure evidence", nonempty=args.state == "complete")
    with memory.coordination_lock(root):
        data = load_schedule(root)
        item = next((entry for entry in data["items"] if entry["id"] == args.id), None)
        if item is None:
            raise ValueError("Unknown schedule item in this scope")
        if item["state"] != "open":
            if (item["state"], item["note"], item["evidence"]) == (args.state, args.note, args.evidence):
                return {"changed": False, "item": item}
            raise ValueError("Closure is immutable; record a new follow-up instead of reopening or replacing it")
        stamp = memory.now()
        if memory.timestamp(stamp) < memory.timestamp(item["createdAt"]):
            raise ValueError("Local clock precedes item creation; correct the clock before recording closure")
        item.update({"state": args.state, "closedAt": stamp, "note": args.note, "evidence": args.evidence})
        records.write(root, SCHEDULE, data)
    return {"changed": True, "item": item}


def positive(value):
    number = int(value)
    if not 1 <= number <= 1000:
        raise ValueError("Limit must be between 1 and 1000")
    return number


def add_cli(subparsers, scope):
    command = scope(subparsers.add_parser("event", help="append an observed/planned event with a stable retry key"))
    for name in ("key", "at", "summary", "revision", "actor-id"):
        command.add_argument("--" + name, required=True)
    command.add_argument("--actor-kind", choices=ACTORS, required=True)
    command.add_argument("--kind", choices=KINDS, required=True)
    command.add_argument("--stage", choices=STAGES, required=True)
    command.add_argument("--task", action="append", default=[])
    command.add_argument("--evidence", action="append", default=[])
    command = scope(subparsers.add_parser("list", help="bounded event history in observed-time order"))
    command.add_argument("--since")
    command.add_argument("--until")
    command.add_argument("--task")
    command.add_argument("--limit", type=positive, default=25)
    command = scope(subparsers.add_parser("schedule", help="track a due item; does not create an OS/cloud job"))
    for name in ("key", "title", "due", "owner"):
        command.add_argument("--" + name, required=True)
    command.add_argument("--external-ref", default="")
    command.add_argument("--task", action="append", default=[])
    command = scope(subparsers.add_parser("due", help="read due items without changing state or launching work"))
    command.add_argument("--as-of")
    command.add_argument("--limit", type=positive, default=25)
    command = scope(subparsers.add_parser("close", help="record completed/cancelled schedule bookkeeping"))
    command.add_argument("id")
    command.add_argument("--state", choices=("complete", "cancelled"), required=True)
    command.add_argument("--note", required=True)
    command.add_argument("--evidence", action="append", default=[])
    scope(subparsers.add_parser("validate"))


def dispatch(root, args):
    action = args.standard_action
    if action == "event":
        return add_event(root, args)
    if action == "schedule":
        return add_schedule(root, args)
    if action == "close":
        return close_schedule(root, args)
    if action == "due":
        at = memory.timestamp(args.as_of or memory.now())
        items = [item for item in load_schedule(root)["items"]
                 if item["state"] == "open" and memory.timestamp(item["dueAt"]) <= at]
        items.sort(key=lambda item: (memory.timestamp(item["dueAt"]), item["id"]))
        return {"asOf": utc(at.isoformat()), "totalDue": len(items), "items": items[:args.limit],
                "truncated": len(items) > args.limit, "executed": False}
    if action == "list":
        since = memory.timestamp(args.since) if args.since else datetime.min.replace(tzinfo=timezone.utc)
        until = memory.timestamp(args.until) if args.until else datetime.max.replace(tzinfo=timezone.utc)
        if since > until:
            raise ValueError("--since must not follow --until")
        events = [event for event in load_events(root)["events"]
                  if since <= memory.timestamp(event["at"]) <= until and (not args.task or args.task in event["tasks"])]
        events.sort(key=lambda event: (memory.timestamp(event["at"]), event["id"]), reverse=True)
        return {"total": len(events), "events": events[:args.limit], "truncated": len(events) > args.limit}
    return {"valid": True, "events": len(load_events(root)["events"]),
            "scheduleItems": len(load_schedule(root)["items"]), "runtimeVerified": False}
