"""The optional root instruction bridge preserves existing harness guidance."""

from pathlib import Path
import os
import sys
import tempfile
import unittest
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import agent_guide_bridge as bridge


class AgentGuideBridgeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.project = Path(self.temporary.name) / "project"
        self.project.mkdir()
        self.selected = self.project / ".SYSTEMX"
        self.selected.mkdir()
        (self.selected / "AGENTS.md").write_text("# Reviewed project guide\n", encoding="utf-8")
        self.target = self.project / "AGENTS.md"

    def test_preview_then_exclusive_apply_creates_only_the_pointer(self):
        before = (self.selected / "AGENTS.md").read_bytes()
        preview = bridge.bridge_status(self.selected)
        self.assertEqual(preview["path"], "AGENTS.md")
        self.assertEqual(preview["state"], "absent")
        self.assertEqual(preview["preview"], bridge.POINTER)
        self.assertFalse(preview["applied"] or preview["preserved"])
        self.assertFalse(self.target.exists())

        result = bridge.bridge_apply(self.selected, preview["contentSha256"])
        self.assertTrue(result["applied"])
        self.assertEqual(result["state"], "existing")
        self.assertEqual(self.target.read_bytes(), bridge.POINTER_BYTES)
        self.assertEqual((self.selected / "AGENTS.md").read_bytes(), before)
        self.assertEqual(list(self.project.iterdir()), [self.selected, self.target])

    def test_existing_regular_file_is_preserved_and_never_read(self):
        original = b"# Existing user instructions\nDo not replace me.\n"
        self.target.write_bytes(original)
        with patch.object(Path, "read_bytes", side_effect=AssertionError("existing content was read")):
            preview = bridge.bridge_status(self.selected)
            self.assertEqual(preview["state"], "existing")
            self.assertTrue(preview["preserved"])
            with self.assertRaisesRegex(ValueError, "preserved"):
                bridge.bridge_apply(self.selected, preview["contentSha256"])
        self.assertEqual(self.target.read_bytes(), original)

    def test_symlink_and_directory_targets_are_conflicts(self):
        other = self.project / "other"
        other.write_text("user file\n", encoding="utf-8")
        try:
            self.target.symlink_to(other)
        except (OSError, NotImplementedError) as error:
            self.skipTest("Symlink creation unavailable: " + str(error))
        self.assertEqual(bridge.bridge_status(self.selected)["state"], "conflict")
        with self.assertRaisesRegex(ValueError, "preserved"):
            bridge.bridge_apply(self.selected, bridge.POINTER_SHA256)
        self.assertEqual(other.read_text(encoding="utf-8"), "user file\n")
        self.target.unlink()
        self.target.mkdir()
        self.assertEqual(bridge.bridge_status(self.selected)["state"], "conflict")
        with self.assertRaisesRegex(ValueError, "preserved"):
            bridge.bridge_apply(self.selected, bridge.POINTER_SHA256)

    def test_rejects_wrong_scope_and_linked_or_missing_inner_guide(self):
        with self.assertRaisesRegex(ValueError, "exact .SYSTEMX"):
            bridge.bridge_status(self.project)
        (self.selected / "AGENTS.md").unlink()
        with self.assertRaisesRegex(ValueError, "guide is missing"):
            bridge.bridge_status(self.selected)
        outside = self.project / "other-guide"
        outside.write_text("# Other\n", encoding="utf-8")
        try:
            (self.selected / "AGENTS.md").symlink_to(outside)
        except (OSError, NotImplementedError) as error:
            self.skipTest("Symlink creation unavailable: " + str(error))
        with self.assertRaisesRegex(ValueError, "regular file"):
            bridge.bridge_status(self.selected)

    def test_stale_hash_and_concurrent_creation_preserve_winner(self):
        with self.assertRaisesRegex(ValueError, "preview hash changed"):
            bridge.bridge_apply(self.selected, "0" * 64)
        created = False
        original_anchor = bridge._anchored_project

        def race(project, project_stat, selected_stat, guide_stat):
            nonlocal created
            project_fd, root_fd = original_anchor(project, project_stat, selected_stat, guide_stat)
            if not created:
                created = True
                descriptor = os.open("AGENTS.md", os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                                     0o644, dir_fd=project_fd)
                with os.fdopen(descriptor, "wb") as stream:
                    stream.write(b"# Concurrent user file\n")
            return project_fd, root_fd

        with patch.object(bridge, "_anchored_project", side_effect=race):
            with self.assertRaisesRegex(ValueError, "appeared or conflicts"):
                bridge.bridge_apply(self.selected, bridge.POINTER_SHA256)
        self.assertEqual(self.target.read_bytes(), b"# Concurrent user file\n")

    def test_partial_write_is_removed_only_if_created_inode_is_still_at_target(self):
        original_write = os.write
        count = 0

        def partial_then_error(descriptor, data):
            nonlocal count
            count += 1
            if count == 1:
                return original_write(descriptor, data[:5])
            raise OSError("simulated write failure")

        with patch.object(bridge.os, "write", side_effect=partial_then_error):
            with self.assertRaisesRegex(OSError, "simulated write failure"):
                bridge.bridge_apply(self.selected, bridge.POINTER_SHA256)
        self.assertFalse(self.target.exists())

        def replace_then_error(descriptor, data):
            original_write(descriptor, data[:5])
            self.target.unlink()
            self.target.write_bytes(b"# New owner file\n")
            raise OSError("simulated replacement")

        with patch.object(bridge.os, "write", side_effect=replace_then_error):
            with self.assertRaisesRegex(OSError, "simulated replacement"):
                bridge.bridge_apply(self.selected, bridge.POINTER_SHA256)
        self.assertEqual(self.target.read_bytes(), b"# New owner file\n")


if __name__ == "__main__":
    unittest.main()
