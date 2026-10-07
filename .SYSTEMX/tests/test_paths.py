"""Real filesystem case, alias, CLI, and preservation checks in isolated projects."""

import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
from unittest.mock import patch

import test_manager

manager = test_manager.manager


class PathTests(unittest.TestCase):
    setUp = test_manager.ManagerTests.setUp
    install = test_manager.ManagerTests.install
    root_files = test_manager.ManagerTests.root_files

    def sensitive_project(self):
        canonical = self.root / ".SYSTEMX"
        canonical.mkdir(parents=True, exist_ok=True)
        if (self.root / ".systemx").exists():
            self.skipTest("Distinct case spellings require a case-sensitive filesystem")
        return canonical

    def test_alias_install_dry_run_then_idempotent_and_same_records(self):
        preview = self.install(lowercase_alias=True, dry_run=True)
        self.assertFalse(self.root.exists())
        self.assertTrue(preview["pathLayout"]["requested"])
        result = self.install(lowercase_alias=True)
        self.assertIn(result["pathLayout"]["aliasStatus"], {"linked", "filesystem-equivalent"})
        canonical, alias = self.root / ".SYSTEMX", self.root / ".systemx"
        self.assertTrue(alias.samefile(canonical))
        if result["pathLayout"]["aliasStatus"] == "linked":
            self.assertEqual(os.readlink(alias), ".SYSTEMX")
        before = self.root_files()
        self.assertFalse(manager.alias(self.root, create=True)["created"])
        self.assertEqual(before, self.root_files())
        (alias / "MEMORY/PROJECT.md").write_text("A single durable project record")
        self.assertEqual((canonical / "MEMORY/PROJECT.md").read_text(), "A single durable project record")
        moved = self.root.with_name("moved project")
        self.root.rename(moved)
        self.assertTrue((moved / ".systemx").samefile(moved / ".SYSTEMX"))
        result = manager.run(moved, ["status"], offline=True, capture=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_install_without_option_has_no_distinct_sibling_alias(self):
        self.install()
        self.assertEqual({p.name for p in self.root.iterdir()}, {".SYSTEMX"})
        self.assertFalse(manager.alias(self.root)["created"])
        self.assertEqual({p.name for p in self.root.iterdir()}, {".SYSTEMX"})

    def test_wrong_stored_case_is_refused_before_install_on_every_filesystem(self):
        for name in (".systemx", ".SystemX", ".sYsTeMx"):
            with self.subTest(name=name):
                wrong = self.root / name
                wrong.mkdir(parents=True)
                (wrong / "memory.txt").write_text("Keep this")
                with self.assertRaisesRegex(manager.InstallError, "Exact-case conflict"):
                    self.install(lowercase_alias=True)
                self.assertEqual({p.name for p in self.root.iterdir()}, {name})
                self.assertEqual((wrong / "memory.txt").read_text(), "Keep this")
                shutil.rmtree(self.root)

    def test_containing_target_cannot_be_systemx_or_nested_inside_it(self):
        for relative in (".SYSTEMX", ".systemx", ".SystemX", ".SYSTEMX/WORK", ".systemx/new"):
            with self.subTest(relative=relative), self.assertRaisesRegex(manager.InstallError, "containing project"):
                manager.install(self.root / relative, source=self.source)
        self.assertFalse(self.root.exists())

    def test_explicit_blank_paths_are_refused_before_target_install(self):
        for value in ("", " ", " \t\n ", Path(" ")):
            with self.subTest(value=repr(value)):
                with self.assertRaisesRegex(manager.InstallError, "cannot be empty or whitespace"):
                    manager.lexical_path(value)
                with self.assertRaisesRegex(manager.InstallError, "cannot be empty or whitespace"):
                    manager.project_directory(value)
                with self.assertRaisesRegex(manager.InstallError, "cannot be empty or whitespace"):
                    manager.inspect_layout(value)
                with self.assertRaisesRegex(manager.InstallError, "cannot be empty or whitespace"):
                    manager.record_directory(value)
                with self.assertRaisesRegex(manager.InstallError, "cannot be empty or whitespace"):
                    manager.read_bundle(value)
                result = subprocess.run(
                    [sys.executable, "-I", "-B", str(test_manager.SOURCE / "manager.py"),
                     "install", "--target", value, "--source", str(self.source)],
                    cwd=self.folder, text=True, capture_output=True, timeout=20)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn("cannot be empty or whitespace", result.stderr)
                self.assertEqual({path.name for path in self.folder.iterdir()}, {"release"})

    def test_space_containing_target_path_remains_valid(self):
        self.assertEqual(manager.project_directory(self.root), self.root.resolve())
        self.assertEqual(manager.project_directory(str(self.root)), self.root.resolve())

    def test_independent_sibling_blocks_all_manager_actions_and_preserves_files(self):
        self.sensitive_project()
        self.install()
        wrong = self.root / ".systemx"
        wrong.mkdir()
        (wrong / "notes.txt").write_text("Independent data")
        before = self.root_files()
        state = (self.root / ".SYSTEMX/INSTALLATION.json").read_bytes()
        for action in (lambda: manager.alias(self.root, create=True),
                       lambda: manager.update(self.root, source=self.source),
                       lambda: manager.set_policy(self.root, pin="none"),
                       lambda: manager.status(self.root),
                       lambda: manager.run(self.root, ["init"], capture=True),
                       lambda: manager.export_chat(self.root, self.folder / "packet.md")):
            with self.assertRaisesRegex(manager.InstallError, "Exact-case conflict"):
                action()
        self.assertEqual(self.root_files(), before)
        self.assertEqual((self.root / ".SYSTEMX/INSTALLATION.json").read_bytes(), state)
        self.assertEqual((wrong / "notes.txt").read_text(), "Independent data")
        self.assertFalse((self.folder / "packet.md").exists())

    def test_unsupported_alias_entries_are_never_replaced(self):
        self.sensitive_project()
        for kind in ("file", "directory", "dangling", "outside", "absolute", "mixed-case"):
            with self.subTest(kind=kind):
                alias = self.root / (".SystemX" if kind == "mixed-case" else ".systemx")
                if kind == "file":
                    alias.write_text("User file")
                elif kind in {"directory", "mixed-case"}:
                    alias.mkdir()
                else:
                    outside = self.folder / "outside"
                    outside.mkdir(exist_ok=True)
                    target = {"dangling": "absent", "outside": str(outside),
                              "absolute": str(self.root / ".SYSTEMX")}[kind]
                    alias.symlink_to(target, target_is_directory=True)
                with self.assertRaisesRegex(manager.InstallError, "Exact-case conflict"):
                    manager.alias(self.root, create=True)
                self.assertTrue(os.path.lexists(alias))
                if alias.is_symlink() or alias.is_file():
                    alias.unlink()
                else:
                    alias.rmdir()

    def test_standalone_runner_normalizes_valid_alias_and_menu_creates_one(self):
        self.install()
        runner = self.root / ".SYSTEMX/scripts/systemx.py"
        result = subprocess.run([sys.executable, "-B", str(runner), "menu"],
                                input="11\n12\n0\n", text=True, capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Enable local .systemx -> .SYSTEMX alias", result.stdout)
        self.assertTrue((self.root / ".systemx").samefile(self.root / ".SYSTEMX"))
        result = subprocess.run([sys.executable, "-B", str(runner), "--root",
                                 str(self.root / ".systemx"), "paths"], text=True, capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(Path(json.loads(result.stdout)["canonical"]).name, ".SYSTEMX")

    def test_standalone_runner_blocks_duplicate_before_record_write(self):
        self.sensitive_project()
        self.install()
        (self.root / ".SystemX").mkdir()
        runner = self.root / ".SYSTEMX/scripts/systemx.py"
        before = self.root_files()
        result = subprocess.run([sys.executable, "-B", str(runner), "init"],
                                text=True, capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Exact-case conflict", result.stderr)
        self.assertEqual(before, self.root_files())

    def test_source_case_and_archive_case_cannot_hide_second_root(self):
        bad_source = self.folder / "source-project"
        shutil.copytree(self.source, bad_source / ".systemx")
        with self.assertRaisesRegex(manager.InstallError, "Exact-case conflict"):
            manager.install(self.root, source=bad_source)
        self.assertFalse(self.root.exists())
        archive = io.BytesIO()
        with test_manager.zipfile.ZipFile(archive, "w") as output:
            for name, data in manager.read_bundle(self.source)["files"].items():
                output.writestr("tag/.SYSTEMX/" + name, data)
            output.writestr("tag/.systemx/other.txt", "Second tree")
        with patch.object(manager, "get_url", return_value=archive.getvalue()), self.assertRaisesRegex(manager.InstallError, "noncanonical"):
            manager.remote_bundle((self.source / "VERSION").read_text().strip())
        for name in (".SYSTEMX/file", "LOCAL/private", "nested/.systemx/file", "installation.json"):
            with self.subTest(name=name), self.assertRaises(manager.InstallError):
                manager.portable_path(name)

    def test_distribution_directories_cannot_use_conflicting_case_prefixes(self):
        bundle = manager.read_bundle(self.source)
        files = dict(bundle["files"])
        files["DOCS/other.md"] = b"Conflicting directory case"
        manifest = json.loads(files[manager.MANIFEST])
        manifest["files"]["DOCS/other.md"] = manager.digest(files["DOCS/other.md"])
        files[manager.MANIFEST] = json.dumps(manifest).encode()
        with self.assertRaisesRegex(manager.InstallError, "conflicting case spellings"):
            manager.verified_bundle(files)

    def test_direct_runner_rejects_lowercase_stored_root(self):
        self.install()
        canonical = self.root / ".SYSTEMX"
        temporary = self.root / "rename-fixture"
        canonical.rename(temporary)
        temporary.rename(self.root / ".systemx")
        result = subprocess.run([sys.executable, "-B", str(self.root / ".systemx/scripts/systemx.py"), "init"],
                                text=True, capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Exact-case conflict", result.stderr)
        self.assertFalse((self.root / ".systemx/project.json").exists())

    def test_public_template_cannot_ship_a_local_sibling_alias(self):
        self.sensitive_project()
        shutil.copytree(self.source, self.root / ".SYSTEMX", dirs_exist_ok=True)
        manager.alias(self.root, create=True)
        result = manager.run(self.root, ["validate", "--template"], offline=True, capture=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("public template must not include", result.stderr)

    def test_optional_alias_permission_failure_preserves_complete_install(self):
        self.sensitive_project()
        with patch.object(Path, "symlink_to", side_effect=OSError("Symlinks unavailable")):
            with self.assertRaisesRegex(manager.InstallError, "canonical directory is preserved"):
                self.install(lowercase_alias=True)
        self.assertEqual(manager.status(self.root)["integrity"], "verified")
        self.assertEqual(manager.status(self.root)["autoUpdate"], "manual")


if __name__ == "__main__":
    unittest.main()
