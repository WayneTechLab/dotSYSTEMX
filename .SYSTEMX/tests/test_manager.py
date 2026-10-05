"""Install/update preservation and boundary tests; no live network or user project writes."""

from contextlib import redirect_stderr
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

SOURCE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("systemx_manager_test", SOURCE / "manager.py")
manager = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(manager)


class ManagerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="systemx-manager-")
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.root = self.folder / "project with spaces"
        self.source = self.folder / "release"
        shutil.copytree(SOURCE, self.source, ignore=shutil.ignore_patterns("__pycache__", ".systemx", "local", "logs", "state"))
        self.version = (self.source / "VERSION").read_text().strip()
        major, minor, patch = manager.version_key(self.version)[:3]
        self.next_version = f"{major}.{minor}.{patch + 1}"

    def write_manifest(self, version=None):
        if version:
            (self.source / "VERSION").write_text(version + "\n")
            provenance = json.loads((self.source / "SOURCE.json").read_text())
            provenance["templateVersion"] = version
            (self.source / "SOURCE.json").write_text(json.dumps(provenance))
        files = {p.relative_to(self.source).as_posix(): manager.digest(p.read_bytes()) for p in self.source.rglob("*")
                 if p.is_file() and p.relative_to(self.source).as_posix() != manager.MANIFEST}
        (self.source / manager.MANIFEST).write_text(json.dumps({"schemaVersion": 1,
            "version": (self.source / "VERSION").read_text().strip(), "files": files}))

    def install(self, **kwargs):
        return manager.install(self.root, source=self.source, **kwargs)

    def root_files(self):
        root = self.root / ".SYSTEMX"
        return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*")
                if p.is_file() and ".systemx" not in p.relative_to(root).parts and p.name != manager.STATE}

    def next_release(self, version=None):
        version = version or self.next_version
        (self.source / "STANDARD.md").write_text("# Updated default\n")
        (self.source / "docs/new-guide.md").write_text("# New default\n")
        (self.source / "templates/RELEASE.md").unlink()
        self.write_manifest(version)

    def test_install_dry_run_is_read_only_then_installs_pinned_defaults(self):
        preview = self.install(dry_run=True)
        self.assertFalse(self.root.exists())
        self.assertFalse(preview["applied"])
        result = self.install()
        self.assertTrue(result["applied"])
        state = manager.status(self.root)
        self.assertEqual(state["pinnedVersion"], self.version)
        self.assertEqual(state["autoUpdate"], "manual")
        with self.assertRaisesRegex(manager.InstallError, "Already managed"):
            self.install()

    def test_adoption_preserves_all_existing_files_and_adds_missing_only(self):
        local = self.root / ".SYSTEMX"
        (local / "local/custom").mkdir(parents=True)
        (local / "local/custom/secret.txt").write_text("Fixture value, never uploaded")
        (local / "STANDARD.md").write_text("User guidance\n")
        (local / "project.json").write_text('{"userOwned": true}')
        before = self.root_files()
        self.install()
        after = self.root_files()
        for name, content in before.items():
            self.assertEqual(after[name], content)
        self.assertTrue((local / "START-HERE.md").exists())

    def test_update_preserves_changed_defaults_records_and_removed_upstream_paths(self):
        self.install(lowercase_alias=True)
        local = self.root / ".SYSTEMX"
        (local / "MEMORY/PROJECT.md").write_text("Project-owned learned fact\n")
        (local / "STANDARD.md").write_text("Locally customized standard\n")
        (local / "my-folder").mkdir()
        before = self.root_files()
        old_release = manager.release_path(self.root, self.version)
        old_bytes = {p.relative_to(old_release): p.read_bytes() for p in old_release.rglob("*") if p.is_file()}
        self.next_release()
        with self.assertRaisesRegex(manager.InstallError, "pinned"):
            manager.update(self.root, source=self.source)
        manager.set_policy(self.root, pin="none")
        preview = manager.update(self.root, source=self.source, dry_run=True)
        self.assertIn("docs/new-guide.md", preview["add"])
        self.assertFalse(manager.release_path(self.root, self.next_version).exists())
        manager.update(self.root, source=self.source)
        for name, content in before.items():
            self.assertEqual((local / name).read_bytes(), content, name)
        self.assertTrue((local / "my-folder").is_dir())
        self.assertTrue((self.root / ".systemx").samefile(local))
        self.assertEqual((local / "docs/new-guide.md").read_text(), "# New default\n")
        self.assertEqual((manager.release_path(self.root, self.next_version) / "STANDARD.md").read_text(), "# Updated default\n")
        for name, content in old_bytes.items():
            self.assertEqual((old_release / name).read_bytes(), content)
        manager.set_policy(self.root, pin="current")
        self.assertEqual(manager.status(self.root)["pinnedVersion"], self.next_version)

    def test_same_release_cannot_be_replaced_and_integrity_is_checked_before_execution(self):
        self.install()
        (self.source / "STANDARD.md").write_text("Different content under the same version\n")
        self.write_manifest()
        with self.assertRaisesRegex(manager.InstallError, "Existing release differs"):
            manager.update(self.root, source=self.source)
        cached = manager.release_path(self.root, self.version) / "scripts/systemx.py"
        cached.write_text("raise RuntimeError('must never execute')")
        with self.assertRaisesRegex(manager.InstallError, "fingerprint mismatch"):
            manager.run(self.root, ["status"])

    def test_release_cache_rejects_unlisted_import_content_without_deleting_it(self):
        version = (self.source / "VERSION").read_text().strip()
        cases = ("scripts/hashlib.py", "scripts/hashlib/__init__.py", "scripts/tool.pyc",
                 "scripts/__pycache__/tool.cpython-39.pyc", ".SYSTEMX/redirect.txt", "unexpected/empty.txt")
        for index, relative in enumerate(cases):
            with self.subTest(relative=relative):
                root = self.folder / ("adopted-" + str(index))
                planted = root / ".SYSTEMX/.systemx/releases" / version / relative
                planted.parent.mkdir(parents=True)
                planted.write_bytes(b"preserve untrusted fixture")
                before = planted.read_bytes()
                preview = manager.install(root, source=self.source, dry_run=True)
                self.assertFalse(preview["applied"])
                self.assertTrue(any("unexpected" in conflict for conflict in preview["conflicts"]), preview)
                with self.assertRaisesRegex(manager.InstallError, "unexpected"):
                    manager.install(root, source=self.source)
                self.assertEqual(planted.read_bytes(), before)
                self.assertFalse((root / ".SYSTEMX/INSTALLATION.json").exists())

    def test_active_release_rejects_added_module_before_subprocess(self):
        self.install()
        snapshot = manager.release_path(self.root, self.version)
        planted = snapshot / "scripts/hashlib.py"
        planted.write_text("raise RuntimeError('must not import')")
        with patch.object(manager.subprocess, "run", side_effect=AssertionError("must not execute")):
            with self.assertRaisesRegex(manager.InstallError, "unexpected file"):
                manager.run(self.root, ["status"], offline=True, capture=True)
        self.assertEqual(planted.read_text(), "raise RuntimeError('must not import')")

    def test_adopted_root_module_cannot_shadow_manager_standard_library_imports(self):
        local = self.root / ".SYSTEMX"
        local.mkdir(parents=True)
        marker = self.folder / "ROOT-MODULE-EXECUTED"
        planted = local / "hashlib.py"
        planted.write_text("from pathlib import Path\nPath(" + repr(str(marker)) + ").write_text('executed')\n")
        self.install()
        result = subprocess.run(["bash", str(local / "SYSTEMX.sh"), "status"],
                                cwd=self.folder, env={**os.environ, "PYTHONPATH": str(local)},
                                text=True, capture_output=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run([sys.executable, "-I", "-B", str(local / "manager.py"), "status", "--target", str(self.root)],
                                cwd=self.folder, env={**os.environ, "PYTHONPATH": str(local)},
                                text=True, capture_output=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(marker.exists())
        self.assertTrue(planted.is_file())

    def test_initial_adoption_refuses_different_executable_defaults_without_overwriting(self):
        local = self.root / ".SYSTEMX"
        local.mkdir(parents=True)
        planted = local / "lifecycle.py"
        planted.write_text("raise RuntimeError('preplanted code')\n")
        preview = self.install(dry_run=True)
        self.assertTrue(any("Existing executable default differs" in item for item in preview["conflicts"]))
        with self.assertRaisesRegex(manager.InstallError, "Existing executable default differs"):
            self.install()
        self.assertEqual(planted.read_text(), "raise RuntimeError('preplanted code')\n")
        self.assertFalse((local / "INSTALLATION.json").exists())

    def test_release_cache_rejects_links_and_unexpected_empty_directories(self):
        version = (self.source / "VERSION").read_text().strip()
        for kind in ("link", "directory"):
            with self.subTest(kind=kind):
                root = self.folder / ("snapshot-" + kind)
                snapshot = root / ".SYSTEMX/.systemx/releases" / version
                snapshot.mkdir(parents=True)
                entry = snapshot / "unexpected"
                if kind == "link":
                    entry.symlink_to(self.source, target_is_directory=True)
                    message = "link or junction"
                else:
                    entry.mkdir()
                    message = "unexpected directory"
                with self.assertRaisesRegex(manager.InstallError, message):
                    manager.install(root, source=self.source)
                self.assertTrue(entry.is_symlink() if kind == "link" else entry.is_dir())

    def test_permissive_source_read_ignores_generated_unlisted_cache(self):
        generated = self.source / "scripts/__pycache__/generated.pyc"
        generated.parent.mkdir()
        generated.write_bytes(b"local generated file")
        bundle = manager.read_bundle(self.source)
        self.assertNotIn("scripts/__pycache__/generated.pyc", bundle["files"])

    def test_managed_runner_reads_and_changes_project_records_not_blank_snapshot(self):
        self.install()
        (self.root / ".SYSTEMX/templates/AGENT-MEMORY.md").write_text("Old customized default; preserve this file")
        result = manager.run(self.root, ["agent-add", "agent.1", "--role", "test"], capture=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("Old customized", (self.root / ".SYSTEMX/AGENTS/agent.1/MEMORY.md").read_text())
        self.assertEqual((self.root / ".SYSTEMX/templates/AGENT-MEMORY.md").read_text(), "Old customized default; preserve this file")
        result = manager.run(self.root, ["task-add", "--title", "Real project task", "--acceptance", "Verified result"], capture=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        actual = json.loads((self.root / ".SYSTEMX/WORK/TASKS.json").read_text())
        cached = json.loads((manager.release_path(self.root, self.version) / "WORK/TASKS.json").read_text())
        self.assertEqual(actual["tasks"][0]["title"], "Real project task")
        self.assertEqual(cached["tasks"], [])
        result = manager.run(self.root, ["context"], capture=True)
        self.assertIn("Selected defaults:", result.stdout)
        self.assertIn("Real project task", result.stdout)
        result = manager.run(self.root, ["validate"], capture=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_manual_and_pinned_startup_never_contact_network(self):
        self.install()
        with patch.object(manager, "get_url", side_effect=AssertionError("No network expected")):
            manager.startup_update(self.root)
            manager.set_policy(self.root, pin="none")
            manager.startup_update(self.root)
            manager.set_policy(self.root, auto_update="on-start")
            result = manager.run(self.root, ["status"], offline=True, capture=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        manager.set_policy(self.root, pin="current")
        with self.assertRaisesRegex(manager.InstallError, "Unpin"):
            manager.set_policy(self.root, auto_update="on-start")

    def test_opt_in_startup_appends_new_release_and_checks_at_most_daily(self):
        self.install()
        manager.set_policy(self.root, pin="none", auto_update="on-start")
        self.next_release()
        bundle = manager.read_bundle(self.source)
        before = self.root_files()
        with patch.object(manager, "latest_version", return_value=self.next_version) as latest, \
             patch.object(manager, "remote_bundle", return_value=bundle), redirect_stderr(io.StringIO()):
            manager.startup_update(self.root)
            manager.startup_update(self.root)
            self.assertEqual(latest.call_count, 1)
        self.assertEqual(manager.status(self.root)["activeVersion"], self.next_version)
        for name, data in before.items():
            self.assertEqual((self.root / ".SYSTEMX" / name).read_bytes(), data)

    def test_unavailable_update_and_new_major_do_not_stop_existing_project(self):
        self.install()
        manager.set_policy(self.root, pin="none", auto_update="on-start")
        with patch.object(manager, "latest_version", side_effect=OSError("offline")), redirect_stderr(io.StringIO()):
            result = manager.run(self.root, ["status"], capture=True)
            self.assertEqual(result.returncode, 0)
        with patch.object(manager, "latest_version", return_value="2.0.0"), \
             patch.object(manager, "remote_bundle", side_effect=AssertionError("Major update must be manual")), \
             redirect_stderr(io.StringIO()):
            manager.startup_update(self.root)
        self.assertEqual(manager.status(self.root)["activeVersion"], self.version)

    def test_alpha_update_preserves_records_and_graduates_to_stable(self):
        self.write_manifest("1.8.7-alpha.2")
        self.install()
        manager.set_policy(self.root, pin="none", auto_update="on-start")
        before = self.root_files()
        self.next_release("1.8.7-alpha.10")
        bundle = manager.read_bundle(self.source)
        with patch.object(manager, "latest_version", return_value=bundle["version"]) as latest, \
             patch.object(manager, "remote_bundle", return_value=bundle), redirect_stderr(io.StringIO()):
            manager.startup_update(self.root)
            latest.assert_called_once_with(manager.DEFAULT_REPOSITORY, channel="alpha")
        self.assertEqual(manager.status(self.root)["releaseChannel"], "alpha")
        self.write_manifest("1.8.7")
        manager.update(self.root, source=self.source)
        self.assertEqual(manager.status(self.root)["releaseChannel"], "stable")
        self.assertEqual(manager.status(self.root)["retainedVersions"], ["1.8.7-alpha.2", "1.8.7-alpha.10", "1.8.7"])
        for name, data in before.items():
            self.assertEqual((self.root / ".SYSTEMX" / name).read_bytes(), data)

    def test_implicit_downgrade_rejected_but_compatible_explicit_rollback_allowed(self):
        self.write_manifest("1.8.7-alpha.10")
        self.install()
        manager.set_policy(self.root, pin="none")
        self.next_release("1.8.7-alpha.2")
        bundle = manager.read_bundle(self.source)
        with patch.object(manager, "latest_version", return_value=bundle["version"]), \
             patch.object(manager, "remote_bundle", return_value=bundle):
            with self.assertRaisesRegex(manager.InstallError, "downgrade"):
                manager.update(self.root)
            manager.update(self.root, version="1.8.7-alpha.2")
        self.assertEqual(manager.status(self.root)["activeVersion"], "1.8.7-alpha.2")

    def test_stable_project_discovers_only_stable_channel(self):
        self.write_manifest("1.8.7")
        self.install()
        manager.set_policy(self.root, pin="none", auto_update="on-start")
        with patch.object(manager, "latest_version", return_value="1.8.7") as latest:
            manager.startup_update(self.root)
            latest.assert_called_once_with(manager.DEFAULT_REPOSITORY, channel="stable")

    def test_pre_isolation_release_is_refused_for_new_managed_install(self):
        self.write_manifest("1.8.6-alpha.1")
        with self.assertRaisesRegex(manager.InstallError, "predates isolated runner"):
            self.install(dry_run=True)
        self.assertFalse((self.root / ".SYSTEMX/INSTALLATION.json").exists())

    def test_retained_legacy_runner_remains_usable_through_isolated_compatibility_shim(self):
        runner = self.source / "scripts/systemx.py"
        text = runner.read_text().replace(
            'SCRIPTS = Path(__file__).resolve().parent\nsys.path.insert(0, str(SCRIPTS))\n', '')
        runner.write_text(text)
        self.write_manifest("1.8.6-alpha.1")
        old = manager.read_bundle(self.source)
        manager.apply_bundle(self.root, old, None, "project", manager.DEFAULT_REPOSITORY)
        marker = self.folder / "OLD-RUNNER-MODULE-EXECUTED"
        planted = self.root / ".SYSTEMX/hashlib.py"
        planted.write_text("from pathlib import Path\nPath(" + repr(str(marker)) + ").write_text('executed')\n")
        with patch.dict(os.environ, {"PYTHONPATH": str(planted.parent)}):
            result = manager.run(self.root, ["status"], offline=True, capture=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(marker.exists())

    def test_bootstrap_refresh_adds_helper_absent_from_all_retained_legacy_releases(self):
        helper = self.source / "versions.py"
        current_bytes = helper.read_bytes()
        helper.unlink()
        self.write_manifest("1.5.0")
        old = manager.read_bundle(self.source)
        manager.apply_bundle(self.root, old, None, "project", manager.DEFAULT_REPOSITORY)
        self.assertFalse((self.root / ".SYSTEMX/versions.py").exists())
        helper.write_bytes(current_bytes)
        self.write_manifest(self.version)
        preview = manager.bootstrap_refresh(self.root, source=self.source)
        self.assertIn("versions.py", preview["add"])
        self.assertFalse(preview["conflicts"])
        applied = manager.bootstrap_refresh(self.root, source=self.source, apply=True)
        self.assertTrue(applied["applied"])
        self.assertEqual((self.root / ".SYSTEMX/versions.py").read_bytes(), current_bytes)

    def test_cli_reports_tool_version_without_a_project(self):
        result = subprocess.run([sys.executable, "-B", str(self.source / "manager.py"), "--version"],
                                capture_output=True, text=True, cwd=self.folder)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(".SYSTEMX " + self.version, result.stdout)
        self.assertIn(manager.package_version(self.version), result.stdout)

    def test_symlinks_conflicts_and_locks_preserve_user_content(self):
        self.root.mkdir()
        outside = self.folder / "outside"
        outside.mkdir()
        (self.root / ".SYSTEMX").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(manager.InstallError, "symlink"):
            self.install()
        (self.root / ".SYSTEMX").unlink()
        self.install()
        lock = self.root / ".SYSTEMX/.systemx/update.lock"
        lock.write_text("another owner")
        before = manager.load_state(self.root)
        with self.assertRaisesRegex(manager.InstallError, "holds"):
            manager.set_policy(self.root, pin="none")
        self.assertEqual(lock.read_text(), "another owner")
        self.assertEqual(manager.load_state(self.root), before)

    def test_bad_manifest_or_populated_seed_cannot_be_installed(self):
        (self.source / "STANDARD.md").write_text("Unrecorded change")
        with self.assertRaisesRegex(manager.InstallError, "fingerprint mismatch"):
            self.install()
        self.write_manifest()
        (self.source / "WORK/TASKS.json").write_text('{"schemaVersion":1,"tasks":[{"private":"data"}]}')
        seeds_path = self.source / "config/template-records.json"
        seeds = json.loads(seeds_path.read_text())
        seeds["sha256"]["WORK/TASKS.json"] = manager.digest((self.source / "WORK/TASKS.json").read_bytes())
        seeds_path.write_text(json.dumps(seeds))
        self.write_manifest()
        with self.assertRaisesRegex(manager.InstallError, "must be empty"):
            self.install()
        self.assertFalse(self.root.exists())

    def test_archive_manifest_and_path_checks_reject_untrusted_layouts(self):
        for path in ("../outside", "a/../../escape", "/absolute", "C:/escape", "a\\b", "con.txt", "NUL", "a./b", "local/data"):
            with self.subTest(path=path), self.assertRaises(manager.InstallError):
                manager.portable_path(path)
        bundle = manager.read_bundle(self.source)
        archive = io.BytesIO()
        with zipfile.ZipFile(archive, "w") as output:
            for name, data in bundle["files"].items():
                output.writestr("repo-tag/.SYSTEMX/" + name, data)
            output.writestr("repo-tag/application.txt", "Must not install the application")
        raw_archive = archive.getvalue()
        expected = hashlib.sha256(raw_archive).hexdigest()
        with patch.object(manager, "get_url", return_value=raw_archive):
            fetched = manager.remote_bundle(self.version, expected_archive_sha256=expected)
        self.assertEqual(fetched["manifestSha256"], bundle["manifestSha256"])
        self.assertEqual(fetched["archiveDigest"], {"sha256": expected, "verifiedBy": "explicit-pin"})
        self.assertNotIn("application.txt", fetched["files"])
        with patch.object(manager, "get_url", return_value=b"not a zip archive"):
            with self.assertRaisesRegex(manager.InstallError, "does not match the explicit pin"):
                manager.remote_bundle(self.version, expected_archive_sha256="0" * 64)

    def test_archive_pin_requires_exact_remote_version_and_is_recorded(self):
        for kwargs in ({"source": self.source, "archive_sha256": "0" * 64},
                       {"archive_sha256": "0" * 64}, {"version": self.version, "archive_sha256": "BAD"}):
            with self.subTest(kwargs=kwargs), self.assertRaises(manager.InstallError):
                manager.install(self.root, **kwargs)
        self.install()
        state_path = self.root / ".SYSTEMX/INSTALLATION.json"
        state = json.loads(state_path.read_text())
        self.assertEqual(state["schemaVersion"], 2)
        self.assertIsNone(state["archiveDigests"][self.version])

    def test_explicit_archive_receipt_survives_same_release_source_retry(self):
        bundle = manager.read_bundle(self.source)
        receipt = {"sha256": "a" * 64, "verifiedBy": "explicit-pin"}
        bundle["archiveDigest"] = receipt
        with patch.object(manager, "remote_bundle", return_value=bundle):
            manager.install(self.root, version=self.version, archive_sha256=receipt["sha256"])
        self.assertEqual(manager.status(self.root)["archiveDigest"], receipt)
        manager.update(self.root, source=self.source)
        self.assertEqual(manager.status(self.root)["archiveDigest"], receipt)

    def test_legacy_bootstrap_requires_explicit_backed_up_refresh_before_update(self):
        old_bytes = (self.source / "manager.py").read_bytes() + b"\n# Previous reviewed bootstrap\n"
        (self.source / "manager.py").write_bytes(old_bytes)
        old_launcher = (self.source / "SYSTEMX.sh").read_bytes().replace(
            b'"$SYSTEMX_PYTHON" -I -B "$SYSTEMX_DIR/manager.py"',
            b'"$SYSTEMX_PYTHON" -B "$SYSTEMX_DIR/manager.py"')
        (self.source / "SYSTEMX.sh").write_bytes(old_launcher)
        self.write_manifest()
        self.install()
        root_manager = self.root / ".SYSTEMX/manager.py"
        root_launcher = self.root / ".SYSTEMX/SYSTEMX.sh"
        self.assertEqual(root_manager.read_bytes(), old_bytes)
        self.assertEqual(root_launcher.read_bytes(), old_launcher)
        state_path = self.root / ".SYSTEMX/INSTALLATION.json"
        legacy = json.loads(state_path.read_text())
        legacy["schemaVersion"] = 1
        legacy.pop("archiveDigests")
        state_path.write_text(json.dumps(legacy))
        (self.source / "manager.py").write_bytes((SOURCE / "manager.py").read_bytes())
        (self.source / "SYSTEMX.sh").write_bytes((SOURCE / "SYSTEMX.sh").read_bytes())
        self.write_manifest(self.next_version)
        manager.set_policy(self.root, pin="none")
        with self.assertRaisesRegex(manager.InstallError, "bootstrap-refresh"):
            manager.update(self.root, source=self.source)
        self.assertEqual(root_manager.read_bytes(), old_bytes)
        preview = manager.bootstrap_refresh(self.root, source=self.source)
        self.assertEqual(preview["replace"], ["manager.py", "SYSTEMX.sh"])
        self.assertFalse(preview["applied"])
        self.assertEqual(root_manager.read_bytes(), old_bytes)
        refreshed = manager.bootstrap_refresh(self.root, source=self.source, apply=True)
        self.assertTrue(refreshed["applied"])
        self.assertEqual((Path(refreshed["backup"]) / "manager.py").read_bytes(), old_bytes)
        self.assertEqual((Path(refreshed["backup"]) / "SYSTEMX.sh").read_bytes(), old_launcher)
        self.assertEqual(root_launcher.read_bytes(), (SOURCE / "SYSTEMX.sh").read_bytes())
        manager.update(self.root, source=self.source)
        result = subprocess.run(["bash", str(self.root / ".SYSTEMX/SYSTEMX.sh"), "status"],
                                cwd=self.folder, text=True, capture_output=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(manager.status(self.root)["activeVersion"], self.next_version)

    def test_schema_one_installation_state_migrates_without_losing_release_history(self):
        self.install()
        path = self.root / ".SYSTEMX/INSTALLATION.json"
        state = json.loads(path.read_text())
        state["schemaVersion"] = 1
        state.pop("archiveDigests")
        path.write_text(json.dumps(state))
        loaded = manager.load_state(self.root)
        self.assertEqual(loaded["schemaVersion"], 2)
        self.assertEqual(loaded["archiveDigests"], {self.version: None})
        manager.set_policy(self.root, pin="none")
        persisted = json.loads(path.read_text())
        self.assertEqual(persisted["schemaVersion"], 2)
        self.assertEqual(persisted["archiveDigests"], {self.version: None})

    def test_chat_export_is_local_bounded_and_never_overwrites(self):
        self.install(profile="chat")
        (self.root / ".SYSTEMX/MEMORY/PROJECT.md").write_text("# Project memory\nUnicode fact: 项目\n", encoding="utf-8")
        output = self.folder / "packet.md"
        with patch.object(manager, "get_url", side_effect=AssertionError("No network expected")):
            result = manager.export_chat(self.root, output)
        self.assertFalse(result["uploaded"])
        self.assertIn("SYSTEMX chat packet", output.read_text())
        self.assertIn("PROJECT RESUME PACKET", output.read_text())
        self.assertIn("项目", output.read_text(encoding="utf-8"))
        before = output.read_bytes()
        with self.assertRaisesRegex(manager.InstallError, "already exists"):
            manager.export_chat(self.root, output)
        self.assertEqual(output.read_bytes(), before)

    def test_all_profiles_share_identical_template_records(self):
        for profile in manager.PROFILES:
            root = self.folder / profile
            manager.install(root, source=self.source, profile=profile)
            self.assertEqual(manager.status(root)["profile"], profile)
            self.assertEqual((root / ".SYSTEMX/WORK/TASKS.json").read_bytes(), (self.source / "WORK/TASKS.json").read_bytes())
        with self.assertRaisesRegex(manager.InstallError, "local folder"):
            manager.install("https://drive.google.com/drive/folders/example", source=self.source)

    def test_parent_file_conflict_is_rejected_before_install_and_unknown_policy_has_no_side_effect(self):
        with self.assertRaises(OSError):
            manager.set_policy(self.root, pin="none")
        self.assertFalse(self.root.exists())
        folder = self.root / ".SYSTEMX"
        folder.mkdir(parents=True)
        (folder / "docs").write_text("User file")
        with self.assertRaisesRegex(manager.InstallError, "parent directory"):
            self.install(dry_run=True)
        self.assertEqual((folder / "docs").read_text(), "User file")
        self.assertFalse((folder / ".systemx").exists())

    def test_partial_snapshot_is_not_selected_when_writing_fails(self):
        self.install()
        manager.set_policy(self.root, pin="none")
        self.next_release()
        old_state = manager.load_state(self.root)
        original = manager.create_missing
        def failing_create(path, data):
            if self.next_version in path.parts and path.name == "STANDARD.md":
                raise OSError("Simulated interrupted write")
            return original(path, data)
        with patch.object(manager, "create_missing", side_effect=failing_create), self.assertRaises(OSError):
            manager.update(self.root, source=self.source)
        self.assertEqual(manager.load_state(self.root), old_state)
        self.assertEqual(manager.status(self.root)["activeVersion"], self.version)
        manager.update(self.root, source=self.source)
        self.assertEqual(manager.status(self.root)["activeVersion"], self.next_version)


if __name__ == "__main__":
    unittest.main()
