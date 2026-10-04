"""Behavioral checks for role activation, event integrity, fixed reviews, and scope."""

import json
import os
import sys
from pathlib import Path
import unittest
from unittest.mock import patch

import test_systemx
from test_manager import manager


class StandardAgentTests(unittest.TestCase):
    setUp = test_systemx.SystemxTests.setUp
    run_cli = test_systemx.SystemxTests.run_cli
    assert_ok = test_systemx.SystemxTests.assert_ok

    def value(self, *args):
        result = self.run_cli(*args)
        self.assert_ok(result)
        return json.loads(result.stdout[result.stdout.index("{"):])

    def rejected(self, *args):
        result = self.run_cli(*args)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        return result

    def files(self, root=None):
        root = root or self.systemx
        return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}

    def setup_roles(self):
        return self.value("roles-init", "--apply")

    def event(self, *extra):
        return ["agent-x", "event", "--key", "fixture-001", "--at", "2026-01-01T01:00:00+01:00",
                "--summary", "Observed fixture", "--revision", "revision-1", "--actor-kind", "automation",
                "--actor-id", "fixture-runner", "--kind", "check", "--stage", "checked", "--evidence", "proof-1", *extra]

    def prepare(self, revision="revision-1", apply=True):
        return self.value("agent-z", "prepare", "--kind", "change", "--subject", "fixture",
                          "--revision", revision, "--evidence-revision", "proof-1", "--stage", "checked",
                          *(["--apply"] if apply else []))

    def answers(self, result, outcomes):
        path = self.systemx / result["requestPath"]
        data = json.loads(path.read_text())
        for answer, outcome in zip(data["answers"], outcomes):
            answer.update({"result": outcome, "note": "Fixture judgment" if outcome != "unknown" else "",
                           "evidence": ["fixture/evidence"] if outcome in {"pass", "partial", "not_applicable"} else []})
        path.write_text(json.dumps(data))
        return data

    def test_activation_is_explicit_preserving_and_idempotent(self):
        before = self.files()
        preview = self.value("roles-init")
        self.assertEqual(preview["register"], ["agent.x", "agent.z"])
        self.assertEqual(before, self.files())
        self.rejected("agent-x", "due")
        self.assertEqual(before, self.files())
        result = self.setup_roles()
        self.assertFalse(result["runtimeStarted"])
        for key, value in before.items():
            if key != "AGENTS/REGISTRY.json":
                self.assertEqual((self.systemx / key).read_bytes(), value)
        self.assertEqual(json.loads((self.systemx / result["receipt"]).read_text())["state"], "complete")
        after = self.files()
        self.value("roles-init", "--apply")
        self.assertEqual(after, self.files())
        self.assert_ok(self.run_cli("context", "--agent", "agent.x"))
        self.assert_ok(self.run_cli("context", "--agent", "agent.z"))
        self.assert_ok(self.run_cli("validate"))
        self.rejected("validate", "--template")

    def test_existing_policy_memory_and_registry_conflicts_are_preserved(self):
        self.setup_roles()
        p = self.systemx / "AGENTS/agent.z/MEMORY.md"
        p.write_text("Preserve private review facts")
        self.value("roles-init", "--apply")
        self.assertEqual(p.read_text(), "Preserve private review facts")
        registry = self.systemx / "AGENTS/REGISTRY.json"
        data = json.loads(registry.read_text()); data["agents"][-1]["role"] = "different-role"
        registry.write_text(json.dumps(data))
        before = self.files()
        self.rejected("roles-init", "--apply")
        self.assertEqual(before, self.files())

    def test_event_deduplication_time_normalization_and_changed_key_refusal(self):
        self.setup_roles()
        first = self.value(*self.event())
        self.assertEqual(first["event"]["at"], "2026-01-01T00:00:00Z")
        self.assertNotEqual(first["event"]["at"], first["event"]["recordedAt"])
        p = self.systemx / "EVENTS/EVENTS.json"; stamp = p.stat().st_mtime_ns
        self.assertFalse(self.value(*self.event())["created"])
        self.assertEqual(stamp, p.stat().st_mtime_ns)
        before = p.read_bytes()
        self.rejected(*self.event("--revision", "revision-2"))
        self.assertEqual(before, p.read_bytes())
        self.assertEqual(self.value("agent-x", "list")["total"], 1)

    def test_events_require_original_evidence_valid_time_and_local_tasks(self):
        self.setup_roles()
        for extra in [("--at", "2026-01-01T12:00:00"), ("--at", "0001-01-01T00:00:00+01:00"),
                      ("--task", "TASK-999"), ("--summary", "")]:
            with self.subTest(extra=extra):
                self.rejected(*self.event(*extra))
        args = self.event()
        del args[-2:]
        self.rejected(*args)
        self.assertEqual(self.value("agent-x", "list")["total"], 0)
        self.rejected("agent-x", "list", "--since", "2026-02-01T00:00:00Z", "--until", "2026-01-01T00:00:00Z")

    def test_bounded_event_listing_does_not_load_history_into_context(self):
        self.setup_roles()
        for i in range(3):
            self.value(*self.event("--key", "fixture-" + str(i), "--summary", "EVENT_ONLY_FACT"))
        result = self.value("agent-x", "list", "--limit", "2")
        self.assertEqual(result["total"], 3); self.assertTrue(result["truncated"])
        self.assertEqual(len(result["events"]), 2)
        self.assertNotIn("EVENT_ONLY_FACT", self.run_cli("context", "--agent", "agent.x").stdout)
        self.rejected("agent-x", "list", "--limit", "0")

    def test_due_tracking_is_read_only_and_does_not_execute_references(self):
        self.setup_roles()
        scheduled = self.value("agent-x", "schedule", "--key", "due-1", "--title", "Fixture",
                               "--owner", "user", "--due", "2026-01-01T01:00:00+01:00",
                               "--external-ref", "touch must-not-exist.txt")
        self.assertFalse(scheduled["jobCreated"])
        before = self.files()
        self.assertEqual(self.value("agent-x", "due", "--as-of", "2025-12-31T23:59:59Z")["totalDue"], 0)
        due = self.value("agent-x", "due", "--as-of", "2026-01-01T00:00:00Z")
        self.assertEqual(due["totalDue"], 1); self.assertFalse(due["executed"])
        self.assertEqual(before, self.files())
        self.assertFalse((self.root / "must-not-exist.txt").exists())
        identifier = scheduled["item"]["id"]
        self.rejected("agent-x", "close", identifier, "--state", "complete", "--note", "done")
        self.value("agent-x", "close", identifier, "--state", "complete", "--note", "Observed", "--evidence", "proof")
        before = self.files()
        self.value("agent-x", "close", identifier, "--state", "complete", "--note", "Observed", "--evidence", "proof")
        self.assertEqual(before, self.files())
        self.rejected("agent-x", "close", identifier, "--state", "cancelled", "--note", "replace")
        self.assertEqual(self.value("agent-x", "due")["totalDue"], 0)

    def test_policy_has_exactly_one_hundred_stable_questions(self):
        before = self.files()
        policy = self.value("agent-z", "policy")["policy"]
        self.assertEqual(len(policy["categories"]), 10)
        self.assertEqual([len(c["questions"]) for c in policy["categories"]], [10] * 10)
        self.assertEqual(len({q["id"] for c in policy["categories"] for q in c["questions"]}), 100)
        self.assertEqual(before, self.files())

    def test_prepare_preview_and_repeat_preserve_prior_answers(self):
        self.setup_roles()
        before = self.files(); preview = self.prepare(apply=False)
        self.assertEqual(before, self.files())
        result = self.prepare(); self.assertEqual(preview["request"]["id"], result["request"]["id"])
        self.answers(result, ["pass"])
        before = self.files()
        reused = self.prepare()
        self.assertTrue(reused["reused"])
        self.assertEqual(reused["request"]["answers"][0]["result"], "pass")
        self.assertEqual(before, self.files())

    def test_scoring_math_coverage_and_no_task_mutation(self):
        self.setup_roles(); request = self.prepare()
        self.answers(request, ["pass"] * 50 + ["partial"] * 10 + ["fail"] * 10 + ["unknown"] * 20 + ["not_applicable"] * 10)
        before = self.files()
        preview = self.value("agent-z", "score", request["request"]["id"])
        self.assertEqual(before, self.files())
        score = preview["report"]["score"]
        self.assertEqual(score["points"], 55)
        self.assertEqual(score["applicableMaximum"], 90)
        self.assertEqual(score["applicablePercent"], 61.11)
        self.assertEqual(score["coveragePercent"], 77.78)
        self.assertEqual(len(score["categories"]), 10)
        report = self.value("agent-z", "score", request["request"]["id"], "--apply")
        for key, value in before.items(): self.assertEqual((self.systemx / key).read_bytes(), value)
        path = self.systemx / report["reportPath"]; stamp = path.stat().st_mtime_ns
        self.assertTrue(self.value("agent-z", "score", request["request"]["id"], "--apply")["reused"])
        self.assertEqual(stamp, path.stat().st_mtime_ns)

    def test_unknown_and_all_na_reviews_do_not_score_as_complete(self):
        self.setup_roles(); request = self.prepare()
        score = self.value("agent-z", "score", request["request"]["id"])["report"]["score"]
        self.assertEqual(score["points"], 0); self.assertEqual(score["coveragePercent"], 0)
        self.answers(request, ["not_applicable"] * 100)
        score = self.value("agent-z", "score", request["request"]["id"])["report"]["score"]
        self.assertEqual(score["points"], 0); self.assertIsNone(score["applicablePercent"])
        self.assertIsNone(score["coveragePercent"])

    def test_answers_cannot_omit_questions_or_pass_without_evidence(self):
        self.setup_roles(); request = self.prepare()
        path = self.systemx / request["requestPath"]
        original = path.read_text()
        for mutate in [lambda d: d["answers"].pop(), lambda d: d["answers"][0].update(result="pass", note="claim"),
                       lambda d: d["answers"][0].update(result="not_applicable", note="guess"),
                       lambda d: d["answers"][0].update(id="Z99.01")]:
            data = json.loads(original); mutate(data); path.write_text(json.dumps(data))
            self.rejected("agent-z", "score", request["request"]["id"], "--apply")
        self.assertFalse((self.systemx / "REVIEWS/reports").exists())

    def test_comparable_delta_and_report_tampering_refusal(self):
        self.setup_roles(); one = self.prepare()
        before = self.value("agent-z", "score", one["request"]["id"], "--apply")
        two = self.prepare("revision-2"); self.answers(two, ["pass"])
        after = self.value("agent-z", "score", two["request"]["id"], "--apply")
        delta = self.value("agent-z", "compare", before["report"]["id"], after["report"]["id"])
        self.assertEqual(delta["pointDelta"], 1)
        self.assertEqual(len(delta["changes"]), 1)
        self.assertFalse(delta["automaticWork"])
        self.assertTrue(self.value("agent-z", "compare", after["report"]["id"], after["report"]["id"])["sameInputs"])
        p = self.systemx / after["reportPath"]; data = json.loads(p.read_text()); data["score"]["points"] = 100
        p.write_text(json.dumps(data))
        self.rejected("agent-z", "validate", after["report"]["id"])
        self.rejected("agent-z", "score", two["request"]["id"], "--apply")

    def test_policy_edits_require_new_version_and_new_comparison_baseline(self):
        self.setup_roles(); one = self.prepare()
        before = self.value("agent-z", "score", one["request"]["id"], "--apply")
        p = self.systemx / "REVIEWS/POLICY.json"; data = json.loads(p.read_text())
        data["categories"][0]["questions"][0]["question"] = "Is the selected company criterion met?"
        p.write_text(json.dumps(data))
        self.rejected("agent-z", "prepare", "--kind", "change", "--subject", "fixture", "--revision", "revision-2",
                      "--evidence-revision", "proof-1", "--stage", "checked", "--apply")
        data["version"] = "1.0.1"; p.write_text(json.dumps(data)); two = self.prepare("revision-2")
        after = self.value("agent-z", "score", two["request"]["id"], "--apply")
        self.rejected("agent-z", "compare", before["report"]["id"], after["report"]["id"])
        self.assert_ok(self.run_cli("agent-z", "validate", before["report"]["id"]))

    def test_child_roles_and_events_are_isolated(self):
        for name in ("Project-A", "Project-B"):
            self.value("projects", "add", name, "--apply")
        sibling = self.systemx / "Projects/Project-B/.SYSTEMXP"; before = self.files(sibling)
        parent = (self.systemx / "AGENTS/REGISTRY.json").read_bytes()
        self.value("projects", "roles-init", "--project", "Project-A", "--apply")
        event = self.value("projects", *self.event(), "--project", "Project-A")
        self.assertTrue(event["created"])
        output = self.run_cli("projects", "agent-x", "list", "--project", "Project-A")
        self.assert_ok(output)
        self.assertEqual(json.loads(output.stdout)["total"], 1)
        self.assertIn("Project-A", json.loads(output.stdout)["scope"])
        self.value("projects", "agent-z", "policy", "--project", "Project-A")
        self.rejected("projects", "agent-x", "list")
        self.rejected("agent-x", "list")
        self.assertEqual(before, self.files(sibling))
        self.assertEqual(parent, (self.systemx / "AGENTS/REGISTRY.json").read_bytes())
        self.assert_ok(self.run_cli("projects", "validate"))

    def test_record_links_path_escapes_and_duplicate_json_keys_fail_closed(self):
        self.setup_roles()
        self.rejected("agent-z", "score", "../../WORK/TASKS")
        p = self.systemx / "REVIEWS/POLICY.json"
        p.write_text('{"schemaVersion":1,"schemaVersion":2}')
        self.rejected("agent-z", "policy")
        outside = self.root / "outside.json"; outside.write_text('{"keep":true}')
        p.unlink()
        try: os.link(outside, p)
        except OSError: self.skipTest("Hard links unavailable")
        self.rejected("roles-init", "--apply")
        self.assertEqual(outside.read_text(), '{"keep":true}')

    def test_root_memory_hardlinks_are_rejected_like_child_records(self):
        p = self.systemx / "MEMORY/PROJECT.md"; p.unlink()
        outside = self.root / "outside.md"; outside.write_text("private")
        try: os.link(outside, p)
        except OSError: self.skipTest("Hard links unavailable")
        self.rejected("context")
        self.assertEqual(outside.read_text(), "private")

    def test_invalid_child_command_config_is_a_clean_error(self):
        self.value("projects", "add", "Project-A", "--apply")
        (self.systemx / "Projects/Project-A/.SYSTEMXP/project.json").write_text('{}')
        self.rejected("projects", "check", "--project", "Project-A")
        self.rejected("validate")

    def test_manager_refuses_target_override_and_malformed_manifest(self):
        for args in ["context", ["--root", str(self.systemx), "context"], ["--root=" + str(self.systemx), "context"], ["--roo", "elsewhere", "context"], ["--", "--root", "elsewhere"]]:
            with self.subTest(args=args), self.assertRaises(manager.InstallError):
                manager.run(self.root, args)
        (self.systemx / "config/distribution.json").write_text('[]')
        with self.assertRaises(manager.InstallError): manager.read_bundle(self.systemx)

    def test_manager_refuses_duplicate_and_nonfinite_json(self):
        for value in [b'{"schemaVersion":1,"schemaVersion":2}', b'{"value":NaN}', b'{"value":Infinity}']:
            with self.subTest(value=value), self.assertRaises(manager.InstallError):
                manager.decode(value)

    def test_task_records_refuse_shadowed_json_fields(self):
        path = self.systemx / "WORK/TASKS.json"
        path.write_text('{"schemaVersion":1,"tasks":[{}],"tasks":[]}')
        before = path.read_bytes()
        self.rejected("context")
        self.assertEqual(before, path.read_bytes())

    def test_configuration_refuses_shadowed_command_fields(self):
        (self.systemx / "project.json").write_text('{"schemaVersion":1,"schemaVersion":1,"project":{"name":"x","description":""},"checks":[],"commands":{"dev":[],"build":[],"deploy":[]}}')
        result = self.rejected("check")
        self.assertIn("Duplicate JSON", result.stderr)

    def test_runner_refuses_second_global_target_even_from_an_old_bootstrap(self):
        before = self.files()
        self.rejected("--root", str(self.systemx), "--roo", str(self.systemx), "roles-init", "--apply")
        self.assertEqual(before, self.files())

    def test_oversized_record_is_refused_before_replacing_existing_bytes(self):
        with patch.object(sys, "path", [str(test_systemx.SOURCE / "scripts"), *sys.path]):
            import agent_standards
        self.setup_roles()
        path = self.systemx / "EVENTS/EVENTS.json"
        before = path.read_bytes()
        with patch.object(agent_standards, "MAX_RECORD_BYTES", 100):
            with self.assertRaisesRegex(ValueError, "exceed"):
                agent_standards.write(self.systemx, "EVENTS/EVENTS.json", {"text": "é" * 100})
        self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
