"""Task acceptance, context isolation, and durable record consistency checks."""

import json
from pathlib import Path
import unittest

import test_systemx


class ProjectMemoryTests(unittest.TestCase):
    setUp = test_systemx.SystemxTests.setUp
    run_cli = test_systemx.SystemxTests.run_cli
    assert_ok = test_systemx.SystemxTests.assert_ok

    def ledger(self):
        return json.loads((self.systemx / "WORK/TASKS.json").read_text())

    def add(self, title="Focused change", *extra):
        result = self.run_cli("task-add", "--title", title,
                              "--acceptance", "Relevant behavior is verified", *extra)
        self.assert_ok(result)
        return self.ledger()["tasks"][-1]["id"]

    def start(self, task_id):
        self.assert_ok(self.run_cli("task-set", task_id, "--status", "in_progress",
                                    "--next", "Run the focused check"))

    def complete(self, task_id):
        self.start(task_id)
        self.assert_ok(self.run_cli("task-set", task_id, "--status", "needs_review",
                                    "--evidence", "Fixture test passed at the recorded revision"))
        self.assert_ok(self.run_cli("task-set", task_id, "--status", "done", "--reviewer", "agent.0"))

    def write_ledger(self, data):
        (self.systemx / "WORK/TASKS.json").write_text(json.dumps(data))

    def test_blank_status_and_context_do_not_create_work_or_claim_completion(self):
        before = {str(path.relative_to(self.systemx)): path.read_bytes()
                  for path in self.systemx.rglob("*") if path.is_file()}
        result = self.run_cli("status")
        self.assert_ok(result)
        self.assertIn("does not establish project completion", result.stdout)
        result = self.run_cli("context", "--agent", "agent.0")
        self.assert_ok(result)
        self.assertIn("No assigned open work", result.stdout)
        after = {str(path.relative_to(self.systemx)): path.read_bytes()
                 for path in self.systemx.rglob("*") if path.is_file()}
        self.assertEqual(before, after)

    def test_task_creation_generates_views_and_stable_ids(self):
        self.assertEqual(self.add(), "TASK-001")
        self.assertEqual(self.add("Second change"), "TASK-002")
        self.assertIn("Focused change", (self.systemx / "WORK/TODO.md").read_text())
        self.assert_ok(self.run_cli("validate"))

    def test_registration_creates_scoped_memory_and_preserves_existing_notes(self):
        result = self.run_cli("agent-add", "agent.1", "--role", "test")
        self.assert_ok(result)
        self.assertIn("No agent process was started", result.stdout)
        memory = self.systemx / "AGENTS/agent.1/MEMORY.md"
        self.assertIn("# agent.1 memory", memory.read_text())
        memory.write_text("Worker's existing checkpoint\n")
        self.assertEqual(self.run_cli("agent-add", "agent.1", "--role", "code").returncode, 2)
        self.assertEqual(memory.read_text(), "Worker's existing checkpoint\n")
        self.add("Worker assignment", "--owner", "agent.1")
        self.assert_ok(self.run_cli("validate"))

    def test_unknown_owners_and_invalid_agent_paths_do_not_mutate_ledger(self):
        before = (self.systemx / "WORK/TASKS.json").read_bytes()
        self.assertEqual(self.run_cli("task-add", "--title", "Bad owner", "--acceptance", "proof",
                                      "--owner", "agent.99").returncode, 2)
        self.assertEqual(self.run_cli("agent-add", "../outside", "--role", "test").returncode, 2)
        self.assertEqual((self.systemx / "WORK/TASKS.json").read_bytes(), before)

    def test_done_requires_review_transition_evidence_and_reviewer(self):
        task_id = self.add()
        self.assertEqual(self.run_cli("task-set", task_id, "--status", "done", "--reviewer", "agent.0",
                                      "--evidence", "unreviewed").returncode, 2)
        self.start(task_id)
        self.assert_ok(self.run_cli("task-set", task_id, "--status", "needs_review"))
        self.assertEqual(self.run_cli("task-set", task_id, "--status", "done", "--reviewer", "agent.0").returncode, 2)
        self.assertEqual(self.run_cli("task-set", task_id, "--status", "done", "--evidence", "proof").returncode, 2)
        self.assert_ok(self.run_cli("task-set", task_id, "--status", "done",
                                    "--evidence", "Reviewed proof", "--reviewer", "user"))
        self.assertIn("Reviewed proof", (self.systemx / "WORK/DONE.md").read_text())
        self.assertNotIn(task_id, (self.systemx / "WORK/REVIEW.md").read_text())
        self.assert_ok(self.run_cli("validate"))

    def test_reopen_preserves_history_and_clears_current_acceptance(self):
        task_id = self.add()
        self.complete(task_id)
        self.assertEqual(self.run_cli("task-set", task_id, "--note", "silent terminal edit").returncode, 2)
        self.assert_ok(self.run_cli("task-set", task_id, "--status", "todo", "--note", "New regression"))
        task = self.ledger()["tasks"][0]
        self.assertEqual(task["evidence"], [])
        self.assertEqual(task["reviewedBy"], "")
        self.assertEqual(task["history"][-2]["status"], "done")
        self.assertTrue(task["history"][-2]["evidence"])
        self.assertEqual(task["history"][-1]["note"], "New regression")
        self.assert_ok(self.run_cli("validate"))

    def test_blocked_and_cancelled_require_a_reason(self):
        task_id = self.add()
        self.assertEqual(self.run_cli("task-set", task_id, "--status", "blocked").returncode, 2)
        self.assert_ok(self.run_cli("task-set", task_id, "--status", "blocked",
                                    "--blocker", "Need the agreed fixture from its owner"))
        self.assertIn("Need the agreed fixture", (self.systemx / "WORK/BLOCKED.md").read_text())
        self.assertEqual(self.run_cli("task-set", task_id, "--status", "cancelled").returncode, 2)
        self.assert_ok(self.run_cli("task-set", task_id, "--status", "cancelled", "--note", "Scope withdrawn"))
        self.assertIn("Scope withdrawn", (self.systemx / "WORK/CANCELLED.md").read_text())

    def test_dependencies_gate_start_and_prevent_invalid_reopening(self):
        first = self.add("Prerequisite")
        second = self.add("Dependent", "--depends-on", first)
        self.assertEqual(self.run_cli("task-set", second, "--status", "in_progress", "--next", "Do work").returncode, 2)
        self.complete(first)
        self.start(second)
        self.assertEqual(self.run_cli("task-set", first, "--status", "todo").returncode, 2)
        self.assertEqual(self.ledger()["tasks"][0]["status"], "done")
        self.assert_ok(self.run_cli("validate"))

    def test_unknown_dependencies_and_cycles_are_rejected(self):
        result = self.run_cli("task-add", "--title", "Missing dependency", "--acceptance", "proof",
                              "--depends-on", "TASK-999")
        self.assertEqual(result.returncode, 2)
        first = self.add("One")
        second = self.add("Two", "--depends-on", first)
        ledger = self.ledger()
        ledger["tasks"][0]["dependsOn"] = [second]
        self.write_ledger(ledger)
        self.assertIn("cycle", self.run_cli("refresh-work").stderr)

    def test_milestones_must_be_declared_in_the_master_plan(self):
        self.assertEqual(self.run_cli("task-add", "--title", "Plan item", "--acceptance", "proof",
                                      "--milestone", "M-001").returncode, 2)
        plan = self.systemx / "PLAN/MASTER-PLAN.md"
        plan.write_text(plan.read_text() + "\n| M-001 | Working feature | Reviewed proof | None | |\n")
        self.add("Plan item", "--milestone", "M-001")
        self.assertEqual(self.ledger()["tasks"][0]["milestone"], "M-001")
        self.assert_ok(self.run_cli("validate"))

    def test_stale_views_are_detected_and_rebuilt_without_changing_records(self):
        self.add()
        ledger_before = (self.systemx / "WORK/TASKS.json").read_bytes()
        view = self.systemx / "WORK/TODO.md"
        expected = view.read_bytes()
        view.write_text("Outdated manual status\n")
        result = self.run_cli("validate")
        self.assertEqual(result.returncode, 2)
        self.assertIn("stale", result.stderr)
        self.assert_ok(self.run_cli("refresh-work"))
        self.assertEqual(view.read_bytes(), expected)
        self.assertEqual((self.systemx / "WORK/TASKS.json").read_bytes(), ledger_before)

    def test_lock_contention_does_not_overwrite_task_records(self):
        self.add()
        lock = self.systemx / "state/coordination.lock"
        lock.mkdir()
        before = (self.systemx / "WORK/TASKS.json").read_bytes()
        result = self.run_cli("task-add", "--title", "Concurrent write", "--acceptance", "proof")
        self.assertEqual(result.returncode, 2)
        self.assertIn("writer is busy", result.stderr)
        self.assertEqual((self.systemx / "WORK/TASKS.json").read_bytes(), before)
        self.assertTrue(lock.is_dir())
        lock.rmdir()
        self.add("Successful retry")

    def test_symlinked_worker_memory_cannot_escape_the_project(self):
        outside = Path(self.temp.name) / "outside-agent"
        outside.mkdir()
        (self.systemx / "AGENTS/agent.1").symlink_to(outside, target_is_directory=True)
        self.assertEqual(self.run_cli("agent-add", "agent.1", "--role", "test").returncode, 2)
        self.assertEqual(list(outside.iterdir()), [])

    def test_context_loads_shared_and_selected_worker_memory_without_other_workers_or_archives(self):
        for number in (1, 2):
            self.assert_ok(self.run_cli("agent-add", "agent." + str(number), "--role", "test"))
            (self.systemx / f"AGENTS/agent.{number}/MEMORY.md").write_text(f"WORKER_{number}_CHECKPOINT\n")
        (self.systemx / "GLOBAL/CONTEXT.md").write_text("SHARED_PROJECT_FACT\n")
        (self.systemx / "MEMORY/sessions/old.md").write_text("OLD_ARCHIVE_NOT_PRELOADED\n")
        self.add("Selected worker task", "--owner", "agent.1")
        self.add("Other worker task", "--owner", "agent.2")
        result = self.run_cli("context", "--agent", "agent.1")
        self.assert_ok(result)
        self.assertIn("WORKER_1_CHECKPOINT", result.stdout)
        self.assertIn("SHARED_PROJECT_FACT", result.stdout)
        self.assertIn("Selected worker task", result.stdout)
        self.assertNotIn("WORKER_2_CHECKPOINT", result.stdout)
        self.assertNotIn("Other worker task", result.stdout)
        self.assertNotIn("OLD_ARCHIVE_NOT_PRELOADED", result.stdout)
        self.assertEqual(self.run_cli("context", "--agent", "agent.99").returncode, 2)

    def test_context_truncates_large_records_with_a_read_more_notice(self):
        (self.systemx / "MEMORY/PROJECT.md").write_text("x" * 7000 + "END_NOT_PRELOADED")
        result = self.run_cli("context")
        self.assert_ok(result)
        self.assertIn("Truncated after 6000", result.stdout)
        self.assertNotIn("END_NOT_PRELOADED", result.stdout)

    def test_manual_completion_without_consistent_review_history_is_rejected(self):
        self.add()
        ledger = self.ledger()
        task = ledger["tasks"][0]
        task.update(status="done", evidence=["Manual claim"], reviewedBy="agent.0")
        self.write_ledger(ledger)
        self.assertIn("history event disagree", self.run_cli("validate").stderr)
        task["history"][-1].update(status="done", evidence=["Manual claim"], reviewedBy="agent.0")
        self.write_ledger(ledger)
        self.assertIn("history must start", self.run_cli("validate").stderr)

    def test_full_task_record_exposes_history_and_evidence_for_review(self):
        task_id = self.add()
        self.complete(task_id)
        result = self.run_cli("task-show", task_id)
        self.assert_ok(result)
        task = json.loads(result.stdout)
        self.assertEqual([event["status"] for event in task["history"]],
                         ["todo", "in_progress", "needs_review", "done"])
        self.assertTrue(task["evidence"])


if __name__ == "__main__":
    unittest.main()
