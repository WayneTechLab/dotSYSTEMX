"""SYSTEMX PROJECTS: explicit, local routing to isolated .SYSTEMXP records."""

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import tempfile
import uuid

import project_memory
import agent_standards
from systemx_paths import is_link

REGISTRY = "Projects/REGISTRY.json"
BLUEPRINT = "templates/project"
KINDS = ("general", "software", "research", "operations", "channel")
SOURCES = ("repository", "directory", "drive", "chat", "document", "other")
SEED_FILES = (
    "README.md", "START-HERE.md", "AGENTS.md", "GLOBAL/CONTEXT.md",
    "GLOBAL/ACCESS-MATRIX.md", "PLAN/MASTER-PLAN.md", "PLAN/MAP.md",
    "MEMORY/PROJECT.md", "MEMORY/sessions/README.md",
    "AGENTS/REGISTRY.json", "AGENTS/agent.0/MEMORY.md", "WORK/README.md",
    "WORK/TASKS.json", "WORK/FOCUS.json", "DECISIONS/README.md",
    "SYNC/README.md", "SOURCES.json", "project.json",
)
REQUIRED = ("scripts/project_workspaces.py", "tests/test_workspaces.py",
            "docs/PROJECTS.md", "Projects/README.md", REGISTRY) + tuple(
                BLUEPRINT + "/" + name for name in SEED_FILES)


def project_name(name):
    if (not isinstance(name, str) or
            not re.fullmatch(r"[A-Za-z](?:[A-Za-z0-9 _-]{0,78}[A-Za-z0-9])?", name) or
            name.casefold() in {"root", "con", "prn", "aux", "nul"} or
            re.fullmatch(r"(?:com|lpt)[1-9]", name, re.I)):
        raise ValueError("Use a portable project name: 1–80 letters, digits, spaces, _ or -; no reserved OS names")
    return name


def blank_blueprint(defaults):
    """Read only dedicated blank seeds, never the active root project's memory."""
    base = Path(defaults) / BLUEPRINT
    data = {}
    for name in SEED_FILES:
        path = project_memory.managed(base, name)
        if not path.is_file() or is_link(path) or path.stat().st_nlink > 1:
            raise ValueError("Project blueprint must contain regular files: " + name)
        data[name] = path.read_text(encoding="utf-8")
    ledger, agents = project_memory.load(base)
    focus = project_memory.load_focus(base, ledger)
    if (ledger["tasks"] or any(focus[k] for k in ("objective", "taskIds", "checkpoint", "updatedAt")) or
            agents["agents"] != [{"id": "agent.0", "role": "coordinator",
                                  "memory": "AGENTS/agent.0/MEMORY.md"}]):
        raise ValueError("Project blueprint must have empty work/focus and only Agent 0")
    if json.loads(data["SOURCES.json"]) != {"schemaVersion": 1, "sources": []}:
        raise ValueError("Project blueprint sources must be empty")
    if json.loads(data["project.json"]) != {
            "schemaVersion": 1, "project": {"name": "", "description": ""},
            "checks": [], "commands": {"dev": [], "build": [], "deploy": []}}:
        raise ValueError("Project blueprint configuration must be blank")
    return data


