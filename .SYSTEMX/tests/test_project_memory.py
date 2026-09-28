"""Task acceptance, context isolation, and durable record consistency checks."""

import json
import copy
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

    def test_long_dependency_chain_is_independent_of_record_order_and_recursion_limit(self):
        self.add()
        seed = self.ledger()["tasks"][0]
        tasks = []
        for number in range(1, 1101):
            task = copy.deepcopy(seed)
            task["id"] = "TASK-{:03d}".format(number)
            task["dependsOn"] = ["TASK-{:03d}".format(number - 1)] if number > 1 else []
            tasks.append(task)
        ledger = {"schemaVersion": 1, "tasks": list(reversed(tasks))}
        self.write_ledger(ledger)
        self.assert_ok(self.run_cli("refresh-work"))
        self.assert_ok(self.run_cli("validate"))
        tasks[0]["dependsOn"] = ["TASK-1100"]
        self.write_ledger(ledger)
        self.assertIn("cycle", self.run_cli("refresh-work").stderr)

    def test_history_must_begin_at_creation_and_preserve_observation_order(self):
        task_id = self.add()
        self.start(task_id)
        ledger = self.ledger()
        task = ledger["tasks"][0]
        task["createdAt"] = "2026-01-01T00:00:00Z"
        task["history"][0]["at"] = "2026-01-02T00:00:00Z"
        self.write_ledger(ledger)
        self.assertIn("begin at createdAt", self.run_cli("refresh-work").stderr)
        task["history"][0]["at"] = task["createdAt"]
        task["history"][1]["at"] = task["updatedAt"] = "2025-12-31T00:00:00Z"
        self.write_ledger(ledger)
        self.assertIn("remain chronological", self.run_cli("refresh-work").stderr)

    def test_manual_records_cannot_retain_inapplicable_current_fields(self):
        self.add()
        ledger = self.ledger()
        task = ledger["tasks"][0]
        task["blocker"] = "Stale blocker on a TODO task"
        self.write_ledger(ledger)
        self.assertIn("Only blocked tasks", self.run_cli("refresh-work").stderr)
        task["blocker"] = ""
        task["reviewedBy"] = task["history"][-1]["reviewedBy"] = "agent.0"
        self.write_ledger(ledger)
        self.assertIn("Only completed tasks", self.run_cli("refresh-work").stderr)

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

    def test_focus_projects_current_task_state_without_mutating_the_ledger(self):
        task_id = self.add("Current objective")
        before = (self.systemx / "WORK/TASKS.json").read_bytes()
        self.assert_ok(self.run_cli("focus", "--objective", "Finish the accepted outcome", "--task", task_id))
        self.assertEqual((self.systemx / "WORK/TASKS.json").read_bytes(), before)
        self.start(task_id)
        current = (self.systemx / "CURRENT.md").read_text()
        self.assertIn("in_progress / agent.0", current)
        self.assertIn("Run the focused check", current)
        self.assert_ok(self.run_cli("task-set", task_id, "--status", "blocked", "--blocker", "Fixture missing"))
        self.assertIn("Fixture missing", (self.systemx / "CURRENT.md").read_text())
        focus = json.loads((self.systemx / "WORK/FOCUS.json").read_text())
        self.assertNotIn("status", focus)
        self.assertNotIn("blocker", focus)
        self.assert_ok(self.run_cli("validate"))

    def test_invalid_focus_is_rejected_before_mutating_either_record(self):
        task_id = self.add()
        before = [(self.systemx / path).read_bytes() for path in ("WORK/FOCUS.json", "CURRENT.md")]
        for arguments in [(), ("--objective", " "), ("--objective", "x" * 601),
                          ("--objective", "Work", "--task", "TASK-999"),
                          ("--objective", "Work", "--task", task_id, "--task", task_id),
                          ("--clear", "--objective", "Work")]:
            self.assertEqual(self.run_cli("focus", *arguments).returncode, 2)
            self.assertEqual([(self.systemx / path).read_bytes() for path in ("WORK/FOCUS.json", "CURRENT.md")], before)

    def test_checkpoint_pointer_is_contained_and_clear_preserves_history(self):
        task_id = self.add()
        checkpoint = self.systemx / "MEMORY/sessions/session.md"
        checkpoint.write_text("Original observation and source credit\n")
        args = ("focus", "--objective", "Resume existing work", "--task", task_id, "--checkpoint")
        for bad in ("../outside.md", "MEMORY/sessions/missing.md", "MEMORY/sessions/README.md",
                    "MEMORY/PROJECT.md", str(checkpoint), "MEMORY/sessions/../PROJECT.md"):
            self.assertEqual(self.run_cli(*args, bad).returncode, 2)
        outside = Path(self.temp.name) / "private.md"
        outside.write_text("Other project memory\n")
        (self.systemx / "MEMORY/sessions/link.md").symlink_to(outside)
        self.assertEqual(self.run_cli(*args, "MEMORY/sessions/link.md").returncode, 2)
        (self.systemx / "MEMORY/sessions/link.md").unlink()
        self.assert_ok(self.run_cli(*args, "MEMORY/sessions/session.md"))
        before = (self.systemx / "WORK/TASKS.json").read_bytes()
        self.assert_ok(self.run_cli("focus", "--clear"))
        self.assertEqual(checkpoint.read_text(), "Original observation and source credit\n")
        self.assertEqual((self.systemx / "WORK/TASKS.json").read_bytes(), before)
        self.assertIn("No current objective recorded", (self.systemx / "CURRENT.md").read_text())

    def test_focus_lock_and_stale_current_view_are_handled(self):
        task_id = self.add()
        lock = self.systemx / "state/coordination.lock"
        lock.mkdir()
        self.assertEqual(self.run_cli("focus", "--objective", "Work", "--task", task_id).returncode, 2)
        lock.rmdir()
        self.assert_ok(self.run_cli("focus", "--objective", "Work", "--task", task_id))
        current = self.systemx / "CURRENT.md"
        expected = current.read_bytes()
        current.write_text("Hand-maintained stale result\n")
        self.assertIn("CURRENT.md is stale", self.run_cli("validate").stderr)
        self.assert_ok(self.run_cli("refresh-work"))
        self.assertEqual(current.read_bytes(), expected)

    def test_obsolete_checkpoint_can_be_replaced_without_resetting_work(self):
        task_id = self.add()
        checkpoint = self.systemx / "MEMORY/sessions/old.md"
        checkpoint.write_text("Dated evidence\n")
        self.assert_ok(self.run_cli("focus", "--objective", "Work", "--task", task_id,
                                    "--checkpoint", "MEMORY/sessions/old.md"))
        checkpoint.rename(checkpoint.with_name("archived.md"))
        self.assertIn("Checkpoint must name", self.run_cli("validate").stderr)
        before = (self.systemx / "WORK/TASKS.json").read_bytes()
        self.assert_ok(self.run_cli("focus", "--objective", "Work", "--task", task_id,
                                    "--checkpoint", "MEMORY/sessions/archived.md"))
        self.assertEqual((self.systemx / "WORK/TASKS.json").read_bytes(), before)
        self.assert_ok(self.run_cli("validate"))

    def test_readiness_excludes_active_blocked_review_terminal_and_waiting_work(self):
        first = self.add("Prerequisite")
        dependent = self.add("Waiting", "--depends-on", first)
        active = self.add("Active")
        self.start(active)
        blocked = self.add("Blocked")
        self.assert_ok(self.run_cli("task-set", blocked, "--status", "blocked", "--blocker", "Needs input"))
        cancelled = self.add("Cancelled prerequisite")
        self.assert_ok(self.run_cli("task-set", cancelled, "--status", "cancelled", "--note", "Withdrawn"))
        dead_end = self.add("Needs cancelled work", "--depends-on", cancelled)
        review = self.add("Review")
        self.start(review)
        self.assert_ok(self.run_cli("task-set", review, "--status", "needs_review"))
        result = self.run_cli("task-ready")
        self.assert_ok(result)
        self.assertIn(first, result.stdout)
        for task in (dependent, active, blocked, cancelled, dead_end, review):
            self.assertNotIn(task, result.stdout)
        self.complete(first)
        result = self.run_cli("task-ready")
        self.assertIn(dependent, result.stdout)
        self.assertNotIn(first, result.stdout)

    def test_task_packet_is_bounded_preserves_dependency_credit_and_is_read_only(self):
        self.assert_ok(self.run_cli("agent-add", "agent.1", "--role", "test"))
        (self.systemx / "AGENTS/agent.1/MEMORY.md").write_text("UNRELATED_WORKER_PRIVATE_CONTEXT")
        first = self.add("Accepted source")
        self.complete(first)
        task_id = self.add("Runtime acceptance", "--depends-on", first, "--scope", "src/feature.py")
        before = {str(path.relative_to(self.systemx)): path.read_bytes()
                  for path in self.systemx.rglob("*") if path.is_file()}
        result = self.run_cli("task-packet", task_id, "--base", "observed-commit")
        self.assert_ok(result)
        for value in (task_id, first, "observed-commit", "src/feature.py", '"status": "done"', '"reviewedBy": "agent.0"'):
            self.assertIn(value, result.stdout)
        self.assertNotIn("UNRELATED_WORKER_PRIVATE_CONTEXT", result.stdout)
        self.assertNotIn('"history"', result.stdout)
        self.assertIn("does not dispatch", result.stdout)
        self.assert_ok(self.run_cli("task-ready", "--agent", "agent.0"))
        self.assertEqual(self.run_cli("task-ready", "--agent", "agent.99").returncode, 2)
        self.assertEqual(self.run_cli("task-packet", "TASK-999", "--base", "source").returncode, 2)
        after = {str(path.relative_to(self.systemx)): path.read_bytes()
                 for path in self.systemx.rglob("*") if path.is_file()}
        self.assertEqual(before, after)
        (self.systemx / "AGENTS/agent.0/MEMORY.md").write_text("x" * 4000 + "TAIL_NOT_LOADED")
        result = self.run_cli("task-packet", task_id, "--base", "source")
        self.assertIn("Memory truncated after 3000", result.stdout)
        self.assertNotIn("TAIL_NOT_LOADED", result.stdout)

    def test_focus_tasks_are_loaded_before_a_large_backlog(self):
        for index in range(26):
            task_id = self.add("Task " + str(index))
        self.assert_ok(self.run_cli("focus", "--objective", "Continue the accepted plan", "--task", task_id))
        result = self.run_cli("context")
        self.assert_ok(result)
        self.assertLess(result.stdout.index("CURRENT.md (from canonical records)"), result.stdout.index("--- GLOBAL/CONTEXT.md ---"))
        tasks = result.stdout.split("--- Relevant open tasks: 26 ---")[1]
        self.assertLess(tasks.index("TASK-026"), tasks.index("TASK-001"))
        self.assertIn("Showing 25 tasks", result.stdout)


if __name__ == "__main__":
    unittest.main()
