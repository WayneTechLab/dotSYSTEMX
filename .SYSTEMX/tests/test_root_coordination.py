"""ROOT references, bounded three-surface observations, and acceptance separation."""

import argparse
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
from pathlib import Path
import shutil
import sys
import unittest
from unittest.mock import patch

import test_systemx

sys.path.insert(0, str(test_systemx.SOURCE / "scripts"))
sys.path.insert(0, str(test_systemx.SOURCE))
import systemx_paths
import root_coordination as root_tools
import project_memory as memory


class RootCoordinationTests(unittest.TestCase):
    setUp = test_systemx.SystemxTests.setUp
    run_cli = test_systemx.SystemxTests.run_cli
    assert_ok = test_systemx.SystemxTests.assert_ok

    def call(self, *args, scope=None):
        parser = argparse.ArgumentParser()
        root_tools.add_cli(parser.add_subparsers(dest="action", required=True))
        options = parser.parse_args(["root", *args])
        return root_tools.dispatch(scope or self.systemx, self.systemx, options)

    def read(self, name, scope=None):
        return json.loads(((scope or self.systemx) / name).read_text(encoding="utf-8"))

    def save(self, name, value, scope=None):
        ((scope or self.systemx) / name).write_text(json.dumps(value), encoding="utf-8")

    def payloads(self, scope=None):
        scope = scope or self.systemx
        return {p.relative_to(scope).as_posix(): p.read_bytes() for p in scope.rglob("*") if p.is_file()}

    def tasks(self, *statuses, milestone="", scope=None):
        items = []
        for index, status in enumerate(statuses, 1):
            sequence = {"todo": ["todo"], "in_progress": ["todo", "in_progress"],
                        "blocked": ["todo", "blocked"], "needs_review": ["todo", "in_progress", "needs_review"],
                        "done": ["todo", "in_progress", "needs_review", "done"],
                        "cancelled": ["todo", "cancelled"]}[status]
            history = [{"at": "2020-01-01T00:00:0" + str(number) + "Z", "status": state,
                        "owner": "agent.0", "note": "Fixture transition", "evidence": ["proof"] if state == "done" else [],
                        "reviewedBy": "agent.0" if state == "done" else ""} for number, state in enumerate(sequence)]
            items.append({"id": "TASK-{:03d}".format(index), "title": "Fixture " + str(index), "owner": "agent.0",
                          "status": status, "milestone": milestone, "scope": [], "acceptance": ["Original fixture evidence"],
                          "dependsOn": [], "nextAction": "Implement fixture" if status == "in_progress" else "",
                          "blocker": "Fixture blocker" if status == "blocked" else "", "evidence": history[-1]["evidence"],
                          "reviewedBy": history[-1]["reviewedBy"], "createdAt": history[0]["at"],
                          "updatedAt": history[-1]["at"], "history": history})
        self.save("WORK/TASKS.json", {"schemaVersion": 1, "tasks": items}, scope)
        memory.load(scope or self.systemx)
        return items

    def request(self, key="origin", kind="rtask", parent="", scope=None):
        args = ["request", "--key", key, "--kind", kind, "--title", "Accepted outcome", "--source-ref", "human/request-1", "--apply"]
        if parent:
            args += ["--parent", parent]
        return self.call(*args, scope=scope)["record"]["id"]

    def bind(self, key="harness", layer="harness", item="plan-item-1", tasks=("TASK-001",), supersedes="", scope=None):
        args = ["bind", "--key", key, "--layer", layer, "--channel", "fixture-provider", "--item", item, "--apply"]
        for identifier in tasks:
            args += ["--task", identifier]
        if supersedes:
            args += ["--supersedes", supersedes]
        return self.call(*args, scope=scope)["record"]["id"]

    def observe(self, binding, key="observation", state="pending", revision="source-1", expected="source-1", at=None, scope=None):
        args = ["observe", "--key", key, "--binding", binding, "--raw-state", "provider:" + state,
                "--state", state, "--revision", revision, "--evidence", "fixture/original-observation", "--apply"]
        if expected is not None:
            args += ["--expected-revision", expected]
        if at:
            args += ["--at", at]
        return self.call(*args, scope=scope)

    def node(self, key, kind, request, parent="", tasks=(), milestone="", scope=None):
        args = ["node", "--key", key, "--kind", kind, "--title", "Fixture " + kind, "--request", request, "--apply"]
        if parent:
            args += ["--parent", parent]
        if milestone:
            args += ["--milestone", milestone]
        for identifier in tasks:
            args += ["--task", identifier]
        return self.call(*args, scope=scope)["record"]["id"]

    def test_public_seeds_blank_legacy_scope_optional_and_cli_status(self):
        root_tools.validate_template(self.systemx, self.systemx)
        self.assertEqual(self.read(root_tools.PLAN), root_tools.BLANK_PLAN)
        self.assertEqual(self.read(root_tools.MIRRORS), root_tools.BLANK_MIRRORS)
        result = self.run_cli("root", "status")
        self.assert_ok(result)
        self.assertFalse(json.loads(result.stdout)["executed"])
        shutil.rmtree(self.systemx / "ROOT")
        root_tools.validate_optional(self.systemx)
        with self.assertRaises(ValueError):
            self.call("status")

    def test_init_preview_preserves_private_guides_adds_missing_records_and_logs(self):
        shutil.rmtree(self.systemx / "ROOT")
        (self.systemx / "ROOT").mkdir()
        custom = self.systemx / "ROOT/SX-RULES.md"
        custom.write_text("Accepted local policy\n")
        before = self.payloads()
        preview = self.call("init")
        self.assertEqual(len(preview["add"]), 3)
        self.assertEqual(before, self.payloads())
        applied = self.call("init", "--apply")
        self.assertEqual(custom.read_text(), "Accepted local policy\n")
        self.assertEqual(self.read(applied["receipt"])["state"], "complete")
        self.assertFalse(applied["runtimeStarted"])
        before = self.payloads()
        self.assertEqual(self.call("init", "--apply")["add"], [])
        self.assertEqual(before, self.payloads())
        root_tools.validate_optional(self.systemx)

    def test_request_origin_delegation_preview_idempotence_and_conflicting_retry(self):
        before = self.payloads()
        args = ("request", "--key", "first", "--kind", "rtask", "--title", "Outcome", "--source-ref", "owner/request")
        preview = self.call(*args)
        self.assertEqual(before, self.payloads())
        first = self.call(*args, "--apply")["record"]
        self.assertEqual(preview["record"]["id"], first["id"])
        before = self.payloads()
        self.assertTrue(self.call(*args, "--apply")["reused"])
        self.assertEqual(before, self.payloads())
        child = self.request("delegation", "stask", first["id"])
        self.assertTrue(child.startswith("ST-"))
        with self.assertRaises(ValueError):
            self.request("orphan", "stask")
        with self.assertRaises(ValueError):
            self.request("root-parent", "rtask", first["id"])
        with self.assertRaises(ValueError):
            self.call(*args, "--title", "Changed outcome", "--apply")
        self.assertEqual(len(self.read(root_tools.PLAN)["requests"]), 2)

    def test_flexible_hierarchy_deduplicates_task_progress_without_accepting_milestone(self):
        master = self.systemx / "PLAN/MASTER-PLAN.md"
        master.write_text(master.read_text() + "\n| M-001 | Fixture outcome | Proof | | |\n")
        self.tasks("done", "needs_review", milestone="M-001")
        origin = self.request()
        milestone = self.node("milestone", "milestone", origin, milestone="M-001")
        phase = self.node("phase", "phase", origin, parent=milestone)
        self.node("task-a", "task", origin, parent=phase, tasks=("TASK-001", "TASK-002"))
        self.node("task-b", "task", origin, parent=phase, tasks=("TASK-001",))
        progress = self.call("status")["progress"]["milestones"][0]
        self.assertEqual(progress["totalTasks"], 2)
        self.assertEqual(progress["taskCounts"]["done"], 1)
        self.assertFalse(progress["allLinkedTasksAccepted"])
        self.assertFalse(progress["milestoneAcceptanceEstablished"])
        with self.assertRaises(ValueError):
            self.node("backwards", "wave", origin, parent=phase)
        with self.assertRaises(ValueError):
            self.node("unknown-milestone", "milestone", origin, milestone="M-999")
        self.assertEqual(self.read("WORK/TASKS.json")["tasks"][1]["status"], "needs_review")

    def test_many_to_many_aggregate_state_checks_unselected_members(self):
        self.tasks("done", "in_progress", "todo")
        binding = self.bind(tasks=("TASK-001", "TASK-002"))
        self.bind("second-part", item="plan-item-2", tasks=("TASK-002", "TASK-003"))
        self.observe(binding, state="running")
        report = self.call("delta", "--task", "TASK-001")
        self.assertTrue(report["recordedObservationsAligned"])
        entry = report["tasks"][0]["layers"]["harness"]["bindings"][0]
        self.assertEqual(entry["expectedStates"], ["running"])
        self.assertEqual(entry["coveredTaskIds"], ["TASK-001", "TASK-002"])
        self.assertEqual(report["tasks"][0]["layers"]["bot"]["assessment"], "not_assessed")
        self.assertFalse(report["liveSyncVerified"])
        self.tasks("done", "needs_review", "todo")
        changed = self.call("delta", "--task", "TASK-001")["tasks"][0]
        self.assertIn("stale_canonical", changed["issues"])
        self.assertIn("state_difference", changed["issues"])
        self.assertEqual(changed["layers"]["harness"]["bindings"][0]["staleTaskIds"], ["TASK-002"])

    def test_projection_mixed_blocked_cancelled_review_and_completion(self):
        examples = [(("cancelled", "cancelled"), ["cancelled"]),
                    (("todo", "cancelled"), ["pending"]), (("done", "todo"), ["running"]),
                    (("needs_review", "done"), ["completed"]), (("blocked", "todo"), ["blocked"]),
                    (("blocked", "in_progress"), ["blocked", "running"])]
        for statuses, expected in examples:
            with self.subTest(statuses=statuses):
                items = self.tasks(*statuses)
                self.assertEqual(root_tools._expected_states({"taskIds": [item["id"] for item in items]},
                                                            {item["id"]: item for item in items}), expected)

    def test_completed_provider_run_does_not_accept_task_and_missing_revision_is_unverified(self):
        self.tasks("in_progress")
        binding = self.bind()
        before = (self.systemx / "WORK/TASKS.json").read_bytes()
        observed = self.observe(binding, state="completed", expected=None)
        report = self.call("delta")
        self.assertFalse(observed["taskAccepted"])
        self.assertFalse(report["recordedObservationsAligned"])
        self.assertEqual(set(report["tasks"][0]["issues"]), {"state_difference", "revision_unverified"})
        self.assertEqual(before, (self.systemx / "WORK/TASKS.json").read_bytes())
        self.assertFalse(report["tasks"][0]["accepted"])

    def test_observation_retry_preserves_original_time_fingerprints_and_refuses_changed_facts(self):
        self.tasks("todo")
        binding = self.bind()
        original = self.observe(binding)
        before = self.payloads()
        self.assertEqual(self.observe(binding)["record"], original["record"])
        self.assertEqual(before, self.payloads())
        self.tasks("in_progress")
        self.assertTrue(self.observe(binding)["reused"])
        self.assertIn("stale_canonical", self.call("delta")["tasks"][0]["issues"])
        with self.assertRaises(ValueError):
            self.observe(binding, state="running")
        self.assertEqual(len(self.read(root_tools.MIRRORS)["observations"]), 1)

    def test_revision_difference_optional_age_and_latest_original_observation(self):
        self.tasks("todo")
        binding = self.bind()
        self.observe(binding, revision="old", expected="wanted", at="2020-01-02T00:00:00Z")
        report = self.call("delta")
        self.assertEqual(report["tasks"][0]["issues"], ["revision_difference"])
        aged = self.call("delta", "--max-age-seconds", "60")
        self.assertIn("stale_observation", aged["tasks"][0]["issues"])
        self.observe(binding, "current", at="2020-01-03T00:00:00+00:00")
        self.observe(binding, "late-history", revision="old", expected="wanted", at="2020-01-01T00:00:00Z")
        self.assertTrue(self.call("delta")["recordedObservationsAligned"])
        with self.assertRaises(ValueError):
            self.call("delta", "--max-age-seconds", "0")

    def test_superseded_attempt_history_retained_without_remote_cancel_or_stale_comparison(self):
        self.tasks("in_progress")
        previous = self.bind(layer="bot", item="attempt-1")
        self.observe(previous, state="cancelled")
        current = self.bind("replacement", layer="bot", item="attempt-2", supersedes=previous)
        self.observe(current, "replacement-observation", state="running")
        report = self.call("delta", "--layer", "bot")
        self.assertTrue(report["recordedObservationsAligned"])
        self.assertEqual(report["tasks"][0]["layers"]["bot"]["bindings"][0]["item"], "attempt-2")
        self.assertEqual(len(self.read(root_tools.MIRRORS)["observations"]), 2)
        self.assertEqual(self.call("status")["activeBindings"], 1)
        with self.assertRaises(ValueError):
            self.observe(previous, "new-old-attempt", state="running")
        self.tasks("in_progress", "todo")
        with self.assertRaises(ValueError):
            self.bind("changed-attempt-and-set", layer="bot", item="attempt-3", tasks=("TASK-001", "TASK-002"), supersedes=current)

    def test_explicit_binding_mapping_correction_and_ambiguous_duplicate_rejected(self):
        self.tasks("todo", "todo")
        first = self.bind()
        with self.assertRaises(ValueError):
            self.bind("duplicate", tasks=("TASK-001", "TASK-002"))
        corrected = self.bind("corrected", tasks=("TASK-001", "TASK-002"), supersedes=first)
        self.assertNotEqual(first, corrected)
        self.assertEqual(self.call("status")["activeBindings"], 1)

    def test_requested_layers_missing_observation_and_empty_report_are_truthful(self):
        empty = self.call("delta")
        self.assertFalse(empty["recordedObservationsAligned"])
        self.tasks("todo")
        binding = self.bind()
        self.assertEqual(self.call("delta")["tasks"][0]["issues"], ["unavailable"])
        self.observe(binding)
        self.assertTrue(self.call("delta")["recordedObservationsAligned"])
        both = self.call("delta", "--layer", "harness", "--layer", "bot")
        self.assertFalse(both["recordedObservationsAligned"])
        self.assertEqual(both["tasks"][0]["layers"]["bot"]["issues"], ["unmapped"])

    def test_future_observation_invalid_timestamp_and_corrupt_future_history_rejected(self):
        self.tasks("todo")
        binding = self.bind()
        for at in ("2099-01-01T00:00:00Z", "2026-01-01", "20260101T000000Z", "2026-01-01T00:00:00"):
            with self.subTest(at=at), self.assertRaises(ValueError):
                self.observe(binding, at=at)
        self.observe(binding)
        mirrors = self.read(root_tools.MIRRORS)
        mirrors["observations"][0]["at"] = "2099-01-01T00:00:00Z"
        self.save(root_tools.MIRRORS, mirrors)
        with self.assertRaises(ValueError):
            root_tools.validate_optional(self.systemx)

    def test_invalid_json_shape_unknown_fields_links_and_deep_parser_errors_are_controlled(self):
        plan_path = self.systemx / root_tools.PLAN
        for content in ('{"schemaVersion":1,"schemaVersion":1,"requests":[],"nodes":[]}',
                        '{"schemaVersion":NaN,"requests":[],"nodes":[]}',
                        '{"schemaVersion":true,"requests":[],"nodes":[]}',
                        '{"schemaVersion":1,"requests":[],"nodes":[],"extra":0}',
                        '[' * 1100 + '0' + ']' * 1100):
            with self.subTest(prefix=content[:40]):
                plan_path.write_text(content)
                with self.assertRaises(ValueError):
                    root_tools.validate_optional(self.systemx)
        plan_path.unlink()
        target = self.root / "outside-plan.json"
        target.write_text(json.dumps(root_tools.BLANK_PLAN))
        plan_path.symlink_to(target)
        with self.assertRaises(ValueError):
            root_tools.validate_optional(self.systemx)

    def test_malformed_parent_node_is_validated_before_access_and_request_cycles_rejected(self):
        origin = self.request()
        parent = self.node("parent", "phase", origin)
        self.node("child", "task", origin, parent=parent)
        plan = self.read(root_tools.PLAN)
        plan["nodes"].reverse()
        del plan["nodes"][-1]["kind"]
        self.save(root_tools.PLAN, plan)
        with self.assertRaises(ValueError):
            root_tools.validate_optional(self.systemx)
        plan = deepcopy(root_tools.BLANK_PLAN)
        for key, other in (("a", "b"), ("b", "a")):
            plan["requests"].append({"id": root_tools._id("ST", key), "key": key, "kind": "stask", "title": "Cycle",
                                     "sourceRef": "fixture", "parent": root_tools._id("ST", other), "createdAt": "2020-01-01T00:00:00Z"})
        self.save(root_tools.PLAN, plan)
        with self.assertRaisesRegex(ValueError, "cycle"):
            root_tools.validate_optional(self.systemx)

    def test_malformed_enum_reference_types_and_later_binding_parent_reject_cleanly(self):
        self.tasks("todo")
        origin = self.request()
        plan = self.read(root_tools.PLAN)
        plan["requests"][0]["kind"] = []
        self.save(root_tools.PLAN, plan)
        with self.assertRaises(ValueError):
            root_tools.validate_optional(self.systemx)
        plan["requests"][0]["kind"] = "rtask"
        self.save(root_tools.PLAN, plan)
        binding = self.bind()
        self.observe(binding)
        mirrors = self.read(root_tools.MIRRORS)
        bad = deepcopy(mirrors)
        bad["bindings"][0]["layer"] = []
        self.save(root_tools.MIRRORS, bad)
        with self.assertRaises(ValueError):
            root_tools.validate_optional(self.systemx)
        bad = deepcopy(mirrors)
        bad["observations"][0]["binding"] = {}
        self.save(root_tools.MIRRORS, bad)
        with self.assertRaises(ValueError):
            root_tools.validate_optional(self.systemx)
        bad = deepcopy(mirrors)
        child = deepcopy(bad["bindings"][0])
        child.update({"id": root_tools._id("BIND", "child"), "key": "child", "supersedes": binding})
        bad["bindings"] = [child, {"id": binding, "key": "harness"}]
        self.save(root_tools.MIRRORS, bad)
        with self.assertRaises(ValueError):
            root_tools.validate_optional(self.systemx)

    def test_parallel_writers_share_scope_lock_without_losing_requests(self):
        with ThreadPoolExecutor(max_workers=8) as pool:
            identifiers = list(pool.map(lambda index: self.request("parallel-" + str(index)), range(16)))
        self.assertEqual(len(set(identifiers)), 16)
        self.assertEqual(len(self.read(root_tools.PLAN)["requests"]), 16)
        root_tools.validate_optional(self.systemx)

    def test_capacity_and_byte_limits_preserve_old_records(self):
        self.request()
        before = (self.systemx / root_tools.PLAN).read_bytes()
        with patch.object(root_tools, "MAX_REQUESTS", 1), self.assertRaises(ValueError):
            self.request("second")
        self.assertEqual(before, (self.systemx / root_tools.PLAN).read_bytes())
        with patch.object(root_tools, "MAX_BYTES", 32), self.assertRaises(ValueError):
            self.call("status")
        self.assertEqual(before, (self.systemx / root_tools.PLAN).read_bytes())
        with self.assertRaises(ValueError):
            self.call("request", "--key", "long-title", "--kind", "rtask", "--title", "X" * 513, "--source-ref", "fixture", "--apply")
        self.assertEqual(before, (self.systemx / root_tools.PLAN).read_bytes())

    def test_oversized_allowed_observation_preview_and_apply_leave_no_record_or_log(self):
        self.tasks("todo")
        binding = self.bind()
        args = ["root", "observe", "--key", "oversized-observation", "--binding", binding,
                "--raw-state", "pending", "--state", "pending", "--revision", "r1",
                "--expected-revision", "r1"]
        for index in range(100):
            # Each reference is unique and within the allowed 2,048-byte field
            # limit. Their complete public response still exceeds 128 KiB.
            args += ["--evidence", str(index).zfill(3) + "x" * 2045]
        before = self.payloads()
        for suffix in ([], ["--apply"]):
            if sys.platform == "win32":
                # CreateProcess caps the entire command line below this 200 KiB
                # fixture; exercise the same dispatch/output guard in process.
                with self.assertRaisesRegex(ValueError, "ROOT output exceeds 128 KiB"):
                    self.call("observe", *args[2:], *suffix)
            else:
                result = self.run_cli(*args, *suffix)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn("ROOT output exceeds 128 KiB", result.stderr)
                self.assertNotIn("Traceback", result.stderr)
            self.assertEqual(before, self.payloads())
        self.assertEqual(self.read(root_tools.MIRRORS)["observations"], [])

    def test_all_append_commands_preflight_complete_metadata_before_writing(self):
        self.tasks("todo")
        origin = self.request()
        binding = self.bind()
        commands = [
            ["request", "--key", "bounded-request", "--kind", "rtask", "--title", "Outcome", "--source-ref", "fixture"],
            ["node", "--key", "bounded-node", "--kind", "task", "--title", "Work", "--request", origin, "--task", "TASK-001"],
            ["bind", "--key", "bounded-bind", "--layer", "bot", "--channel", "fixture", "--item", "external", "--task", "TASK-001"],
            ["observe", "--key", "bounded-observation", "--binding", binding, "--raw-state", "pending",
             "--state", "pending", "--revision", "r1", "--evidence", "fixture/evidence"],
            ["card", "--key", "bounded-card", "--task", "TASK-001", "--provider", "provider", "--tool", "tool",
             "--purpose", "Purpose", "--input-revision", "r1", "--expected-evidence", "Original result",
             "--permission-boundary", "Existing authorization", "--stop-condition", "One result"],
        ]
        for args in commands:
            with self.subTest(command=args[0]):
                preview = self.call(*args)
                expected = {**preview, "applied": True}
                rendered_size = len((json.dumps(expected, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8"))
                before = self.payloads()
                with patch.object(root_tools, "MAX_OUTPUT_BYTES", rendered_size - 1), self.assertRaises(ValueError):
                    self.call(*args, "--apply")
                self.assertEqual(before, self.payloads())

    def test_fresh_under_lock_candidate_is_checked_before_ledger_replacement(self):
        self.tasks("todo")
        binding = self.bind()
        before = self.payloads()
        original = root_tools._public
        calls = []

        def reject_fresh_candidate(*args, **kwargs):
            calls.append(1)
            if len(calls) == 2:
                raise ValueError("Fixture output grew before the locked write")
            return original(*args, **kwargs)

        with patch.object(root_tools, "_public", side_effect=reject_fresh_candidate), self.assertRaises(ValueError):
            self.observe(binding)
        self.assertEqual(len(calls), 2)
        self.assertEqual(before, self.payloads())

    def test_packet_limit_counts_public_pretty_utf8_output_and_final_metadata(self):
        self.tasks("todo")
        ledger = self.read("WORK/TASKS.json")
        ledger["tasks"][0]["scope"] = ["s" + str(index) for index in range(6000)]
        self.save("WORK/TASKS.json", ledger)
        before = self.payloads()
        result = self.run_cli("root", "packet", "--task", "TASK-001")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("ROOT packet exceeds 64 KiB", result.stderr)
        self.assertEqual(before, self.payloads())
        ledger["tasks"][0]["scope"] = ["s" + str(index) for index in range(100)]
        self.save("WORK/TASKS.json", ledger)
        accepted = self.run_cli("root", "packet", "--task", "TASK-001")
        self.assert_ok(accepted)
        self.assertLessEqual(len(accepted.stdout.encode("utf-8")), root_tools.MAX_PACKET_BYTES)
        # The launcher resolves macOS temporary-directory aliases; direct calls
        # retain their supplied scope spelling, so measure that exact response.
        public = self.call("packet", "--task", "TASK-001")
        rendered_size = len((json.dumps(public, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8"))
        with patch.object(root_tools, "MAX_PACKET_BYTES", rendered_size - 1), self.assertRaises(ValueError):
            self.call("packet", "--task", "TASK-001")

    def test_packet_ancestor_closure_bounded_default_large_task_set_and_selected_scope(self):
        self.tasks(*(["todo"] * 105))
        origin = self.request()
        delegated = self.request("delegated", "stask", origin)
        phase = self.node("phase", "phase", origin)
        self.node("task", "task", delegated, parent=phase, tasks=("TASK-001",))
        packet = self.call("packet", "--task", "TASK-001")
        self.assertEqual({item["id"] for item in packet["requests"]}, {origin, delegated})
        self.assertEqual(len(packet["nodes"]), 2)
        default = self.call("packet")
        self.assertEqual(len(default["tasks"]), 10)
        self.assertTrue(default["truncated"])
        report = self.call("delta")
        self.assertEqual(report["returned"], 10)
        self.assertEqual(report["totalCanonicalTasks"], 105)
        self.assertTrue(report["truncated"])
        self.assertFalse(report["recordedObservationsAligned"])
        with self.assertRaises(ValueError):
            self.call("packet", "--limit", "11")

    def test_tool_card_retains_contract_without_invocation_or_task_acceptance(self):
        self.tasks("todo")
        origin = self.request()
        before = (self.systemx / "WORK/TASKS.json").read_bytes()
        args = ("card", "--key", "card-1", "--request", origin, "--task", "TASK-001", "--provider", "installed-provider",
                "--tool", "selected-tool", "--purpose", "One bounded operation", "--input-revision", "r1",
                "--expected-evidence", "Original command result", "--permission-boundary", "Existing owner authorization",
                "--stop-condition", "Return after one result")
        preview = self.call(*args)
        self.assertEqual(self.read(root_tools.MIRRORS)["cards"], [])
        stored = self.call(*args, "--apply")
        self.assertFalse(stored["toolCalled"])
        self.assertFalse(stored["executed"])
        self.assertFalse(stored["taskAccepted"])
        self.assertEqual(preview["record"]["id"], stored["record"]["id"])
        self.assertEqual(before, (self.systemx / "WORK/TASKS.json").read_bytes())

    def test_child_scope_uses_blank_creation_seeds_and_keeps_parent_private_records_separate(self):
        import project_workspaces
        parent_origin = self.request()
        (self.systemx / "ROOT/SX-RULES.md").write_text("PRIVATE_PARENT_POLICY\n")
        workspaces = project_workspaces.Workspaces(self.systemx, self.systemx)
        workspaces.add("Project-A", "general", "", True)
        child = self.systemx / "Projects/Project-A/.SYSTEMXP"
        self.assertFalse((child / "ROOT").exists())
        self.call("init", "--apply", scope=child)
        self.assertNotIn("PRIVATE_PARENT_POLICY", (child / "ROOT/SX-RULES.md").read_text())
        self.assertEqual(self.read(root_tools.PLAN, child), root_tools.BLANK_PLAN)
        self.tasks("todo", scope=child)
        with self.assertRaises(ValueError):
            self.node("bad-scope", "task", parent_origin, tasks=("TASK-001",), scope=child)
        child_origin = self.request("child-origin", scope=child)
        self.node("child-task", "task", child_origin, tasks=("TASK-001",), scope=child)
        self.assertEqual(len(self.read(root_tools.PLAN)["nodes"]), 0)
        result = self.run_cli("projects", "root", "status", "--project", "Project-A")
        self.assert_ok(result)
        self.assertEqual(json.loads(result.stdout)["canonicalTasks"], 1)


if __name__ == "__main__":
    unittest.main()