class Workspaces:
    def __init__(self, root, defaults):
        self.root = Path(root)
        self.defaults = Path(defaults)
        self.registry = self.read_json(REGISTRY)
        if (not isinstance(self.registry, dict) or set(self.registry) != {"schemaVersion", "projects"} or
                type(self.registry["schemaVersion"]) is not int or self.registry["schemaVersion"] != 1 or
                not isinstance(self.registry["projects"], list)):
            raise ValueError("Unsupported Projects/REGISTRY.json format; preserve it and review migration")
        self.projects = {}
        names = set()
        for entry in self.registry["projects"]:
            project_memory.fields(entry, ("name", "path", "records", "kind"), "Project entry")
            name = project_name(entry["name"])
            if name.casefold() in names:
                raise ValueError("Duplicate or case-conflicting project name")
            names.add(name.casefold())
            path = "Projects/" + name
            if entry["path"] != path or entry["records"] != path + "/.SYSTEMXP" or entry["kind"] not in KINDS:
                raise ValueError("Project paths and kind must match the exact registered scope")
            self.projects[name] = entry

    def safe(self, relative, *, missing=False):
        if (not isinstance(relative, str) or "\\" in relative or ":" in relative or "\x00" in relative or
                PurePosixPath(relative).is_absolute() or any(p in ("", ".", "..") for p in relative.split("/"))):
            raise ValueError("Use an explicit, contained, portable record path")
        path = self.root
        for part in relative.split("/"):
            if path.exists():
                if not path.is_dir():
                    raise ValueError("Record parent is not a directory: " + relative)
                matches = [p.name for p in path.iterdir() if p.name.casefold() == part.casefold()]
                if matches and matches != [part]:
                    raise ValueError("Exact-case conflict: " + relative)
            path = path / part
            if is_link(path):
                raise ValueError("Linked workspace paths are not allowed: " + relative)
            if path.exists():
                if path.is_file() and path.stat().st_nlink > 1:
                    raise ValueError("Hard-linked workspace records are not allowed: " + relative)
            elif not missing:
                raise ValueError("Missing workspace record: " + relative)
        return path

    def read_json(self, relative):
        path = self.safe(relative)
        if not path.is_file() or path.stat().st_size > 2 * 1024 * 1024:
            raise ValueError("Workspace metadata must be a regular file of at most 2 MiB: " + relative)
        return project_memory.read_json(self.root, relative)

    def select(self, name=None, root=False):
        if bool(root) == (name is not None):
            raise ValueError("Select exactly one scope: --root or --project NAME")
        if root:
            return "root", self.root, self.root.parent
        if name not in self.projects:
            raise ValueError("Unknown project; use the exact name from 'projects list'")
        entry = self.projects[name]
        records = self.safe(entry["records"])
        if not records.is_dir():
            raise ValueError("Project records must be a real .SYSTEMXP directory")
        # A project marker must never be a second installation or a recursive workspace.
        for parent in (records, records.parent):
            for path in parent.iterdir():
                if path.name.casefold() == ".systemx" or (parent == records and path.name.casefold() == "projects"):
                    raise ValueError("Nested .SYSTEMX installations and recursive Projects trees are not supported")
        return name, records, records.parent

    def guard(self, records):
        """Inspect the selected records only; do not traverse project code or siblings."""
        if records == self.root:
            # Shared files are guarded by the existing task tools. Never scan children here.
            return
        for directory, dirs, files in os.walk(records, followlinks=False):
            folded = set()
            for name in dirs + files:
                if name.casefold() in folded:
                    raise ValueError("Case-conflicting project records")
                folded.add(name.casefold())
                # Each parent is already checked by select() or this walk. Avoid
                # rescanning all siblings for every child (quadratic in archives).
                path = Path(directory) / name
                if is_link(path) or (path.is_file() and path.stat().st_nlink > 1):
                    raise ValueError("Linked workspace records are not allowed: " + str(path))
                if name.casefold() in {".systemx", ".systemxp", "projects"}:
                    raise ValueError("Nested project markers are not supported inside .SYSTEMXP")
        for name in SEED_FILES:
            path = self.safe((records / name).relative_to(self.root).as_posix())
            if not path.is_file():
                raise ValueError("Missing project record: " + name)

    def validate_scope(self, selection, *, views=True):
        name, records, _ = selection
        self.guard(records)
        agent_standards.validate_optional(records)
        ledger, _ = project_memory.load(records)
        project_memory.load_focus(records, ledger)
        if views:
            project_memory.validate_work(records)
        if name != "root":
            sources = self.read_json(self.projects[name]["records"] + "/SOURCES.json")
            project_memory.fields(sources, ("schemaVersion", "sources"), "Sources")
            if type(sources["schemaVersion"]) is not int or sources["schemaVersion"] != 1 or not isinstance(sources["sources"], list):
                raise ValueError("Invalid project source references")
            for item in sources["sources"]:
                project_memory.fields(item, ("kind", "location", "description"), "Source reference")
                if item["kind"] not in SOURCES:
                    raise ValueError("Unsupported source kind")
                project_memory.string(item["location"], "Source location")
                project_memory.string(item["description"], "Source description", nonempty=False)
            config = self.read_json(self.projects[name]["records"] + "/project.json")
            # Import at call time to avoid a circular import during CLI setup.
            import systemx
            try:
                systemx.validate_config(config)
            except systemx.ConfigError as error:
                raise ValueError(str(error)) from error
            if config["project"]["name"] != name:
                raise ValueError("Project configuration name must match its selected registry entry")
        return ledger

    def status(self, selection):
        ledger = self.validate_scope(selection)
        name, records, _ = selection
        focus = project_memory.load_focus(records, ledger)
        sources = ("WORK/TASKS.json", "WORK/FOCUS.json", "AGENTS/REGISTRY.json")
        result = {
            "schemaVersion": 1, "scope": name,
            "recordsPath": records.relative_to(self.root.parent).as_posix(),
            "kind": "local-record-status", "objective": focus["objective"],
            "taskIds": focus["taskIds"],
            "taskCounts": dict(Counter({state: sum(t["status"] == state for t in ledger["tasks"])
                                       for state in project_memory.VIEWS})),
            "sourceHashes": {p: hashlib.sha256((records / p).read_bytes()).hexdigest() for p in sources},
        }
        if name == "root":
            result["projects"] = list(self.projects.values())
            result["sourceHashes"][REGISTRY] = hashlib.sha256(self.safe(REGISTRY).read_bytes()).hexdigest()
        return result

    def refresh(self, selection, apply=False):
        _, records, _ = selection
        data = json.dumps(self.status(selection), indent=2) + "\n"
        relative = (records / "SYNC/STATUS.json").relative_to(self.root).as_posix()
        destination = self.safe(relative, missing=True)
        changed = not destination.exists() or destination.read_text(encoding="utf-8") != data
        if apply:
            with project_memory.coordination_lock(records):
                # Rebuild under the same scope lock used by task writers.
                data = json.dumps(self.status(selection), indent=2) + "\n"
                self.safe(relative, missing=True)
                changed = not destination.exists() or destination.read_text(encoding="utf-8") != data
                if changed:
                    project_memory.atomic_write(records, "SYNC/STATUS.json", data)
        return {"applied": apply, "changed": changed, "destination": str(destination), "status": json.loads(data)}

    def add(self, name, kind="general", description="", apply=False):
        project_name(name)
        if kind not in KINDS:
            raise ValueError("Unsupported project kind")
        project_memory.string(description, "Project description", nonempty=False)
        blueprint = blank_blueprint(self.defaults)
        entry = {"name": name, "path": "Projects/" + name,
                 "records": "Projects/" + name + "/.SYSTEMXP", "kind": kind}
        destination = self.safe(entry["path"], missing=True)
        if any(p.casefold() == name.casefold() for p in self.projects) or destination.exists():
            raise ValueError("Project is registered or its folder already exists; nothing was replaced")
        result = {"applied": apply, "project": entry, "description": description}
        if not apply:
            return result
        with project_memory.coordination_lock(self.root):
            latest = Workspaces(self.root, self.defaults)
            destination = latest.safe(entry["path"], missing=True)
            if name in latest.projects or destination.exists():
                raise ValueError("Project appeared during setup; nothing was replaced")
            log = "logs/projects/" + uuid.uuid4().hex + ".json"
            latest.safe(log, missing=True)
            receipt = {"schemaVersion": 1, "operation": "project-add", "project": entry,
                       "at": project_memory.now(), "state": "started",
                       "defaultsVersion": (self.defaults / "VERSION").read_text().strip()}
            project_memory.atomic_write(self.root, log, json.dumps(receipt, indent=2) + "\n")
            stage = Path(tempfile.mkdtemp(prefix=".project-stage-", dir=self.root / "Projects"))
            try:
                # Build at a private staging path, then publish the new folder.
                records = stage / ".SYSTEMXP"
                for path, content in blueprint.items():
                    project_memory.atomic_write(records, path, content)
                config = json.loads(blueprint["project.json"])
                config["project"] = {"name": name, "description": description}
                project_memory.atomic_write(records, "project.json", json.dumps(config, indent=2) + "\n")
                (stage / "README.md").write_text(
                    "# " + project_memory.escaped(name) + "\n\n"
                    "Project records: [.SYSTEMXP/START-HERE.md](.SYSTEMXP/START-HERE.md).\n\n"
                    "Keep code and working files beside .SYSTEMXP, or record explicit external\n"
                    "references in .SYSTEMXP/SOURCES.json. No remote is connected automatically.\n",
                    encoding="utf-8")
                (stage / "AGENTS.md").write_text(
                    "# Selected project instructions\n\n"
                    "Read [.SYSTEMXP/START-HERE.md](.SYSTEMXP/START-HERE.md) before work.\n"
                    "Use the outer launcher with an explicit --project selection for this\n"
                    "folder's exact name. Keep this project's records inside .SYSTEMXP;\n"
                    "do not create another .SYSTEMX or import sibling project memory.\n",
                    encoding="utf-8")
                latest.safe(entry["path"], missing=True)
                if destination.exists():
                    raise ValueError("Project appeared during setup; nothing was replaced")
                stage.rename(destination)
                project_memory.refresh(destination / ".SYSTEMXP", {"schemaVersion": 1, "tasks": []})
                latest.registry["projects"].append(entry)
                project_memory.atomic_write(self.root, REGISTRY, json.dumps(latest.registry, indent=2) + "\n")
                receipt["state"] = "complete"
                result["receipt"] = log
            except BaseException:
                receipt["state"] = "failed"
                receipt["recovery"] = "Preserve any unregistered project folder and inspect it before retrying"
                raise
            finally:
                if stage.exists():
                    shutil.rmtree(stage)
                project_memory.atomic_write(self.root, log, json.dumps(receipt, indent=2) + "\n")
        return result


