"""Isolated behavior checks. No real project commands or cloud accounts are used."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1]


class SystemxTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="systemx-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "project with spaces"
        self.systemx = self.root / ".SYSTEMX"
        shutil.copytree(SOURCE, self.systemx, ignore=shutil.ignore_patterns(
            "__pycache__", "project.json", "project", "local", "logs", "state"))
        self.runner = self.systemx / "scripts" / "systemx.py"
        self.config = json.loads((self.systemx / "config" / "project.example.json").read_text())

    def run_cli(self, *args, input_text=None):
        return subprocess.run([sys.executable, "-B", str(self.runner), *args],
                              cwd=self.temp.name, text=True, input=input_text,
                              capture_output=True, timeout=15)

    def assert_ok(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def save_config(self):
        (self.systemx / "project.json").write_text(json.dumps(self.config), encoding="utf-8")

    def record(self, label, exit_code=0):
        code = ("from pathlib import Path; import sys; "
                "p=Path('events.txt'); "
                "p.write_text((p.read_text() if p.exists() else '') + " + repr(label + "\n") + "); "
                "sys.exit(" + str(exit_code) + ")")
        return [sys.executable, "-c", code]

    def wire_project(self, check_exit=0, build_exit=0):
        self.config["project"]["name"] = "Isolated fixture"
        self.config["checks"] = [{"name": "test", "command": self.record("check", check_exit)}]
        self.config["commands"] = {
            "dev": self.record("dev"), "build": self.record("build", build_exit),
            "deploy": self.record("deploy")}
        self.save_config()

    def events(self):
        path = self.root / "events.txt"
        return path.read_text().splitlines() if path.exists() else []

    def test_clean_template_validates_without_initialization(self):
        self.assert_ok(self.run_cli("validate"))
        self.assertFalse((self.systemx / "project.json").exists())

    def test_init_creates_config_once_and_preserves_existing_bytes(self):
        self.assert_ok(self.run_cli("init"))
        path = self.systemx / "project.json"
        before = path.read_bytes()
        result = self.run_cli("init")
        self.assertEqual(result.returncode, 2)
        self.assertIn("already exists", result.stderr)
        self.assertEqual(path.read_bytes(), before)

    def test_missing_and_empty_config_never_pass_project_checks(self):
        self.assertEqual(self.run_cli("check").returncode, 2)
        self.save_config()
        result = self.run_cli("check")
        self.assertEqual(result.returncode, 2)
        self.assertIn("No project checks configured", result.stderr)

    def test_deploy_dry_run_executes_no_project_commands(self):
        self.wire_project()
        result = self.run_cli("deploy", "--dry-run")
        self.assert_ok(result)
        self.assertIn("Dry run", result.stdout)
        self.assertIn("deploy:", result.stdout)
        self.assertEqual(self.events(), [])

    def test_deploy_runs_checks_build_and_deploy_in_project_root(self):
        self.wire_project()
        self.assert_ok(self.run_cli("deploy"))
        self.assertEqual(self.events(), ["check", "build", "deploy"])
        self.assertFalse((Path(self.temp.name) / "events.txt").exists())

    def test_failed_check_preserves_exit_code_and_stops_remaining_plan(self):
        self.wire_project(check_exit=17)
        self.config["checks"].append({"name": "later", "command": self.record("later")})
        self.save_config()
        self.assertEqual(self.run_cli("deploy").returncode, 17)
        self.assertEqual(self.events(), ["check"])

    def test_failed_build_prevents_deploy(self):
        self.wire_project(build_exit=19)
        self.assertEqual(self.run_cli("deploy").returncode, 19)
        self.assertEqual(self.events(), ["check", "build"])

    def test_unconfigured_or_missing_executable_prevents_partial_execution(self):
        self.wire_project()
        self.config["commands"]["deploy"] = []
        self.save_config()
        self.assertEqual(self.run_cli("deploy").returncode, 2)
        self.assertEqual(self.events(), [])
        self.config["commands"]["deploy"] = ["systemx-nonexistent-test-executable"]
        self.save_config()
        self.assertEqual(self.run_cli("deploy").returncode, 2)
        self.assertEqual(self.events(), [])

    def test_dev_runs_independently_of_build_checks(self):
        self.config["commands"]["dev"] = self.record("dev")
        self.save_config()
        self.assert_ok(self.run_cli("dev"))
        self.assertEqual(self.events(), ["dev"])

    def test_arguments_are_passed_literally_without_shell_expansion(self):
        literal = "$(touch unexpected-file); $HOME && echo injected"
        self.config["commands"]["dev"] = [sys.executable, "-c",
            "from pathlib import Path; import sys; Path('argument.txt').write_text(sys.argv[1])", literal]
        self.save_config()
        self.assert_ok(self.run_cli("dev"))
        self.assertEqual((self.root / "argument.txt").read_text(), literal)
        self.assertFalse((self.root / "unexpected-file").exists())

    def test_relative_script_runs_from_project_root(self):
        script = self.root / "local-command.py"
        script.write_text("from pathlib import Path\nPath('relative-result').write_text('ok')\n")
        self.config["commands"]["dev"] = [sys.executable, "local-command.py"]
        self.save_config()
        self.assert_ok(self.run_cli("dev"))
        self.assertEqual((self.root / "relative-result").read_text(), "ok")

    def test_invalid_configuration_and_duplicate_checks_are_rejected(self):
        self.wire_project()
        for bad in ("npm test", [""], [123]):
            with self.subTest(command=bad):
                self.config["commands"]["build"] = bad
                self.save_config()
                self.assertEqual(self.run_cli("validate").returncode, 2)
        self.wire_project()
        self.config["checks"] *= 2
        self.save_config()
        self.assertEqual(self.run_cli("validate").returncode, 2)
        self.wire_project()
        self.config["schemaVersion"] = True
        self.save_config()
        self.assertEqual(self.run_cli("validate").returncode, 2)

    def test_broken_link_and_removed_component_are_rejected(self):
        extra = self.systemx / "extra.md"
        extra.write_text("[missing](missing-file.md)\n")
        self.assertIn("broken", self.run_cli("validate").stderr)
        extra.write_text("Reference: " + ".SYSTEMX/" + "LAN/old.md\n")
        self.assertIn("removed component", self.run_cli("validate").stderr)
        extra.unlink()
        (self.systemx / "KIT").mkdir()
        self.assertEqual(self.run_cli("validate").returncode, 2)

    def test_missing_required_file_is_rejected(self):
        (self.systemx / "LICENSE").unlink()
        self.assertIn("Missing required file: LICENSE", self.run_cli("validate").stderr)

    def test_symlink_and_outside_project_link_are_rejected(self):
        target = Path(self.temp.name) / "outside.md"
        target.write_text("Outside fixture")
        (self.systemx / "extra.md").symlink_to(target)
        self.assertIn("Symlinks", self.run_cli("validate").stderr)
        (self.systemx / "extra.md").unlink()
        (self.systemx / "extra.md").write_text("[outside](../../outside.md)\n")
        self.assertIn("out-of-project", self.run_cli("validate").stderr)

    def test_runtime_folders_are_not_scanned(self):
        for name in ("local", "logs", "state"):
            folder = self.systemx / name
            folder.mkdir()
            (folder / "private.json").write_text("not valid JSON")
            (folder / "private.md").write_text("[private](absent.md)")
        self.assert_ok(self.run_cli("validate"))

    def test_doctor_is_read_only_and_reports_missing_executables(self):
        self.wire_project()
        before = (self.systemx / "project.json").read_bytes()
        self.assert_ok(self.run_cli("doctor"))
        self.assertEqual(self.events(), [])
        self.assertEqual((self.systemx / "project.json").read_bytes(), before)
        self.config["commands"]["dev"] = ["systemx-nonexistent-test-executable"]
        self.save_config()
        self.assertEqual(self.run_cli("doctor").returncode, 2)

    def test_menu_exits_at_eof_and_does_not_deploy_without_confirmation(self):
        self.wire_project()
        self.assert_ok(self.run_cli(input_text=""))
        self.assert_ok(self.run_cli("menu", input_text="8\nno\n0\n"))
        self.assertEqual(self.events(), [])

    @unittest.skipUnless(shutil.which("bash"), "Bash launcher requires Bash")
    def test_legacy_launcher_works_from_another_directory(self):
        result = subprocess.run(["bash", str(self.systemx / "WSG-MENU.sh"), "validate"],
                                cwd=self.temp.name, text=True, capture_output=True, timeout=15)
        self.assert_ok(result)

    @unittest.skipUnless(shutil.which("git"), "Git ignore check requires Git")
    def test_runtime_is_ignored_but_project_configuration_is_trackable(self):
        subprocess.run(["git", "init", "--quiet", str(self.root)], check=True, capture_output=True)
        self.save_config()
        runtime = self.systemx / "logs" / "run.txt"
        runtime.parent.mkdir()
        runtime.write_text("local log")
        ignored = subprocess.run(["git", "check-ignore", "--quiet", str(runtime)], cwd=self.root)
        tracked = subprocess.run(["git", "check-ignore", "--quiet", str(self.systemx / "project.json")], cwd=self.root)
        self.assertEqual(ignored.returncode, 0)
        self.assertEqual(tracked.returncode, 1)


if __name__ == "__main__":
    unittest.main()
