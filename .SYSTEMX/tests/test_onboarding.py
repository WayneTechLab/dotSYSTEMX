"""Read-only first-time onboarding and explicit dotenv inventory boundaries."""

import argparse
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest import mock


SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE))
sys.path.insert(0, str(SOURCE / "scripts"))
import onboarding  # noqa: E402


class OnboardingTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="systemx-onboard-")
        self.addCleanup(self.temporary.cleanup)
        self.project = Path(self.temporary.name) / "project"
        self.project.mkdir()
        self.root = self.project / ".SYSTEMX"
        shutil.copytree(SOURCE, self.root,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "local", "logs", "state"))

    def files(self):
        return {path.relative_to(self.project).as_posix(): path.read_bytes()
                for path in self.project.rglob("*") if path.is_file() and not path.is_symlink()}

    def test_status_uses_canonical_records_and_never_reads_dotenv_implicitly(self):
        marker = "IMPLICIT_ENV_VALUE_MUST_NOT_APPEAR_81472"
        (self.project / ".env").write_text("API_KEY=" + marker + "\n", encoding="utf-8")
        before = self.files()
        with mock.patch.object(onboarding.security_agent1, "env_inventory",
                               side_effect=AssertionError("implicit dotenv read")), \
             mock.patch.object(onboarding.shutil, "which", return_value=None):
            result = onboarding.view(self.root)
        self.assertEqual(result["roster"]["counts"]["standardRoles"], 20)
        self.assertEqual(result["roster"]["counts"]["registeredAgents"], 1)
        self.assertEqual(result["agent1"]["missingQuestionCount"], 8)
        self.assertEqual(len(result["providers"]), len(onboarding.PROVIDERS))
        self.assertFalse(result["authenticated"])
        self.assertFalse(result["accessGranted"])
        self.assertFalse(result["executed"])
        self.assertIsNone(result["envInventory"])
        self.assertNotIn(marker, json.dumps(result))
        self.assertEqual(before, self.files())

    def test_plan_asks_scope_surface_and_credential_consumer_without_writes(self):
        before = self.files()
        with mock.patch.object(onboarding.shutil, "which", return_value="/tmp/fake-grok"):
            result = onboarding.view(self.root, mode="plan", provider="grok-build",
                                     surface="cli", account_context="enterprise",
                                     credential_consumer="actions", credential_class="new")
        self.assertEqual([item["id"] for item in result["providers"]], ["grok-build"])
        self.assertTrue(result["providers"][0]["installedNameOnly"])
        self.assertEqual(result["providers"][0]["execution"], "manual-until-reviewed-adapter")
        self.assertIn("disabled for the upstream dotSYSTEMX", result["credentialBoundary"])
        self.assertIn("selected project's state may differ", result["credentialBoundary"])
        self.assertEqual(len(result["questions"]), 5)
        self.assertFalse(result["valuesReturned"])
        self.assertEqual(before, self.files())

    def test_dot_and_muse_are_external_references_not_cli_providers(self):
        result = onboarding.view(self.root, mode="plan", surface="harness")
        by_id = {item["id"]: item for item in result["providers"]}
        self.assertNotIn("codex-dot", by_id)
        self.assertEqual(by_id["openai-dot"]["name"], "OpenAI dot")
        self.assertEqual(by_id["openai-dot"]["execution"], "offline-reference-only")
        self.assertIsNone(by_id["openai-dot"]["installedNameOnly"])
        self.assertEqual(by_id["meta-muse"]["execution"], "offline-reference-only")
        self.assertIn("introducing-muse-personal-ai-agent", by_id["meta-muse"]["reference"])
        self.assertIsNone(result["selection"]["credentialClass"])
        self.assertFalse(result["authenticated"])
        self.assertFalse(result["valuesReturned"])
        no_key = onboarding.view(self.root, mode="plan", credential_consumer="none")
        self.assertEqual(no_key["selection"]["credentialClass"], "none")

    def test_expanded_provider_lanes_do_not_create_runtime_or_credential_defaults(self):
        before = self.files()
        with mock.patch.object(onboarding.shutil, "which", return_value="/tmp/agent"):
            status = onboarding.view(self.root)
        by_id = {item["id"]: item for item in status["providers"]}
        self.assertEqual(len(by_id), len(onboarding.PROVIDERS))
        manual = {"kiro-cli", "claude-code", "opencode-cli", "blackbox-cli",
                  "gemini-cli", "cursor-agent", "aider"}
        self.assertTrue(all(by_id[name]["execution"] == "manual-until-reviewed-adapter"
                            for name in manual))
        self.assertEqual(by_id["codex-sdk"]["execution"], "application-managed")
        self.assertEqual(by_id["kiro-ide"]["execution"], "host-managed")
        self.assertEqual(by_id["kiro-web"]["execution"], "offline-reference-only")
        self.assertEqual(by_id["aws-cli"]["lane"], "host-account")
        self.assertEqual(status["toolchains"]["options"],
                         ["vscode", "codex", "cursor", "kiro", "jetbrains"])
        self.assertFalse(status["toolchains"]["nativeHostBindingsInstalled"])
        # The current Cursor binary is called 'agent'; a generic PATH match
        # alone cannot establish that it belongs to Cursor.
        self.assertIsNone(by_id["cursor-agent"]["installedNameOnly"])
        self.assertIsNone(status["selection"]["provider"])
        self.assertIsNone(status["selection"]["credentialConsumer"])
        self.assertFalse(status["authenticated"] or status["runtimeStarted"])
        sdk = onboarding.view(self.root, mode="plan", provider="codex-sdk",
                              surface="sdk", credential_consumer="server-application")
        self.assertEqual([item["id"] for item in sdk["providers"]], ["codex-sdk"])
        self.assertEqual(sdk["selection"]["credentialClass"], "new")
        self.assertIn("approved secret destination", sdk["credentialBoundary"])
        with self.assertRaisesRegex(ValueError, "does not support"):
            onboarding.view(self.root, provider="kiro-web", surface="cli")
        self.assertEqual(before, self.files())

    def test_child_plan_keeps_instruction_bridge_at_outer_root(self):
        child = self.root / "Projects" / "Demo" / ".SYSTEMXP"
        child.parent.mkdir(parents=True)
        shutil.copytree(SOURCE / "templates" / "project", child)
        result = onboarding.view(child, mode="plan", provider="codex-cli", surface="cli")
        self.assertEqual(result["scope"], "project")
        self.assertTrue(any("outer .SYSTEMX" in step for step in result["nextSteps"]))
        self.assertFalse(any(step.startswith("onboard bridge (") for step in result["nextSteps"]))
        test_key = onboarding.view(self.root, mode="plan", credential_consumer="local-cli",
                                   credential_class="existing-test")
        self.assertIn("rotate before production", test_key["credentialReview"])

    def test_explicit_env_inventory_returns_names_never_value(self):
        secret = "SYNTHETIC_SECRET_NEVER_RETURN_928473"
        (self.project / ".env").write_text("API_TOKEN=" + secret + "\nDEBUG=1\n", encoding="utf-8")
        before = self.files()
        with mock.patch.object(onboarding.security_agent1, "_tracked_env", return_value=(set(), None)):
            result = onboarding.view(self.root, mode="plan", provider="codex-cli",
                                     surface="cli", credential_consumer="local-cli",
                                     env_file=".env")
        encoded = json.dumps(result)
        self.assertEqual(result["envInventory"]["names"], ["API_TOKEN", "DEBUG"])
        self.assertEqual(result["selection"]["credentialClass"], "new")
        self.assertFalse(result["envInventory"]["valuesReturned"])
        self.assertNotIn(secret, encoded)
        self.assertNotIn(secret, onboarding.format_text(result))
        self.assertIn("provider login", result["credentialBoundary"])
        self.assertEqual(before, self.files())

    def test_invalid_provider_surface_and_env_escape_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "Unknown provider"):
            onboarding.view(self.root, provider="unreviewed-ai")
        with self.assertRaisesRegex(ValueError, "does not support"):
            onboarding.view(self.root, provider="grok-bot", surface="vscode")
        with self.assertRaisesRegex(ValueError, "no-credential"):
            onboarding.view(self.root, mode="plan", credential_consumer="none",
                            credential_class="new")
        outside = self.project.parent / "outside.env"
        outside.write_text("TOKEN=SYNTHETIC\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "within the selected project"):
            onboarding.view(self.root, env_file=outside)
        linked = self.project / ".env"
        try:
            linked.symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks unavailable")
        with self.assertRaisesRegex(ValueError, "linked or inaccessible"):
            onboarding.view(self.root, env_file=".env")

    def test_cli_parser_exposes_first_run_selection_and_bridge_preview(self):
        parser = argparse.ArgumentParser()
        commands = parser.add_subparsers(dest="action", required=True)
        onboarding.add_cli(commands)
        args = parser.parse_args(["onboard", "plan", "--provider", "muse-code",
                                  "--surface", "vscode", "--account-context", "personal",
                                  "--credential-consumer", "vscode-extension"])
        self.assertEqual(args.onboard_action, "plan")
        self.assertEqual(args.provider, "muse-code")
        self.assertEqual(args.format, "text")
        result = onboarding.dispatch(self.root, self.root, args)
        self.assertFalse(result["executed"])
        self.assertEqual(result["providers"][0]["execution"], "task-scoped-agent-y")
        self.assertIn("workspace trust", " ".join(result["providerNextSteps"]))
        human = onboarding.format_text(result)
        self.assertIn(".SYSTEMX first-time setup: plan", human)
        self.assertIn("muse-code", human)
        self.assertNotIn("SYNTHETIC_SECRET_NEVER_RETURN", human)
        preview_args = parser.parse_args(["onboard", "bridge"])
        # Bridge creation is owned by the dedicated helper. Its preview must
        # remain separately explicit and cannot be triggered by status/plan.
        self.assertEqual(preview_args.onboard_action, "bridge")
        self.assertFalse(preview_args.apply)
        self.assertEqual(preview_args.format, "text")

    def test_bridge_dispatch_requires_preview_hash_and_preserves_existing_file(self):
        parser = argparse.ArgumentParser()
        commands = parser.add_subparsers(dest="action", required=True)
        onboarding.add_cli(commands)
        preview = onboarding.dispatch(self.root, self.root,
                                      parser.parse_args(["onboard", "bridge"]))
        self.assertEqual(preview["path"], "AGENTS.md")
        self.assertFalse(preview["applied"])
        self.assertIn(preview["contentSha256"], onboarding.format_text(preview))
        with self.assertRaisesRegex(ValueError, "supply its contentSha256"):
            onboarding.dispatch(self.root, self.root,
                                parser.parse_args(["onboard", "bridge", "--apply"]))
        applied = onboarding.dispatch(
            self.root, self.root,
            parser.parse_args(["onboard", "bridge", "--apply", "--expected-sha256",
                               preview["contentSha256"]]))
        self.assertTrue(applied["applied"])
        original = (self.project / "AGENTS.md").read_bytes()
        with self.assertRaises(ValueError):
            onboarding.dispatch(
                self.root, self.root,
                parser.parse_args(["onboard", "bridge", "--apply", "--expected-sha256",
                                   preview["contentSha256"]]))
        self.assertEqual((self.project / "AGENTS.md").read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
