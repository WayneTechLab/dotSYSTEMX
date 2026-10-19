"""DATA privacy scaffolding, additive setup, and bounded metadata evidence."""

import argparse
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE))
try:
    SPEC = importlib.util.spec_from_file_location("systemx_data_test", SOURCE / "scripts/data_tools.py")
    data_tools = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(data_tools)
finally:
    sys.path.pop(0)


class DataToolsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="systemx-data-")
        self.addCleanup(self.temp.cleanup)
        self.host = Path(self.temp.name) / "host project"
        self.root = self.host / ".SYSTEMX"
        self.root.mkdir(parents=True)
        shutil.copytree(SOURCE / "templates/data", self.root / "templates/data")

    def init(self, root=None, apply=True):
        return data_tools.initialize(root or self.root, self.root, apply)

    def git(self, *arguments):
        result = subprocess.run([shutil.which("git"), "-C", str(self.host), *arguments],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        return result.stdout

    def snapshot(self, root=None):
        return {p.relative_to(root or self.root).as_posix(): p.read_bytes()
                for p in (root or self.root).rglob("*") if p.is_file()}

    def test_preview_is_read_only_and_init_is_additive_idempotent(self):
        before = self.snapshot()
        preview = self.init(apply=False)
        self.assertEqual(before, self.snapshot())
        self.assertEqual(set(preview["wouldCreate"]), set(data_tools.SCAFFOLD))
        result = self.init()
        self.assertEqual(len(result["created"]), 10)
        (self.root / "DATA/README.md").write_text("User customization")
        payload = self.root / "DATA/TEMP/user.txt"
        payload.write_bytes(b"User payload\x00")
        before = self.snapshot()
        again = self.init()
        self.assertEqual(again["created"], [])
        self.assertEqual(before, self.snapshot())
        (self.root / "DATA/IMPORTS/README.md").unlink()
        self.assertEqual(self.init()["created"], ["IMPORTS/README.md"])
        self.assertEqual(payload.read_bytes(), b"User payload\x00")
        self.assertEqual((self.root / "DATA/README.md").read_text(), "User customization")

    def test_child_init_uses_dedicated_blank_defaults_not_parent_payload(self):
        self.init()
        (self.root / "DATA/README.md").write_text("PRIVATE PARENT CONTENT")
        child = self.root / "Projects/Project-A/.SYSTEMXP"
        child.mkdir(parents=True)
        self.init(root=child)
        self.assertNotIn("PRIVATE PARENT CONTENT", (child / "DATA/README.md").read_text())
        self.assertFalse((child / "templates").exists())
        data_tools.validate_template(child, self.root)

    def test_selected_release_and_wheel_defaults_names_are_supported(self):
        for name in ("1.9.0-alpha.6", "systemx"):
            with self.subTest(name=name):
                defaults = self.host / name
                shutil.copytree(SOURCE / "templates/data", defaults / "templates/data")
                child = self.host / ("project-" + name) / ".SYSTEMXP"
                child.mkdir(parents=True)
                self.assertEqual(len(data_tools.initialize(child, defaults, True)["created"]), 10)
                data_tools.validate_template(child, defaults)
                # Reviewed text seeds permit normal Git CRLF checkout conversion.
                for relative in data_tools.SCAFFOLD:
                    path = child / "DATA" / relative
                    path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
                data_tools.validate_template(child, defaults)

    @unittest.skipUnless(shutil.which("git"), "Git required for effective-rule checks")
    def test_git_rules_ignore_all_payload_depths_and_only_exact_scaffold_is_trackable(self):
        self.git("init", "-q")
        self.init()
        payload = ["root.bin", "nested/README.md", "TEMP/private.json", "TEMP/deep/README.md",
                   "LARGE/sample.bin", "ASSETS/brand/favicon.ico", "RESEARCH/deep/private/README.md"]
        for name in payload:
            path = self.root / "DATA" / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"Fixture")
            probe = subprocess.run([shutil.which("git"), "-C", str(self.host), "check-ignore", "--", str(path)],
                                   capture_output=True, timeout=10)
            self.assertEqual(probe.returncode, 0, str(path))
        for name in data_tools.SCAFFOLD:
            probe = subprocess.run([shutil.which("git"), "-C", str(self.host), "check-ignore", "--", str(self.root / "DATA" / name)],
                                   capture_output=True, timeout=10)
            self.assertEqual(probe.returncode, 1, name)
        self.git("add", ".SYSTEMX/DATA")
        self.assertEqual(len(self.git("ls-files", "-z").split(b"\0")) - 1, 10)
        audit = data_tools.status(self.root)["git"]
        self.assertEqual(audit["state"], "verified", audit)
        self.assertEqual(audit["trackedPayloadCount"], 0)
        self.assertTrue(audit["payloadIgnored"])
        self.assertTrue(audit["scaffoldTrackable"])

    @unittest.skipUnless(shutil.which("git"), "Git required for forced tracked payload checks")
    def test_forced_tracked_payload_warns_and_audit_does_not_modify_index_or_user_data(self):
        self.git("init", "-q")
        self.init()
        payload = self.root / "DATA/LARGE/private.bin"
        payload.write_bytes(b"Fixture payload")
        self.git("add", "-f", ".SYSTEMX/DATA/LARGE/private.bin")
        before = self.snapshot(self.host)
        audit = data_tools.status(self.root)["git"]
        self.assertEqual(before, self.snapshot(self.host))
        self.assertEqual(audit["state"], "warning")
        self.assertTrue(audit["payloadIgnored"])
        self.assertEqual(audit["trackedPayloadCount"], 1)
        self.assertEqual(audit["trackedPayloadPaths"], ["LARGE/private.bin"])
        self.assertIn("Already tracked", " ".join(audit["warnings"]))

    @unittest.skipUnless(shutil.which("git"), "Git required for bounded index checks")
    def test_tracked_metadata_is_bounded_and_never_reported_clean_when_truncated(self):
        self.git("init", "-q")
        self.init()
        for number in range(25):
            (self.root / "DATA/TEMP" / ("item-%02d.txt" % number)).write_text("fixture")
        self.git("add", "-f", ".SYSTEMX/DATA/TEMP")
        audit = data_tools.status(self.root)["git"]
        self.assertEqual(audit["trackedPayloadCount"], 25)
        self.assertEqual(len(audit["trackedPayloadPaths"]), 20)
        self.assertTrue(audit["trackedPathsTruncated"])
        self.assertFalse(audit["trackedPayloadCountIsLowerBound"])
        original_git = data_tools._git
        def limited_git(git, directory, arguments, **kwargs):
            if arguments[0] == "ls-files":
                kwargs["limit"] = 120
            return original_git(git, directory, arguments, **kwargs)
        with patch.object(data_tools, "_git", limited_git):
            bounded = data_tools.status(self.root)["git"]
        self.assertEqual(bounded["state"], "warning")
        self.assertTrue(bounded["trackedPayloadCountIsLowerBound"])
        self.assertLess(bounded["trackedPayloadCount"], 25)
        self.assertTrue(bounded["trackedPathsTruncated"])

    def test_name_only_case_check_stops_at_its_bound(self):
        self.init()
        with patch.object(data_tools, "MAX_DIRECTORY_ENTRIES", 7):
            with self.assertRaisesRegex(ValueError, "case check exceeded"):
                data_tools.status(self.root)

    @unittest.skipUnless(shutil.which("git"), "Git required for custom-exception evidence checks")
    def test_synthetic_probe_pass_does_not_claim_all_actual_untracked_payload_is_ignored(self):
        self.git("init", "-q")
        self.init()
        ignore = self.root / "DATA/.gitignore"
        with ignore.open("a") as stream:
            stream.write("!TEMP/private.csv\n")
        payload = self.root / "DATA/TEMP/private.csv"
        payload.write_text("fixture")
        before = self.snapshot(self.host)
        audit = data_tools.status(self.root)["git"]
        self.assertEqual(before, self.snapshot(self.host))
        self.assertEqual(audit["state"], "verified")
        self.assertTrue(audit["payloadIgnored"])
        self.assertEqual(audit["ignoreEvidence"], "synthetic-probes-and-tracked-index-only")
        self.assertFalse(audit["allUntrackedPayloadVerified"])
        self.assertIn("customized ignore exceptions", audit["limitation"])
        specific = subprocess.run([shutil.which("git"), "-C", str(self.host), "check-ignore", "--no-index", "--", str(payload)],
                                  capture_output=True, timeout=10)
        self.assertEqual(specific.returncode, 1, "Specific customized exception must be exposed")
        self.assertEqual(payload.read_text(), "fixture")

    def test_missing_git_and_nonrepo_are_unverified(self):
        self.init()
        with patch.object(data_tools.shutil, "which", return_value=None):
            self.assertEqual(data_tools.status(self.root)["git"]["state"], "unverified")
        self.assertEqual(data_tools.status(self.root)["git"]["state"], "unverified")

    def test_customized_local_ignore_is_preserved_and_missing_protection_is_reported(self):
        self.init()
        ignore = self.root / "DATA/.gitignore"
        ignore.write_text("# User opted out\n")
        self.init()
        self.assertEqual(ignore.read_text(), "# User opted out\n")
        if shutil.which("git"):
            self.git("init", "-q")
            result = data_tools.status(self.root)["git"]
            self.assertFalse(result["payloadIgnored"])
            self.assertEqual(result["state"], "warning")

    def test_managed_links_hardlinks_case_conflicts_and_special_files_are_refused(self):
        outside = self.host / "outside"
        outside.mkdir()
        for relative in ("DATA", "DATA/TEMP", "DATA/README.md"):
            with self.subTest(relative=relative):
                link = self.root / relative
                link.parent.mkdir(parents=True, exist_ok=True)
                link.symlink_to(outside, target_is_directory=True)
                with self.assertRaises(ValueError):
                    self.init(apply=False)
                link.unlink()
        self.init()
        document = self.root / "DATA/README.md"
        document.unlink()
        original = outside / "user.txt"
        original.write_text("keep")
        os.link(original, document)
        with self.assertRaises(ValueError):
            self.init()
        self.assertEqual(original.read_text(), "keep")
        document.unlink()
        self.init()
        (self.root / "DATA").rename(self.root / "data")
        with self.assertRaises(ValueError):
            self.init()

    def test_record_scope_symlink_is_refused_without_touching_target(self):
        destination = self.host / "real"
        destination.mkdir()
        child = destination / ".SYSTEMXP"
        child.mkdir()
        link = self.host / ".SYSTEMXP"
        link.symlink_to(child, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.init(root=link)
        self.assertEqual(list(child.iterdir()), [])

    def test_audit_never_reads_hashes_or_recursively_walks_payload(self):
        self.init()
        huge = self.root / "DATA/LARGE/huge.bin"
        with huge.open("wb") as stream:
            stream.truncate(2 ** 34)
        outside = self.host / "outside"
        outside.mkdir()
        (outside / "private.txt").write_text("private fixture")
        (self.root / "DATA/TEMP/external").symlink_to(outside, target_is_directory=True)
        with patch.object(Path, "read_bytes", side_effect=AssertionError("unexpected byte read")), \
                patch.object(Path, "read_text", side_effect=AssertionError("unexpected text read")), \
                patch.object(os, "walk", side_effect=AssertionError("unexpected payload walk")):
            result = data_tools.status(self.root)
        self.assertFalse(result["payloadRead"])
        self.assertFalse(result["payloadTraversed"])
        self.assertEqual(huge.stat().st_size, 2 ** 34)
        data_tools.validate_optional(self.root)
        with self.assertRaises(ValueError):
            data_tools.validate_template(self.root, self.root)

    def test_blank_distribution_rejects_extra_payload_without_reading_it(self):
        self.init()
        data_tools.validate_template(self.root, self.root)
        payload = self.root / "DATA/ARCHIVE/unapproved.bin"
        payload.write_bytes(b"fixture")
        original_read = Path.read_bytes
        def guarded_read(path):
            if path == payload:
                raise AssertionError("Unexpected payload byte read")
            return original_read(path)
        with patch.object(Path, "read_bytes", guarded_read):
            with self.assertRaises(ValueError):
                data_tools.validate_template(self.root, self.root)
        self.assertEqual(payload.read_bytes(), b"fixture")

    def test_cli_freeze_and_scope_wrapper(self):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="action", required=True)
        seen = []
        def scope(command):
            seen.append(command.prog)
            command.add_argument("--project")
            return command
        data_tools.add_cli(subparsers, scope)
        self.assertEqual(len(seen), 3)
        args = parser.parse_args(["data", "init", "--project", "Project-A"])
        self.assertFalse(data_tools.dispatch(self.root, self.root, args)["applied"])
        self.assertEqual(parser.parse_args(["data", "audit", "--project", "Project-A"]).data_action, "audit")


if __name__ == "__main__":
    unittest.main()
