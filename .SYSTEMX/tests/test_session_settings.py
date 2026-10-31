"""Selected-scope session settings expose hashes and status, never contents."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE))
sys.path.insert(0, str(SOURCE / "scripts"))
import agent_beta  # noqa: E402
import session_settings  # noqa: E402


class SessionSettingsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="systemx-session-settings-")
        self.addCleanup(self.temporary.cleanup)
        self.project = Path(self.temporary.name) / "project"
        self.project.mkdir()
        self.root = self.project / ".SYSTEMX"
        shutil.copytree(SOURCE, self.root,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "local", "logs", "state"))
        self.runner = self.root / "scripts/systemx.py"

    def call(self, *args):
        return subprocess.run([sys.executable, "-I", "-B", str(self.runner), *args],
                              cwd=self.project, text=True, capture_output=True, timeout=20)

    def test_blank_scope_maps_ten_fixed_rules_without_content_or_writes(self):
        before = {path.relative_to(self.root).as_posix(): path.read_bytes()
                  for path in self.root.rglob("*") if path.is_file()}
        result = session_settings.status(self.root, self.root)
        self.assertEqual(result["scope"], {"kind": "root", "name": ".SYSTEMX"})
        self.assertEqual(len(result["canonicalRules"]), 10)
        self.assertTrue(all(item["state"] == "present" for item in result["canonicalRules"]))
        self.assertFalse(result["agentBeta"]["registered"])
        self.assertEqual(result["agent1"]["missingQuestionCount"], 8)
        self.assertEqual(result["agenda"]["optionCount"], 0)
        self.assertTrue(result["agenda"]["catalogsInstalled"])
        self.assertEqual(result["agenda"]["settingDefinitions"], 10)
        self.assertEqual(result["agenda"]["decisionRules"], 4)
        self.assertEqual(result["agenda"]["defaultContextState"], "unset")
        self.assertEqual(result["agenda"]["defaultAccessState"], "no-row")
        self.assertFalse(result["executed"])
        self.assertFalse(result["accessGranted"])
        after = {path.relative_to(self.root).as_posix(): path.read_bytes()
                 for path in self.root.rglob("*") if path.is_file()}
        self.assertEqual(before, after)

    def test_compact_packet_preserves_status_and_summarizes_rule_revision(self):
        full = session_settings.status(self.root, self.root)
        compact = session_settings.status(self.root, self.root, compact=True)
        self.assertNotIn("canonicalRules", compact)
        self.assertEqual(compact["rulesSummary"]["count"], len(full["canonicalRules"]))
        self.assertEqual(compact["rulesSummary"]["absent"], [])
        self.assertRegex(compact["rulesSummary"]["revision"], r"^[a-f0-9]{64}$")
        for key in ("scope", "agentBeta", "agent1", "agenda", "rulesReadBytes",
                    "executed", "accessGranted", "limit"):
            self.assertEqual(compact[key], full[key])
        full_bytes = len(json.dumps(full, indent=2).encode("utf-8"))
        compact_bytes = len(json.dumps(compact, indent=2).encode("utf-8"))
        self.assertLess(compact_bytes, full_bytes // 2)
        cli = self.call("session-settings", "--compact")
        self.assertEqual(cli.returncode, 0, cli.stderr)
        self.assertEqual(json.loads(cli.stdout), compact)

    def test_beta_rule_hash_and_agent1_private_config_are_sanitized(self):
        initial_revision = session_settings.status(self.root, self.root, compact=True)["rulesSummary"]["revision"]
        agent_beta.initialize(self.root, self.root, apply=True)
        agent_beta.add_bot(self.root, "EXAMPLE", apply=True)
        rules = self.root / "AGENTB/.SYSTEMXB-EXAMPLE/Rules.MD"
        marker = "SYNTHETIC_PRIVATE_RULE_VALUE_486"
        rules.write_text("# Rules\n" + marker + "\n", encoding="utf-8")
        configured = self.call("agent-1", "setup", "--account-context", "personal",
                               "--repo", "Private/Repository", "--review-scope", "root",
                               "--actor-role", "owner", "--secret-target", "none",
                               "--local-secret-store", "none", "--env-history-reviewed", "yes",
                               "--rotation-decision", "not-applicable", "--apply")
        self.assertEqual(configured.returncode, 0, configured.stderr)
        result = session_settings.status(self.root, self.root)
        encoded = json.dumps(result)
        self.assertNotIn(marker, encoded)
        self.assertNotIn("Private/Repository", encoded)
        self.assertEqual(result["agentBeta"]["botCount"], 1)
        self.assertTrue(result["agentBeta"]["registered"])
        entry = result["canonicalRules"][-1]
        self.assertEqual(entry["path"], "AGENTB/.SYSTEMXB-EXAMPLE/Rules.MD")
        self.assertEqual(entry["sha256"], hashlib.sha256(rules.read_bytes()).hexdigest())
        compact = session_settings.status(self.root, self.root, compact=True)
        self.assertNotIn(marker, json.dumps(compact))
        self.assertNotIn("Private/Repository", json.dumps(compact))
        self.assertEqual(compact["rulesSummary"]["count"], 11)
        self.assertNotEqual(compact["rulesSummary"]["revision"], initial_revision)

    def test_child_scope_does_not_fall_back_to_root_rules_and_cli_routes(self):
        created = self.call("projects", "add", "Demo", "--apply")
        self.assertEqual(created.returncode, 0, created.stderr)
        child = self.root / "Projects/Demo/.SYSTEMXP"
        result = session_settings.status(child, self.root)
        self.assertEqual(result["scope"], {"kind": "project", "name": "Demo"})
        self.assertTrue(all(item["state"] == "absent" for item in result["canonicalRules"]))
        self.assertEqual(result["rulesReadBytes"], 0)
        cli = self.call("projects", "session-settings", "--project", "Demo")
        self.assertEqual(cli.returncode, 0, cli.stderr)
        self.assertEqual(json.loads(cli.stdout)["scope"], result["scope"])
        compact = self.call("projects", "session-settings", "--project", "Demo", "--compact")
        self.assertEqual(compact.returncode, 0, compact.stderr)
        self.assertEqual(json.loads(compact.stdout)["rulesSummary"]["absent"],
                         [item["id"] for item in result["canonicalRules"]])

    def test_symlinked_rule_is_refused(self):
        rule = self.root / "AUTOBOT/Rules.MD"
        outside = self.project / "outside.MD"
        outside.write_text("# Outside\n", encoding="utf-8")
        rule.unlink()
        try:
            rule.symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest("Symbolic links unavailable")
        with self.assertRaises(ValueError):
            session_settings.status(self.root, self.root)


if __name__ == "__main__":
    unittest.main()