def add_cli(subparsers):
    parent = subparsers.add_parser("projects", help="SYSTEMX PROJECTS: .SYSTEMXP scopes")
    commands = parent.add_subparsers(dest="project_action", required=True)
    commands.add_parser("list", help="list identities only; does not load project memories")
    command = commands.add_parser("add", help="preview a blank project; --apply creates it")
    command.add_argument("name")
    command.add_argument("--kind", choices=KINDS, default="general")
    command.add_argument("--description", default="")
    command.add_argument("--apply", action="store_true")

    def scope(command, required=True):
        group = command.add_mutually_exclusive_group(required=required)
        group.add_argument("--project", metavar="NAME")
        group.add_argument("--root", dest="workspace_root", action="store_true")
        return command

    scope(commands.add_parser("validate", help="validate selected records, or all registered scopes"), required=False)
    command = scope(commands.add_parser("refresh-status", help="preview a local status snapshot"))
    command.add_argument("--apply", action="store_true")

    class Scoped:
        def add_parser(self, *args, **kwargs):
            return scope(commands.add_parser(*args, **kwargs))

    project_memory.add_cli(Scoped())
    agent_standards.add_cli(commands, scope)
    for action in ("check", "dev", "build", "deploy"):
        command = scope(commands.add_parser(action))
        command.add_argument("--dry-run", action="store_true")


