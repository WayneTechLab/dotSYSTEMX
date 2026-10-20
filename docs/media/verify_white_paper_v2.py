#!/usr/bin/env python3
"""Verify the paper's ROOT coordination example in disposable local records.

Run: python3 -I -B docs/media/verify_white_paper_v2.py [--output /existing/folder/result.json]
No model, native harness plan, provider process, network request, or cloud job is used.
"""

import sys
if __name__ == "__main__" and not sys.flags.isolated:
    _bootstrap_os = sys.modules.get("os")
    if _bootstrap_os is None or not sys.executable:
        sys.exit("White-paper v2 verifier requires Python isolated mode")
    try:
        _bootstrap_os.execv(sys.executable, [sys.executable, "-I", "-B", __file__, *sys.argv[1:]])
    except OSError as error:
        sys.exit("White-paper v2 verifier could not enter isolated mode: " + str(error))

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import stat
import subprocess
import tempfile
import time


REPO = Path(__file__).resolve().parents[2]
MAX_COMMANDS = 40
MAX_SECONDS = 180


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def digest(content):
    return hashlib.sha256(content).hexdigest()


def encoded(value):
    return json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"


def open_directory(path):
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    directory_fd = os.open(path.anchor, flags)
    try:
        for component in path.parts[1:]:
            next_fd = os.open(component, flags, dir_fd=directory_fd)
            os.close(directory_fd)
            directory_fd = next_fd
        return directory_fd
    except BaseException:
        os.close(directory_fd)
        raise


def write_output(path, content):
    """Atomically write beneath pinned, existing, unlinked POSIX directories."""
    if os.name != "posix" or not all(hasattr(os, name) for name in ("O_DIRECTORY", "O_NOFOLLOW")):
        raise RuntimeError("Safe verifier output requires POSIX directory-descriptor operations")
    directory_fd = open_directory(path.parent)
    temporary_name = None
    try:
        try:
            existing = os.stat(path.name, dir_fd=directory_fd, follow_symlinks=False)
        except FileNotFoundError:
            existing = None
        if existing is not None and not stat.S_ISREG(existing.st_mode):
            raise ValueError("Verifier output must be a regular file")
        candidate = ".systemx-paper-v2-" + secrets.token_hex(16) + ".json"
        temporary_fd = os.open(candidate, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                               0o600, dir_fd=directory_fd)
        temporary_name = candidate
        with os.fdopen(temporary_fd, "w", encoding="utf-8") as draft:
            draft.write(content)
            draft.flush()
            os.fsync(draft.fileno())
        try:
            current = os.stat(path.name, dir_fd=directory_fd, follow_symlinks=False)
        except FileNotFoundError:
            current = None
        if current is not None and not stat.S_ISREG(current.st_mode):
            raise ValueError("Verifier output changed to a non-regular file")
        pinned = os.fstat(directory_fd)
        visible = os.stat(path.parent, follow_symlinks=False)
        if (pinned.st_dev, pinned.st_ino) != (visible.st_dev, visible.st_ino):
            raise RuntimeError("Verifier output directory changed during write")
        os.replace(temporary_name, path.name, src_dir_fd=directory_fd, dst_dir_fd=directory_fd)
        temporary_name = None
        os.fsync(directory_fd)
    finally:
        if temporary_name is not None:
            os.unlink(temporary_name, dir_fd=directory_fd)
        os.close(directory_fd)


def fixture_check(value):
    checks = {"exactFields": isinstance(value, dict) and set(value) == {"kind", "topic", "value"},
              "researchKind": isinstance(value, dict) and value.get("kind") == "research-note",
              "topicA": isinstance(value, dict) and value.get("topic") == "A",
              "expectedValue": isinstance(value, dict) and type(value.get("value")) is int and value["value"] == 1}
    return {"checks": checks, "passed": all(checks.values())}


