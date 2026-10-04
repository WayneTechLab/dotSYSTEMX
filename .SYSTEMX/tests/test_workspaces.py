"""Project routing, preservation, selected execution, and managed lifecycle checks."""

import json
import os
from pathlib import Path
import shutil
import sys
import unittest

import test_systemx
from test_manager import manager


class WorkspaceTests(unittest.TestCase):
    setUp = test_systemx.SystemxTests.setUp
    run_cli = test_systemx.SystemxTests.run_cli
    assert_ok = test_systemx.SystemxTests.assert_ok

    def cli(self, *args):
        return self.run_cli("projects", *args)

    def add(self, name="Project-A"):
        self.assert_ok(self.cli("add", name, "--apply"))
        return self.systemx / "Projects" / name / ".SYSTEMXP"

    def files(self, root=None):
        root = root or self.systemx
        return {p.relative_to(root).as_posix(): p.read_bytes()
                for p in root.rglob("*") if p.is_file()}

    def test_preview_is_read_only_and_creation_is_blank_with_receipt(self):
        before = self.files()
        self.assert_ok(self.cli("add", "Project-A"))
        self.assertEqual(before, self.files())
        # Active parent facts must not become child defaults.
        (self.systemx / "MEMORY/PROJECT.md").write_text("PARENT PRIVATE FACT")
        records = self.add()
        self.assertNotIn("PARENT PRIVATE FACT", (records / "MEMORY/PROJECT.md").read_text())
        self.assertEqual(json.loads((records / "WORK/TASKS.json").read_text())["tasks"], [])
        self.assertEqual(len(json.loads((records / "AGENTS/REGISTRY.json").read_text())["agents"]), 1)
        self.assertFalse((records / "Projects").exists())
        self.assertFalse((records / ".SYSTEMX").exists())
        self.assertFalse((records / "manager.py").exists())
        receipt = next((self.systemx / "logs/projects").glob("*.json"))
        self.assertEqual(json.loads(receipt.read_text())["state"], "complete")
        self.assert_ok(self.cli("validate"))
        self.assert_ok(self.run_cli("validate"))
        self.assertEqual(self.run_cli("validate", "--template").returncode, 2)

    def test_exact_selection_and_portable_names(self):
        self.add("Project A")
        for args in [("status",), ("context",), ("task-add", "--title", "x", "--acceptance", "y"),
                     ("status", "--project", "project a"), ("status", "--project", "../Project A"),
                     ("status", "--project", "Project A", "--root")]:
            with self.subTest(args=args):
                self.assertEqual(self.cli(*args).returncode, 2)
        for name in ("../X", "x/y", "x\\y", "root", "CON", "LPT1", "name.", "name ", "x:y"):
            with self.subTest(name=name):
                self.assertEqual(self.cli("add", name, "--apply").returncode, 2)
        self.assert_ok(self.cli("context", "--project", "Project A"))
        self.assertIn("'Project A'", (self.systemx / "Projects/Project A/.SYSTEMXP/WORK/TODO.md").read_text())

    def test_duplicate_and_existing_folder_preserved(self):
        self.add()
        before = self.files()
        self.assertEqual(self.cli("add", "Project-A", "--apply").returncode, 2)
        self.assertEqual(self.cli("add", "project-a", "--apply").returncode, 2)
        self.assertEqual(before, self.files())
        folder = self.systemx / "Projects/Project-B"
        folder.mkdir()
        (folder / "user.txt").write_text("keep")
        before = self.files()
        self.assertEqual(self.cli("add", "Project-B", "--apply").returncode, 2)
        self.assertEqual(before, self.files())

    def test_tasks_roles_focus_and_acceptance_are_isolated(self):
        a = self.add()
        b = self.add("Project-B")
        untouched = self.files(b)
        parent_ledger = (self.systemx / "WORK/TASKS.json").read_bytes()
        self.assert_ok(self.cli("agent-add", "agent.1", "--role", "test", "--project", "Project-A"))
        self.assert_ok(self.cli("task-add", "--project", "Project-A", "--title", "A_ONLY",
                                "--owner", "agent.1", "--acceptance", "Fixture verified"))
        self.assert_ok(self.cli("focus", "--project", "Project-A", "--objective", "A_ONLY", "--task", "TASK-001"))
        packet = self.cli("task-packet", "TASK-001", "--project", "Project-A", "--base", "observed-fixture")
        self.assert_ok(packet)
        self.assertIn("Canonical child records:", packet.stdout)
        self.assertIn("Project-A/.SYSTEMXP", packet.stdout.replace("\\", "/"))
        self.assertNotIn("Canonical project directory: .SYSTEMX", packet.stdout)
        self.assertEqual(self.cli("task-set", "TASK-001", "--project", "Project-A", "--status", "done",
                                 "--reviewer", "agent.0").returncode, 2)
        for args in [("--status", "in_progress", "--next", "Run fixture"),
                     ("--status", "needs_review", "--evidence", "Fixture passed"),
                     ("--status", "done", "--reviewer", "agent.0")]:
            self.assert_ok(self.cli("task-set", "TASK-001", "--project", "Project-A", *args))
        self.assertEqual(untouched, self.files(b))
        self.assertEqual(parent_ledger, (self.systemx / "WORK/TASKS.json").read_bytes())
        for args in [("context", "--root"), ("status", "--root"), ("context", "--project", "Project-B")]:
            result = self.cli(*args)
            self.assert_ok(result)
            self.assertNotIn("A_ONLY", result.stdout)
        self.assertIn(".SYSTEMXP/WORK/TASKS.json", (a / "AGENTS/agent.1/MEMORY.md").read_text())
        self.assert_ok(self.cli("validate"))

    def test_unselected_invalid_sibling_does_not_block_context_or_list(self):
        self.add()
        b = self.add("Project-B")
        (b / "WORK/TASKS.json").write_text("bad json")
        self.assert_ok(self.cli("list"))
        self.assert_ok(self.cli("context", "--root"))
        self.assert_ok(self.cli("context", "--project", "Project-A"))
        self.assertEqual(self.cli("validate").returncode, 2)

    def test_status_refresh_only_writes_selected_snapshot_and_is_idempotent(self):
        a = self.add()
        self.add("Project-B")
        before = self.files()
        self.assert_ok(self.cli("refresh-status", "--project", "Project-A"))
        self.assertEqual(before, self.files())
        self.assert_ok(self.cli("refresh-status", "--project", "Project-A", "--apply"))
        after = self.files()
        self.assertEqual(set(after) - set(before), {"Projects/Project-A/.SYSTEMXP/SYNC/STATUS.json"})
        for key in before:
            self.assertEqual(before[key], after[key])
        p = a / "SYNC/STATUS.json"
        stamp = p.stat().st_mtime_ns
        self.assert_ok(self.cli("refresh-status", "--project", "Project-A", "--apply"))
        self.assertEqual(stamp, p.stat().st_mtime_ns)
        status = json.loads(p.read_text())
        self.assertEqual(status["scope"], "Project-A")
        self.assertEqual(sum(status["taskCounts"].values()), 0)

    def test_registry_tampering_case_paths_and_nested_markers_are_refused(self):
        a = self.add()
        p = self.systemx / "Projects/REGISTRY.json"
        original = p.read_bytes()
        data = json.loads(original)
        data["projects"][0]["records"] = "Projects/Project-A/../../WORK"
        p.write_text(json.dumps(data))
        self.assertEqual(self.cli("context", "--project", "Project-A").returncode, 2)
        p.write_bytes(original)
        (a / "Projects").mkdir()
        self.assertEqual(self.cli("validate").returncode, 2)
        (a / "Projects").rmdir()
        (a.parent / ".SYSTEMX").mkdir()
        self.assertEqual(self.cli("validate").returncode, 2)
        (a.parent / ".SYSTEMX").rmdir()
        a.rename(a.with_name(".systemxp"))
        self.assertEqual(self.cli("context", "--project", "Project-A").returncode, 2)

    def test_linked_records_and_snapshot_outputs_are_refused(self):
        a = self.add()
        outside = Path(self.temp.name) / "outside.txt"
        outside.write_text("outside")
        record = a / "MEMORY/PROJECT.md"
        record.unlink()
        try:
            record.symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks unavailable")
        self.assertEqual(self.cli("context", "--project", "Project-A").returncode, 2)
        record.unlink()
        record.write_text("# Memory")
        (a / "SYNC/STATUS.json").symlink_to(outside)
        self.assertEqual(self.cli("refresh-status", "--project", "Project-A", "--apply").returncode, 2)
        self.assertEqual(outside.read_text(), "outside")

    def test_hardlinked_records_and_cross_scope_checkpoints_are_refused(self):
        a = self.add()
        b = self.add("Project-B")
        record = a / "MEMORY/PROJECT.md"
        record.unlink()
        try:
            os.link(b / "MEMORY/PROJECT.md", record)
        except OSError:
            self.skipTest("Hard links unavailable")
        self.assertEqual(self.cli("context", "--project", "Project-A").returncode, 2)
        record.unlink()
        record.write_text("# Memory")
        self.assertEqual(self.cli("focus", "--project", "Project-A", "--objective", "x",
                                 "--checkpoint", "../Project-B/private.md").returncode, 2)

    def test_commands_execute_only_from_selected_project_and_dry_run_is_inert(self):
        a = self.add()
        b = self.add("Project-B")
        p = a / "project.json"
        data = json.loads(p.read_text())
        data["checks"] = [{"name": "fixture", "command": [sys.executable, "-c",
            "from pathlib import Path; Path('proof.txt').write_text(str(Path.cwd()))"]}]
        p.write_text(json.dumps(data))
        self.assert_ok(self.cli("check", "--project", "Project-A", "--dry-run"))
        self.assertFalse((a.parent / "proof.txt").exists())
        self.assert_ok(self.cli("check", "--project", "Project-A"))
        self.assertEqual(Path((a.parent / "proof.txt").read_text()), a.parent.resolve())
        self.assertFalse((b.parent / "proof.txt").exists())
        self.assertFalse((self.root / "proof.txt").exists())
        self.assertEqual(self.cli("check", "--project", "Project-B").returncode, 2)

    def test_locks_and_unknown_registry_versions_do_not_overwrite(self):
        lock = self.systemx / "state/coordination.lock"
        lock.mkdir(parents=True)
        self.assertEqual(self.cli("add", "Project-A", "--apply").returncode, 2)
        self.assertFalse((self.systemx / "Projects/Project-A").exists())
        lock.rmdir()
        p = self.systemx / "Projects/REGISTRY.json"
        data = {"schemaVersion": 1, "workspace": "custom", "projects": []}
        p.write_text(json.dumps(data))
        before = p.read_bytes()
        self.assertEqual(self.cli("add", "Project-A", "--apply").returncode, 2)
        self.assertEqual(p.read_bytes(), before)

    def test_managed_library_export_update_uninstall_restore_preserve_projects(self):
        # Use the real reviewed bundle, separate from the mutable source fixture.
        target = Path(self.temp.name) / "managed"
        manager.install(target, source=test_systemx.SOURCE)
        result = manager.projects(target, ["add", "Project-A", "--apply"])
        self.assert_ok(result)
        self.assert_ok(manager.projects(target, ["add", "Project-B", "--apply"]))
        records = target / ".SYSTEMX/Projects/Project-A/.SYSTEMXP"
        (records / "MEMORY/PROJECT.md").write_text("# Memory\nA_ONLY_PRIVATE")
        sibling = target / ".SYSTEMX/Projects/Project-B/.SYSTEMXP"
        (sibling / "MEMORY/PROJECT.md").write_text("# Memory\nB_ONLY_PRIVATE")
        (records.parent / "code").mkdir()
        (records.parent / "code/user.txt").write_text("user-owned code")
        output = Path(self.temp.name) / "packet.md"
        manager.export_chat(target, output, project="Project-A")
        text = output.read_text()
        self.assertIn("A_ONLY_PRIVATE", text)
        self.assertNotIn("B_ONLY_PRIVATE", text)
        self.assertIn(".SYSTEMX/Projects/Project-A/.SYSTEMXP", text)
        before = self.files(target / ".SYSTEMX/Projects")
        manager.update(target, source=test_systemx.SOURCE)
        self.assertEqual(before, self.files(target / ".SYSTEMX/Projects"))
        # Changed defaults must also preserve initialized children and sibling code.
        source = Path(self.temp.name) / "next-release" / ".SYSTEMX"
        shutil.copytree(test_systemx.SOURCE, source)
        major, minor, patch = manager.version_key((test_systemx.SOURCE / "VERSION").read_text().strip())[:3]
        version = "{}.{}.{}-alpha.1".format(major, minor, patch + 1)
        (source / "VERSION").write_text(version + "\n")
        provenance = json.loads((source / "SOURCE.json").read_text())
        provenance["templateVersion"] = version
        (source / "SOURCE.json").write_text(json.dumps(provenance))
        (source / "templates/project/README.md").write_text("# Changed future seed\n")
        manifest = {"schemaVersion": 1, "version": version, "files": {
            p.relative_to(source).as_posix(): manager.digest(p.read_bytes())
            for p in source.rglob("*") if p.is_file() and p.relative_to(source).as_posix() != manager.MANIFEST}}
        (source / manager.MANIFEST).write_text(json.dumps(manifest))
        manager.set_policy(target, pin="none")
        manager.update(target, source=source)
        self.assertEqual(before, self.files(target / ".SYSTEMX/Projects"))
        self.assertEqual(manager.status(target)["activeVersion"], version)
        self.assert_ok(manager.projects(target, ["add", "Project-C", "--apply"]))
        self.assertEqual((target / ".SYSTEMX/Projects/Project-C/.SYSTEMXP/README.md").read_text(),
                         "# Changed future seed\n")
        before = self.files(target / ".SYSTEMX/Projects")
        backup = Path(self.temp.name) / "backup"
        manager.uninstall(target, backup=backup, apply=True)
        self.assertEqual(before, self.files(backup / ".SYSTEMX/Projects"))
        manager.restore(target, backup=backup, apply=True)
        self.assertEqual(before, self.files(target / ".SYSTEMX/Projects"))
        self.assert_ok(manager.projects(target, ["validate"]))


if __name__ == "__main__":
    unittest.main()