def dispatch(root, defaults, args, run_action):
    workspaces = Workspaces(root, defaults)
    action = args.project_action
    if action == "list":
        result = workspaces.registry
    elif action == "add":
        result = workspaces.add(args.name, args.kind, args.description, args.apply)
    elif action == "validate":
        selections = ([workspaces.select(args.project, args.workspace_root)]
                      if args.project is not None or args.workspace_root else
                      [workspaces.select(root=True)] + [workspaces.select(name) for name in workspaces.projects])
        for selection in selections:
            workspaces.validate_scope(selection)
        result = {"valid": True, "scopes": [item[0] for item in selections],
                  "limit": "Record consistency only; not application tests, remote sync, or runtime readiness"}
    else:
        selection = workspaces.select(args.project, args.workspace_root)
        name, records, host = selection
        if action == "status":
            result = workspaces.status(selection)
        elif action == "refresh-status":
            result = workspaces.refresh(selection, args.apply)
        else:
            workspaces.guard(records)
            selected = argparse.Namespace(**vars(args))
            selected.action = action
            if action in agent_standards.COMMANDS:
                return agent_standards.dispatch(records, defaults, selected)
            print("Selected scope: " + name + "\nRecords: " + str(records))
            print("Shared defaults: " + str(defaults))
            if action in ("check", "dev", "build", "deploy"):
                workspaces.validate_scope(selection)
                return run_action(records, host, action, args.dry_run)
            return project_memory.dispatch(records, selected, defaults)
    print(json.dumps(result, indent=2))
    return 0