def run_example():
    commands = []
    started = time.monotonic()
    source = REPO / ".SYSTEMX"
    manifest_bytes = (source / "config/distribution.json").read_bytes()
    version = (source / "VERSION").read_text(encoding="utf-8").strip()
    with tempfile.TemporaryDirectory(prefix="systemx-paper-v2-") as temporary:
        target = Path(temporary) / "Synthetic Research Project"
        root = target / ".SYSTEMX"

        def public_arg(value):
            return str(value).replace(str(REPO), "<SOURCE>").replace(str(target), "<PROJECT>").replace(
                sys.executable, "<PYTHON>")

        def command(arguments, expected=0):
            remaining = MAX_SECONDS - (time.monotonic() - started)
            require(len(commands) < MAX_COMMANDS and remaining > 0, "Verifier command/time budget exceeded")
            result = subprocess.run([str(value) for value in arguments], capture_output=True,
                                    text=True, encoding="utf-8", timeout=min(20, remaining), shell=False)
            require(result.returncode == expected,
                    "Fixture command failed: " + " ".join(public_arg(value) for value in arguments) +
                    " (expected exit " + str(expected) + ", observed " + str(result.returncode) + ")")
            require("Traceback" not in result.stderr, "Fixture command returned an uncontrolled traceback")
            commands.append({"step": len(commands) + 1, "argv": [public_arg(value) for value in arguments],
                             "expectedReturnCode": expected, "returnCode": result.returncode,
                             "stdoutSha256": digest(result.stdout.encode("utf-8")),
                             "stderrSha256": digest(result.stderr.encode("utf-8"))})
            return result.stdout

        command([sys.executable, "-I", "-B", source / "manager.py", "install",
                 "--source", source, "--target", target])
        launcher = [sys.executable, "-I", "-B", root / "manager.py", "run", "--target", target, "--offline", "--"]

        def cli(*arguments, expected=0):
            return command(launcher + list(arguments), expected)

        def jcli(*arguments):
            return json.loads(cli(*arguments))

        def ledger():
            return json.loads((root / "WORK/TASKS.json").read_text(encoding="utf-8"))

        def task_add(title):
            result = cli("task-add", "--title", title, "--milestone", "M-001", "--scope", "evidence/",
                         "--acceptance", "Inspect the original synthetic fixture evidence for this bounded task")
            match = re.search(r"^Created (TASK-[0-9]{3,})$", result, re.M)
            require(match is not None, "task-add did not return a canonical TASK ID")
            return match.group(1)

        jcli("roles-init", "--apply")
        initialized = jcli("root", "init", "--apply")
        require(initialized["runtimeStarted"] is False, "ROOT setup unexpectedly started a runtime")
        master = root / "PLAN/MASTER-PLAN.md"
        master.write_text(master.read_text(encoding="utf-8") +
                          "\n| M-001 | Compare synthetic research topics A and B | Original local evidence | | |\n",
                          encoding="utf-8")
        evidence = target / "evidence"
        evidence.mkdir()
        artifacts = {}

        def artifact(name, value):
            content = encoded(value).encode("utf-8")
            path = evidence / name
            path.write_bytes(content)
            relative = "evidence/" + name
            artifacts[relative] = digest(content)
            return relative, "fixture:sha256:" + artifacts[relative]

        bad = fixture_check({"kind": "research-note", "topic": "A", "value": 0})
        good = fixture_check({"kind": "research-note", "topic": "A", "value": 1})
        require(not bad["passed"] and good["passed"], "Synthetic check did not distinguish known-bad from valid input")
        artifact("record-known-bad.json", bad)
        accepted_evidence, fixture_revision = artifact("record-verified.json", good)
        task_a = task_add("Verify synthetic research record A")
        task_b = task_add("Continue synthetic research comparison B")
        require([task_a, task_b] == ["TASK-001", "TASK-002"], "Unexpected task identities in an empty disposable project")
        before = (root / "WORK/TASKS.json").read_bytes()
        cli("task-set", task_b, "--status", "done", "--reviewer", "agent.0", "--evidence", accepted_evidence, expected=2)
        require((root / "WORK/TASKS.json").read_bytes() == before, "Premature completion mutated the task ledger")
        cli("task-set", task_a, "--status", "in_progress", "--next", "Check the synthetic record")
        cli("task-set", task_a, "--status", "needs_review", "--evidence", accepted_evidence)
        before = (root / "WORK/TASKS.json").read_bytes()
        cli("task-set", task_a, "--status", "done", "--evidence", accepted_evidence, expected=2)
        require((root / "WORK/TASKS.json").read_bytes() == before, "Missing-reviewer completion mutated the task ledger")
        cli("task-set", task_a, "--status", "done", "--reviewer", "agent.0", "--evidence", accepted_evidence,
            "--note", "Original synthetic fixture evidence inspected by the local verifier")
        cli("task-set", task_b, "--status", "in_progress", "--next", "Continue bounded synthetic evidence comparison")
        origin = jcli("root", "request", "--key", "paper-origin", "--kind", "rtask",
                      "--title", "Compare research topics A and B", "--source-ref", "fixture:human-request", "--apply")["record"]["id"]
        delegated = jcli("root", "request", "--key", "paper-delegation", "--kind", "stask", "--parent", origin,
                         "--title", "Compare the local records", "--source-ref", "fixture:delegated-request", "--apply")["record"]["id"]
        milestone = jcli("root", "node", "--key", "paper-milestone", "--kind", "milestone", "--title", "Evidence comparison",
                          "--request", origin, "--milestone", "M-001", "--apply")["record"]["id"]
        phase = jcli("root", "node", "--key", "paper-phase", "--kind", "phase", "--title", "Local research comparison",
                     "--request", origin, "--parent", milestone, "--apply")["record"]["id"]
        group = jcli("root", "node", "--key", "paper-group", "--kind", "group", "--title", "Topics A and B",
                     "--request", delegated, "--parent", phase, "--task", task_a, "--task", task_b, "--apply")["record"]["id"]
        binding = jcli("root", "bind", "--key", "paper-harness-map", "--layer", "harness", "--channel", "synthetic-harness-fixture",
                       "--item", "research-phase-item", "--task", task_a, "--task", task_b, "--apply")["record"]["id"]
        running_evidence, running_revision = artifact("harness-running.json", {
            "source": "Synthetic local fixture; no native harness plan was queried",
            "item": "research-phase-item", "taskIds": [task_a, task_b], "state": "running", "rawState": "in_progress"})
        observation_args = ["root", "observe", "--key", "paper-running", "--binding", binding, "--raw-state", "in_progress",
                            "--state", "running", "--revision", running_revision, "--expected-revision", running_revision,
                            "--evidence", running_evidence, "--apply"]
        running = jcli(*observation_args)
        aligned = jcli("root", "delta", "--layer", "harness", "--task", task_a, "--task", task_b)
        require(aligned["recordedObservationsAligned"] and not aligned["liveSyncVerified"], "Recorded aggregate fixture did not align truthfully")
        entries = aligned["tasks"][0]["layers"]["harness"]["bindings"]
        require(entries[0]["expectedStates"] == ["running"] and set(entries[0]["coveredTaskIds"]) == {task_a, task_b},
                "Many-to-many projection did not inspect the whole bound TASK set")
        require(aligned["tasks"][0]["layers"]["bot"]["assessment"] == "not_assessed", "Optional bot layer was misrepresented")
        cli("task-set", task_b, "--note", "A new canonical fixture note changes its fingerprint")
        stale = jcli("root", "delta", "--layer", "harness", "--task", task_a)
        stale_entry = stale["tasks"][0]["layers"]["harness"]["bindings"][0]
        require("stale_canonical" in stale_entry["issues"] and stale_entry["staleTaskIds"] == [task_b],
                "An unselected bound task change was not reported stale")
        replay = jcli(*observation_args)
        require(replay["reused"] and replay["record"] == running["record"], "Replay refreshed original timestamps or fingerprints")
        completed_evidence, completed_revision = artifact("provider-completed.json", {
            "source": "Synthetic local provider-result fixture; no provider process was started",
            "item": "research-phase-item", "state": "completed", "rawState": "exit-zero"})
        before = (root / "WORK/TASKS.json").read_bytes()
        completed = jcli("root", "observe", "--key", "paper-provider-completed", "--binding", binding,
                          "--raw-state", "exit-zero", "--state", "completed", "--revision", completed_revision,
                          "--expected-revision", completed_revision, "--evidence", completed_evidence, "--apply")
        divergence = jcli("root", "delta", "--layer", "harness", "--task", task_b)
        require(not completed["taskAccepted"] and (root / "WORK/TASKS.json").read_bytes() == before,
                "Provider completion changed canonical task acceptance")
        require(divergence["tasks"][0]["canonicalStatus"] == "in_progress" and
                not divergence["tasks"][0]["accepted"] and "state_difference" in divergence["tasks"][0]["issues"],
                "Provider completion was not kept separate from task acceptance")
        future = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat().replace("+00:00", "Z")
        event_args = ["agent-x", "event", "--at", future, "--actor-kind", "automation", "--actor-id", "synthetic-fixture",
                      "--kind", "check", "--revision", fixture_revision, "--summary", "Synthetic event-time boundary",
                      "--task", task_b, "--evidence", accepted_evidence]
        events_before = (root / "EVENTS/EVENTS.json").read_bytes()
        cli(*event_args, "--key", "paper-future-occurred", "--stage", "live_verified", expected=2)
        require((root / "EVENTS/EVENTS.json").read_bytes() == events_before, "Future occurred event mutated history")
        planned = jcli(*event_args, "--key", "paper-future-planned", "--stage", "planned")
        require(planned["created"] and planned["event"]["stage"] == "planned", "Future planned event was not retained as planned")
        jcli("agent-x", "validate")
        cli("focus", "--objective", "Continue synthetic research comparison B", "--task", task_a, "--task", task_b)
        packet = jcli("root", "packet", "--task", task_a, "--task", task_b)
        require({item["id"] for item in packet["requests"]} == {origin, delegated}, "Packet lost request ancestry")
        require({item["id"] for item in packet["nodes"]} == {milestone, phase, group}, "Packet lost planning ancestry")
        cli("validate")
        final = ledger()
        require([item["status"] for item in final["tasks"]] == ["done", "in_progress"], "Unexpected final task states")
        result = {"schemaVersion": 1, "passed": True, "templateVersion": version,
                  "recordedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                  "sourceManifestSha256": digest(manifest_bytes), "scope": "Disposable synthetic local coordination records",
                  "checks": {"knownBadFixtureRejected": True, "validFixtureAccepted": True,
                             "prematureDoneRefusedWithoutMutation": True, "missingReviewerRefusedWithoutMutation": True,
                             "manyToManyAggregateExpectedStates": entries[0]["expectedStates"],
                             "unselectedBoundTaskStalenessDetected": True, "observationReplayPreservesOriginal": True,
                             "providerCompletedDoesNotAcceptTask": True, "futureOccurredEventRefusedWithoutMutation": True,
                             "futurePlannedEventRetainedAsPlanned": True, "requestAndPlanningAncestryRetained": True,
                             "generatedViewsValidated": True, "finalTaskStates": [item["status"] for item in final["tasks"]]},
                  "recordIds": {"rtask": origin, "stask": delegated, "milestoneNode": milestone, "phaseNode": phase,
                                "groupNode": group, "binding": binding, "runningObservation": running["record"]["id"],
                                "completedObservation": completed["record"]["id"], "plannedEvent": planned["event"]["id"]},
                  "evidenceSha256": artifacts, "commandCount": len(commands), "commands": commands,
                  "taskAcceptanceAuthority": "WORK/TASKS.json, with recorded Agent 0/user review",
                  "nativeHarnessPlanQueried": False, "providerProcessStarted": False, "externalJobCreated": False,
                  "networkRequestMade": False, "liveSyncVerified": False,
                  "limits": "Implementation walkthrough, not model quality, token/cost savings, swarm throughput, AGI, production, or live-service evidence. External states/revisions are synthetic local fixture claims; no real provider or harness was connected."}
    result["temporaryProjectRemoved"] = not target.exists()
    require(result["temporaryProjectRemoved"], "Disposable project was not removed")
    require(str(REPO) not in encoded(result) and str(temporary) not in encoded(result), "Report retained an absolute owner/temp path")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="regular JSON file under an existing, unlinked POSIX directory")
    args = parser.parse_args()
    result = run_example()
    content = encoded(result)
    if args.output:
        write_output(args.output.expanduser().absolute(), content)
    print(content, end="")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as error:
        # Do not print captured CLI output or host paths into a public report.
        print("White-paper v2 verification failed: " + type(error).__name__, file=sys.stderr)
        sys.exit(1)
