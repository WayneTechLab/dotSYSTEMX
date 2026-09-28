"""First-run, logged reversible removal, restore, and scoped-cleanliness checks."""

import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import test_manager

manager = test_manager.manager


class LifecycleTests(unittest.TestCase):
    setUp = test_manager.ManagerTests.setUp
    install = test_manager.ManagerTests.install
    root_files = test_manager.ManagerTests.root_files
    next_release = test_manager.ManagerTests.next_release
    write_manifest = test_manager.ManagerTests.write_manifest

    def logs(self):
        return [json.loads(p.read_text()) for p in (self.root / ".SYSTEMX/.systemx/operations").glob("*.json")]

    def test_first_run_previews_then_initializes_without_commands_or_overwrites(self):
        result = manager.first_run(self.root, source=self.source)
        self.assertFalse(result["applied"])
        self.assertFalse(self.root.exists())
        result = manager.first_run(self.root, source=self.source, apply=True)
        self.assertEqual(result["config"], "created-empty")
        self.assertEqual(manager.status(self.root)["pinnedVersion"], self.version)
        config = self.root / ".SYSTEMX/project.json"
        config.write_text('User-owned configuration')
        manager.set_policy(self.root, pin="none", auto_update="on-start")
        with patch.object(manager, "get_url", side_effect=AssertionError("No network for an existing first-run")), \
                patch.object(manager.subprocess, "run", side_effect=AssertionError("Do not execute project commands")):
            result = manager.first_run(self.root, apply=True)
        self.assertEqual(result["config"], "preserved")
        self.assertEqual(config.read_text(), 'User-owned configuration')
        self.assertEqual(manager.status(self.root)["autoUpdate"], "on-start")
        self.assertEqual({x["action"] for x in self.logs()}, {"install", "first-run", "policy"})

    def test_failed_update_is_logged_without_changing_selected_version(self):
        self.install()
        manager.set_policy(self.root, pin="none")
        self.next_release()
        original = manager.create_missing
        def fail_snapshot(path, data):
            if path.name == ".gitignore":
                return original(path, data)
            raise OSError("Simulated disk error")
        with patch.object(manager, "create_missing", side_effect=fail_snapshot), self.assertRaises(OSError):
            manager.update(self.root, source=self.source)
        failed = [x for x in self.logs() if x["action"] == "update"]
        self.assertEqual(failed[0]["status"], "failed")
        self.assertEqual(manager.status(self.root)["activeVersion"], self.version)
        self.assertTrue(manager.audit(self.root)["issues"])

    def test_uninstall_preview_is_read_only_and_apply_needs_backup(self):
        self.install()
        before = manager.lifecycle.inventory(self.root / ".SYSTEMX")
        backup = self.folder / "removal"
        result = manager.uninstall(self.root, backup=backup)
        self.assertFalse(result["applied"])
        self.assertFalse(backup.exists())
        self.assertEqual(before, manager.lifecycle.inventory(self.root / ".SYSTEMX"))
        with self.assertRaisesRegex(manager.InstallError, "requires --backup"):
            manager.uninstall(self.root, apply=True)
        self.assertEqual(before, manager.lifecycle.inventory(self.root / ".SYSTEMX"))

    def test_uninstall_and_restore_preserve_all_user_bytes_and_host_project(self):
        self.install(lowercase_alias=True)
        folder = self.root / ".SYSTEMX"
        (folder / "MEMORY/PROJECT.md").write_text("Durable work: 项目\n", encoding="utf-8")
        (folder / "local/empty").mkdir(parents=True)
        (folder / "local/private.bin").write_bytes(b"\x00private fixture\r\n")
        (self.root / "app.txt").write_text("Host application")
        before = manager.lifecycle.inventory(folder)
        backup = self.folder / "backup with spaces"
        result = manager.uninstall(self.root, backup=backup, apply=True)
        self.assertTrue(result["audit"]["clean"])
        self.assertFalse(folder.exists())
        self.assertFalse((self.root / ".systemx").is_symlink())
        self.assertEqual((self.root / "app.txt").read_text(), "Host application")
        self.assertEqual(manager.lifecycle.inventory(backup / ".SYSTEMX"), before)
        receipt = json.loads((backup / "UNINSTALL-LOG.json").read_text())
        self.assertEqual(receipt["status"], "complete")
        self.assertEqual(receipt["inventory"], before)
        self.assertFalse(manager.restore(self.root, backup=backup)["applied"])
        self.assertFalse(folder.exists())
        restored = manager.restore(self.root, backup=backup, apply=True)
        self.assertTrue(restored["applied"])
        self.assertEqual(manager.lifecycle.inventory(folder), before)
        self.assertEqual(manager.status(self.root)["pinnedVersion"], self.version)
        self.assertEqual(json.loads((backup / "UNINSTALL-LOG.json").read_text())["restore"]["status"], "complete")
        self.assertFalse((backup / "restore.lock").exists())

    def test_backup_boundaries_existing_destinations_and_writer_locks(self):
        self.install()
        existing = self.folder / "existing"
        existing.mkdir()
        for backup in (self.root / "backup", self.folder, existing):
            with self.subTest(backup=backup), self.assertRaises(manager.InstallError):
                manager.uninstall(self.root, backup=backup, apply=True)
        lock = self.root / ".SYSTEMX/.systemx/update.lock"
        lock.write_text("Live writer")
        backup = self.folder / "backup"
        with self.assertRaisesRegex(manager.InstallError, "holds"):
            manager.uninstall(self.root, backup=backup, apply=True)
        self.assertEqual(lock.read_text(), "Live writer")
        self.assertFalse(backup.exists())
        self.assertIn("Writer lock", " ".join(manager.audit(self.root)["issues"]))

    def test_failed_move_retains_project_and_writes_incomplete_external_log(self):
        self.install()
        before = manager.lifecycle.inventory(self.root / ".SYSTEMX")
        backup = self.folder / "backup"
        with patch.object(manager.os, "rename", side_effect=OSError("Simulated move failure")), self.assertRaises(OSError):
            manager.uninstall(self.root, backup=backup, apply=True)
        self.assertEqual(manager.lifecycle.inventory(self.root / ".SYSTEMX"), before)
        self.assertEqual(json.loads((backup / "UNINSTALL-LOG.json").read_text())["status"], "incomplete")
        self.assertFalse((self.root / ".SYSTEMX/.systemx/update.lock").exists())

    def test_restore_refuses_changed_backup_or_existing_project(self):
        self.install()
        backup = self.folder / "backup"
        manager.uninstall(self.root, backup=backup, apply=True)
        memory = backup / ".SYSTEMX/MEMORY/PROJECT.md"
        before = memory.read_bytes()
        memory.write_text("Changed after archival")
        with self.assertRaisesRegex(manager.InstallError, "inventory differs"):
            manager.restore(self.root, backup=backup, apply=True)
        memory.write_bytes(before)
        self.install()
        current = manager.lifecycle.inventory(self.root / ".SYSTEMX")
        with self.assertRaisesRegex(manager.InstallError, "will not overwrite"):
            manager.restore(self.root, backup=backup, apply=True)
        self.assertEqual(manager.lifecycle.inventory(self.root / ".SYSTEMX"), current)

    def test_changes_during_archival_are_retained_but_not_reported_as_verified(self):
        self.install()
        backup = self.folder / "backup"
        rename = manager.os.rename
        def concurrent_change(source, destination):
            rename(source, destination)
            (Path(destination) / "MEMORY/PROJECT.md").write_text("Late writer change")
        with patch.object(manager.os, "rename", side_effect=concurrent_change), self.assertRaisesRegex(manager.InstallError, "changed during removal"):
            manager.uninstall(self.root, backup=backup, apply=True)
        self.assertEqual((backup / ".SYSTEMX/MEMORY/PROJECT.md").read_text(), "Late writer change")
        self.assertEqual(json.loads((backup / "UNINSTALL-LOG.json").read_text())["status"], "incomplete")
        self.assertFalse((backup / ".SYSTEMX/.systemx/update.lock").exists())
        with self.assertRaisesRegex(manager.InstallError, "inventory differs"):
            manager.restore(self.root, backup=backup, apply=True)

    def test_restore_respects_an_existing_backup_lock(self):
        self.install()
        backup = self.folder / "backup"
        manager.uninstall(self.root, backup=backup, apply=True)
        (backup / "restore.lock").write_text("Other operation")
        with self.assertRaises(FileExistsError):
            manager.restore(self.root, backup=backup, apply=True)
        self.assertEqual((backup / "restore.lock").read_text(), "Other operation")
        self.assertTrue((backup / ".SYSTEMX").is_dir())
        self.assertFalse((self.root / ".SYSTEMX").exists())

    def test_archive_does_not_follow_content_symlinks(self):
        self.install()
        outside = self.folder / "outside.txt"
        outside.write_text("Outside fixture")
        local = self.root / ".SYSTEMX/local"
        local.mkdir()
        (local / "pointer").symlink_to(outside)
        backup = self.folder / "backup"
        manager.uninstall(self.root, backup=backup, apply=True)
        outside.write_text("External change must not change the link inventory")
        manager.restore(self.root, backup=backup, apply=True)
        self.assertTrue((local / "pointer").is_symlink())
        self.assertEqual(outside.read_text(), "External change must not change the link inventory")

    def test_unmanaged_folder_can_be_archived_and_audit_scope_is_explicit(self):
        folder = self.root / ".SYSTEMX"
        folder.mkdir(parents=True)
        (folder / "notes.md").write_text("Unmanaged user work")
        audit = manager.audit(self.root)
        self.assertFalse(audit["clean"])
        self.assertNotIn("installation", audit)
        backup = self.folder / "backup"
        manager.uninstall(self.root, backup=backup, apply=True)
        self.assertTrue(manager.audit(self.root)["clean"])
        self.assertIn("Project .SYSTEMX", manager.audit(self.root)["scope"])
        self.assertEqual((backup / ".SYSTEMX/notes.md").read_text(), "Unmanaged user work")
        self.assertEqual(manager.uninstall(self.root)["status"], "not-installed")

    def test_audit_reports_case_conflicts_without_modifying_them(self):
        lower = self.root / ".systemx"
        lower.mkdir(parents=True)
        (lower / "notes.txt").write_text("Keep")
        result = manager.audit(self.root)
        self.assertFalse(result["clean"])
        self.assertIn("Exact-case conflict", " ".join(result["issues"]))
        self.assertEqual((lower / "notes.txt").read_text(), "Keep")

    def test_removal_refuses_the_target_own_manager_and_guide_menu_is_read_only(self):
        self.install()
        folder = self.root / ".SYSTEMX"
        before = manager.lifecycle.inventory(folder)
        result = subprocess.run([sys.executable, "-B", str(folder / "manager.py"), "uninstall", "--target", str(self.root)],
                                text=True, capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 2)
        self.assertIn("outside the target", result.stderr)
        result = subprocess.run([sys.executable, "-B", str(folder / "scripts/systemx.py"), "menu"],
                                input="13\n14\n0\n", text=True, capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("First-Time Setup", result.stdout)
        self.assertIn("Uninstall, Restore, and Cleanup", result.stdout)
        self.assertEqual(before, manager.lifecycle.inventory(folder))


if __name__ == "__main__":
    unittest.main()
