"""Focused Agent 1 safety and catalog behavior checks using synthetic files."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "scripts"))
import security_agent1 as agent1  # noqa: E402


# The file-backed Agent 1 paths use POSIX anchored handles. Windows support is
# intentionally limited to metadata and filename-level checks until equivalent
# containment can be proved; the unsupported-platform tests below still run.
REQUIRES_ANCHORED_FILES = unittest.skipUnless(
    agent1._secure_file_ops_available(), "POSIX anchored file operations required")


class Agent1Tests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory(prefix="systemx-agent1-")
        self.addCleanup(self.scratch.cleanup)
        self.project = Path(self.scratch.name) / "fixture"
        self.project.mkdir()
        (self.project / ".SYSTEMX").mkdir()
        (self.project / ".SYSTEMX" / "START-HERE.md").write_text("Fixture\n")
        (self.project / ".SYSTEMX" / "AGENTS" / "agent.0").mkdir(parents=True)
        (self.project / ".SYSTEMX" / "AGENTS" / "agent.0" / "MEMORY.md").write_text("Fixture\n")
        (self.project / ".SYSTEMX" / "AGENTS" / "REGISTRY.json").write_text(json.dumps({
            "schemaVersion": 1, "agents": [{"id": "agent.0", "role": "coordinator",
                                             "memory": "AGENTS/agent.0/MEMORY.md"}]}))
        (self.project / ".SYSTEMX" / "WORK").mkdir()
        (self.project / ".SYSTEMX" / "WORK" / "TASKS.json").write_text('{"schemaVersion":1,"tasks":[]}')
        (self.project / ".SYSTEMX" / "WORK" / "FOCUS.json").write_text(
            '{"schemaVersion":1,"objective":"","taskIds":[],"checkpoint":"","updatedAt":""}')
        (self.project / ".SYSTEMX" / "PLAN").mkdir()
        (self.project / ".SYSTEMX" / "PLAN" / "MASTER-PLAN.md").write_text("# Fixture\n")
        self.defaults = HERE

    def parse(self, *tokens):
        parser = argparse.ArgumentParser()
        agent1.add_cli(parser.add_subparsers(dest="action", required=True))
        return parser.parse_args(["agent-1", *tokens])

    def setup_secret_target(self, actor_role="owner", target="repository"):
        args = self.parse("setup", "--apply", "--account-context", "enterprise", "--actor-role", actor_role,
                          "--repo", "owner/repo", "--review-scope", "root", "--secret-target", target,
                          "--local-secret-store", "none", "--env-history-reviewed", "yes",
                          "--rotation-decision", "not-applicable")
        agent1.dispatch(self.project, self.defaults, args)
        (self.project / ".env").write_text("TOKEN=fixture_value_not_uploaded\n")
        tracked = patch.object(agent1, "_tracked_env", return_value=(set(), None))
        tracked.start()
        self.addCleanup(tracked.stop)

    def test_catalog_is_exactly_400_distinct_questions_and_ten_events(self):
        questions, events = agent1._catalog(self.defaults)
        self.assertEqual(questions["defaultProfile"], "all-in-one")
        self.assertEqual(len(questions["categories"]), 20)
        self.assertEqual(sum(len(item["questions"]) for item in questions["categories"]), 400)
        self.assertEqual(len(events["buckets"]), 10)
        ids = [question["id"] for category in questions["categories"] for question in category["questions"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(agent1.validate_catalog(self.defaults)["questions"], 400)
        self.assertEqual(agent1.validate_template(self.defaults, self.defaults)["eventBuckets"], 10)

    def test_warning_only_check_reports_tracked_env_without_secret_content_or_write(self):
        secret = "SYNTHETIC_VALUE_DO_NOT_PRINT"
        (self.project / ".env").write_text("API_KEY=" + secret + "\n")
        (self.project / "package.json").write_text('{"name":"fixture"}\n')
        (self.project / ".env.example").write_text("API_KEY=example\n")
        subprocess.run(["git", "init", "-q", str(self.project)], check=True)
        subprocess.run(["git", "-C", str(self.project), "add", ".env"], check=True)
        before = {p.relative_to(self.project).as_posix(): p.read_bytes()
                  for p in self.project.rglob("*") if p.is_file() and ".git" not in p.parts}
        report = agent1.assess(self.project, self.defaults)
        payload = json.dumps(report)
        self.assertEqual(report["mode"], "warning-only")
        self.assertEqual(report["profile"], "all-in-one")
        self.assertEqual(report["questionsSelected"], 400)
        self.assertEqual(report["questionsAnswered"], 0)
        self.assertIn("ENV_TRACKED", [item["code"] for item in report["findings"]])
        self.assertIn("JS_LOCKFILE_NOT_SEEN", [item["code"] for item in report["findings"]])
        self.assertNotIn(secret, payload)
        self.assertNotIn(".env.example", report["inventory"]["dotenvFileNames"])
        after = {p.relative_to(self.project).as_posix(): p.read_bytes()
                 for p in self.project.rglob("*") if p.is_file() and ".git" not in p.parts}
        self.assertEqual(before, after)

    @REQUIRES_ANCHORED_FILES
    def test_dotenv_inventory_and_migration_preview_never_return_values(self):
        secret = "SYNTHETIC_TOP_SECRET_VALUE"
        (self.project / ".env").write_text("# fixture\nexport API_KEY=" + secret + "\nAPI_KEY=duplicate\nBAD LINE\n")
        inventory = agent1.env_inventory(self.project, ".env")
        self.assertEqual(inventory["names"], ["API_KEY"])
        self.assertEqual(inventory["duplicateNames"], ["API_KEY"])
        self.assertEqual(inventory["unsupportedLineNumbers"], [4])
        args = self.parse("env-migrate", "--env-file", ".env", "--repo", "owner/repo")
        preview = agent1.dispatch(self.project, self.defaults, args)
        self.assertEqual(preview["mode"], "preview")
        self.assertFalse(preview["secretSet"])
        self.assertEqual(preview["credentialClass"], "new")
        self.assertNotIn(secret, json.dumps(inventory) + json.dumps(preview))

    @REQUIRES_ANCHORED_FILES
    def test_names_only_example_is_previewed_then_created_without_changing_source(self):
        secret = "SYNTHETIC_VALUE_NOT_FOR_EXAMPLE"
        source = self.project / ".env"
        source.write_text("API_KEY=" + secret + "\nSERVICE_TOKEN=other_synthetic\n")
        original = source.read_bytes()
        example = self.project / ".env.example"
        args = self.parse("env-sanitize", "--env-file", ".env")
        preview = agent1.dispatch(self.project, self.defaults, args)
        self.assertEqual(preview["mode"], "preview")
        self.assertFalse(example.exists())
        args = self.parse("env-sanitize", "--env-file", ".env", "--apply")
        applied = agent1.dispatch(self.project, self.defaults, args)
        self.assertTrue(applied["changed"])
        self.assertEqual(source.read_bytes(), original)
        self.assertIn("API_KEY=\n", example.read_text())
        self.assertNotIn(secret, example.read_text() + json.dumps(applied))
        self.assertFalse(applied["localStoreWired"])
        self.assertTrue(applied["rotationStillRequired"])

    @REQUIRES_ANCHORED_FILES
    def test_example_replacement_requires_existing_hash_guard(self):
        (self.project / ".env").write_text("KEY=synthetic\n")
        example = self.project / ".env.example"
        example.write_text("# existing reviewed content\n")
        preview = agent1.dispatch(self.project, self.defaults,
                                  self.parse("env-sanitize", "--env-file", ".env"))
        with self.assertRaisesRegex(ValueError, "guarded replacement"):
            agent1.dispatch(self.project, self.defaults,
                            self.parse("env-sanitize", "--env-file", ".env", "--apply"))
        self.assertEqual(example.read_text(), "# existing reviewed content\n")
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            agent1.dispatch(self.project, self.defaults,
                            self.parse("env-sanitize", "--env-file", ".env", "--apply",
                                       "--replace-existing", "--expect-sha256", "0" * 64))
        result = agent1.dispatch(self.project, self.defaults,
                                 self.parse("env-sanitize", "--env-file", ".env", "--apply",
                                            "--replace-existing", "--expect-sha256",
                                            preview["existingSHA256"]))
        self.assertTrue(result["changed"])
        self.assertEqual(example.read_text().splitlines()[-1], "KEY=")

    @REQUIRES_ANCHORED_FILES
    def test_existing_credential_is_explicit_test_only(self):
        (self.project / ".env").write_text("KEY=synthetic\n")
        args = self.parse("env-migrate", "--env-file", ".env", "--repo", "owner/repo",
                          "--credential-class", "existing-test")
        with self.assertRaisesRegex(ValueError, "ack-test-only"):
            agent1.dispatch(self.project, self.defaults, args)
        args = self.parse("env-migrate", "--env-file", ".env", "--repo", "owner/repo",
                          "--credential-class", "existing-test", "--ack-test-only")
        preview = agent1.dispatch(self.project, self.defaults, args)
        self.assertTrue(preview["testOnly"])
        self.assertFalse(preview["secretSet"])

    def test_setup_is_preview_first_and_apply_only_creates_warning_only_record(self):
        config = self.project / ".SYSTEMX" / "local" / "AGENT1-CONFIG.json"
        self.assertFalse(config.exists())
        args = self.parse("setup", "--account-context", "personal", "--actor-role", "owner")
        preview = agent1.dispatch(self.project, self.defaults, args)
        self.assertFalse(preview["configured"])
        self.assertTrue(preview["missingQuestions"])
        self.assertFalse(config.exists())
        args = self.parse("setup", "--apply", "--account-context", "personal", "--actor-role", "owner")
        with self.assertRaisesRegex(ValueError, "Answer all first-run"):
            agent1.dispatch(self.project, self.defaults, args)
        args = self.parse("setup", "--apply", "--account-context", "personal", "--actor-role", "owner",
                          "--repo", "owner/repo", "--review-scope", "root", "--secret-target", "none",
                          "--local-secret-store", "none", "--env-history-reviewed", "yes",
                          "--rotation-decision", "not-applicable")
        result = agent1.dispatch(self.project, self.defaults, args)
        self.assertTrue(result["changed"])
        self.assertEqual(json.loads(config.read_text())["mode"], "warning-only")
        self.assertFalse(json.loads(config.read_text())["serviceInstalled"])
        self.assertEqual(agent1.status(self.project)["config"]["actorRole"], "owner")
        self.assertTrue(agent1.status(self.project)["registration"]["registered"])
        registry = json.loads((self.project / ".SYSTEMX" / "AGENTS" / "REGISTRY.json").read_text())
        self.assertIn({"id": "agent.1", "role": "security-access", "memory": "AGENTS/agent.1/MEMORY.md"},
                      registry["agents"])

    def test_setup_refuses_reserved_role_conflict_and_preserves_compatible_memory(self):
        registry_path = self.project / ".SYSTEMX" / "AGENTS" / "REGISTRY.json"
        memory = self.project / ".SYSTEMX" / "AGENTS" / "agent.1" / "MEMORY.md"
        memory.parent.mkdir()
        memory.write_text("Existing private checkpoint\n")
        registry = json.loads(registry_path.read_text())
        registry["agents"].append({"id": "agent.1", "role": "different-role",
                                   "memory": "AGENTS/agent.1/MEMORY.md"})
        registry_path.write_text(json.dumps(registry))
        with self.assertRaisesRegex(ValueError, "another role"):
            agent1.dispatch(self.project, self.defaults, self.parse("setup"))
        self.assertEqual(memory.read_text(), "Existing private checkpoint\n")
        registry["agents"][-1]["role"] = "security-access"
        registry_path.write_text(json.dumps(registry))
        arguments = self.parse("setup", "--apply", "--account-context", "personal", "--actor-role", "owner",
                               "--repo", "owner/repo", "--review-scope", "root", "--secret-target", "none",
                               "--local-secret-store", "none", "--env-history-reviewed", "yes",
                               "--rotation-decision", "not-applicable")
        applied = agent1.dispatch(self.project, self.defaults, arguments)
        self.assertFalse(applied["registration"]["changed"])
        self.assertEqual(memory.read_text(), "Existing private checkpoint\n")

    @REQUIRES_ANCHORED_FILES
    def test_setup_reconfiguration_is_previewed_and_sha_guarded(self):
        initial = self.parse("setup", "--apply", "--account-context", "personal", "--actor-role", "guest",
                             "--repo", "owner/repo", "--review-scope", "root", "--secret-target", "none",
                             "--local-secret-store", "none", "--env-history-reviewed", "yes",
                             "--rotation-decision", "needed")
        agent1.dispatch(self.project, self.defaults, initial)
        memory = self.project / ".SYSTEMX" / "AGENTS" / "agent.1" / "MEMORY.md"
        memory_before = memory.read_bytes()
        config = self.project / ".SYSTEMX" / "local" / "AGENT1-CONFIG.json"
        config_before = config.read_bytes()
        next_answers = ("--account-context", "enterprise", "--actor-role", "guest",
                        "--repo", "owner/repo", "--review-scope", "root",
                        "--secret-target", "repository", "--local-secret-store", "none",
                        "--env-history-reviewed", "yes", "--rotation-decision", "needed")
        preview = agent1.dispatch(self.project, self.defaults, self.parse("setup", *next_answers))
        self.assertFalse(preview["changed"])
        self.assertTrue(preview["applyRequired"])
        self.assertEqual(preview["config"]["githubActionsSecretTarget"], "none")
        self.assertEqual(preview["proposed"]["githubActionsSecretTarget"], "repository")
        self.assertEqual(config.read_bytes(), config_before)
        with self.assertRaisesRegex(ValueError, "guarded replacement"):
            agent1.dispatch(self.project, self.defaults, self.parse("setup", *next_answers, "--apply"))
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            agent1.dispatch(self.project, self.defaults,
                            self.parse("setup", *next_answers, "--apply", "--replace-existing",
                                       "--expect-sha256", "0" * 64))
        applied = agent1.dispatch(self.project, self.defaults,
                                  self.parse("setup", *next_answers, "--apply", "--replace-existing",
                                             "--expect-sha256", preview["existingSHA256"]))
        self.assertTrue(applied["changed"])
        self.assertEqual(agent1.status(self.project)["config"]["githubActionsSecretTarget"], "repository")
        self.assertEqual(memory.read_bytes(), memory_before)
        registry = json.loads((self.project / ".SYSTEMX" / "AGENTS" / "REGISTRY.json").read_text())
        self.assertEqual([item["id"] for item in registry["agents"]].count("agent.1"), 1)

    @REQUIRES_ANCHORED_FILES
    def test_child_systemxp_scope_and_complete_review_matrix(self):
        child = Path(self.scratch.name) / "child"
        child.mkdir()
        (child / ".SYSTEMXP").mkdir()
        (child / ".SYSTEMXP" / "START-HERE.md").write_text("Fixture\n")
        self.assertEqual(agent1._project(child / ".SYSTEMXP"), (child.resolve() / ".SYSTEMXP", child.resolve()))
        self.assertEqual(agent1._project(child), (child.resolve() / ".SYSTEMXP", child.resolve()))
        selected = agent1.questions(self.defaults, "all-in-one")
        answers = [{"id": question["id"], "result": "unknown", "evidence": []}
                   for category in selected["categories"] for question in category["questions"]]
        answers[0] = {"id": answers[0]["id"], "result": "fail", "evidence": ["proof/fixture.json"]}
        answer_path = child / "answers.json"
        answer_path.write_text(json.dumps({"answers": answers}))
        result = agent1.review_answers(child / ".SYSTEMXP", self.defaults, "answers.json")
        self.assertEqual(result["questionsAnswered"], 400)
        self.assertEqual(result["counts"]["fail"], 1)
        self.assertEqual(result["counts"]["unknown"], 399)
        self.assertEqual(result["evidenceAuthenticity"], "not_verified")
        self.assertEqual(result["overallVerdict"], "requires_review")

    def test_env_symlink_and_external_file_are_refused(self):
        external = Path(self.scratch.name) / "outside.env"
        external.write_text("API_KEY=synthetic\n")
        (self.project / ".env").symlink_to(external)
        with self.assertRaises(ValueError):
            agent1.env_inventory(self.project, ".env")
        report = agent1.assess(self.project, self.defaults)
        self.assertIn(".env", report["inventory"]["dotenvFileNames"])

    @REQUIRES_ANCHORED_FILES
    def test_parent_directory_symlink_is_refused_for_dotenv_operations(self):
        external = Path(self.scratch.name) / "external"
        external.mkdir()
        (external / ".env").write_text("TOKEN=synthetic\n")
        (self.project / "linked").symlink_to(external, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "linked"):
            agent1.env_inventory(self.project, "linked/.env")
        with self.assertRaisesRegex(ValueError, "linked"):
            agent1.dispatch(self.project, self.defaults,
                            self.parse("env-sanitize", "--env-file", "linked/.env", "--apply"))
        self.assertFalse((external / ".env.example").exists())

    @REQUIRES_ANCHORED_FILES
    def test_post_open_byte_limit_blocks_growth_past_initial_stat(self):
        (self.project / ".env").write_bytes(b"TOKEN=" + b"x" * 64)
        with patch.object(agent1, "MAX_ENV_BYTES", 32), \
                patch.object(agent1.os, "fstat", return_value=SimpleNamespace(st_mode=0o100600, st_size=0)):
            with self.assertRaisesRegex(ValueError, "one MiB limit"):
                agent1.env_inventory(self.project, ".env")

    @unittest.skipUnless(hasattr(os, "mkfifo") and agent1._secure_file_ops_available(),
                         "POSIX FIFO check requires anchored file operations")
    def test_fifo_substitution_is_rejected_without_waiting_for_writer(self):
        os.mkfifo(self.project / ".env")
        with self.assertRaisesRegex(ValueError, "regular file"):
            agent1.env_inventory(self.project, ".env")

    @unittest.skipUnless(agent1._secure_file_ops_available(), "POSIX directory handles required")
    def test_sanitizer_keeps_anchored_directory_when_name_is_swapped(self):
        nested = self.project / "nested"
        nested.mkdir()
        (nested / ".env").write_text("TOKEN=synthetic\n")
        external = Path(self.scratch.name) / "external"
        external.mkdir()
        original_read = agent1._read_regular_at
        swapped = False

        def swap_after_source_read(directory, name, **kwargs):
            nonlocal swapped
            result = original_read(directory, name, **kwargs)
            if name == ".env" and not swapped:
                swapped = True
                nested.rename(self.project / "moved")
                nested.symlink_to(external, target_is_directory=True)
            return result

        with patch.object(agent1, "_read_regular_at", side_effect=swap_after_source_read):
            agent1.dispatch(self.project, self.defaults,
                            self.parse("env-sanitize", "--env-file", "nested/.env", "--apply"))
        self.assertTrue(swapped)
        self.assertFalse((external / ".env.example").exists())
        self.assertTrue((self.project / "moved" / ".env.example").exists())

    def test_unsupported_file_handle_platform_fails_closed_for_dotenv(self):
        (self.project / ".env").write_text("TOKEN=synthetic\n")
        with patch.object(agent1, "_secure_file_ops_available", return_value=False), \
                patch("subprocess.run") as runner:
            with self.assertRaisesRegex(ValueError, "unavailable on this OS"):
                agent1.env_inventory(self.project, ".env")
            with self.assertRaisesRegex(ValueError, "unavailable on this OS"):
                agent1.dispatch(self.project, self.defaults,
                                self.parse("env-sanitize", "--env-file", ".env", "--apply"))
            with self.assertRaisesRegex(ValueError, "unavailable on this OS"):
                agent1.dispatch(self.project, self.defaults,
                                self.parse("env-migrate", "--env-file", ".env", "--repo", "owner/repo",
                                           "--name", "TOKEN", "--apply"))
            runner.assert_not_called()
        self.assertFalse((self.project / ".env.example").exists())

    @unittest.skipIf(agent1._secure_file_ops_available(),
                     "native unsupported-platform check requires Windows-style file handles")
    def test_native_unsupported_platform_refuses_file_backed_review_and_env(self):
        (self.project / ".env").write_text("TOKEN=synthetic\n")
        (self.project / "answers.json").write_text('{"answers":[]}\n')
        with self.assertRaisesRegex(ValueError, "unavailable on this OS"):
            agent1.env_inventory(self.project, ".env")
        with self.assertRaisesRegex(ValueError, "unavailable on this OS"):
            agent1.dispatch(self.project, self.defaults,
                            self.parse("env-sanitize", "--env-file", ".env", "--apply"))
        with self.assertRaisesRegex(ValueError, "unavailable on this OS"):
            agent1.review_answers(self.project, self.defaults, "answers.json")
        self.assertFalse((self.project / ".env.example").exists())

    def test_unsupported_handle_platform_keeps_metadata_first_run_but_refuses_reconfigure(self):
        initial = self.parse("setup", "--apply", "--account-context", "personal", "--actor-role", "owner",
                             "--repo", "owner/repo", "--review-scope", "root", "--secret-target", "none",
                             "--local-secret-store", "none", "--env-history-reviewed", "yes",
                             "--rotation-decision", "needed")
        with patch.object(agent1, "_secure_file_ops_available", return_value=False):
            result = agent1.dispatch(self.project, self.defaults, initial)
            self.assertTrue(result["configured"])
            self.assertEqual(agent1.status(self.project)["config"]["githubActionsSecretTarget"], "none")
            with self.assertRaisesRegex(ValueError, "unavailable on this OS"):
                agent1.dispatch(self.project, self.defaults,
                                self.parse("setup", "--account-context", "personal", "--actor-role", "owner",
                                           "--repo", "owner/repo", "--review-scope", "root",
                                           "--secret-target", "repository", "--local-secret-store", "none",
                                           "--env-history-reviewed", "yes", "--rotation-decision", "needed"))

    @REQUIRES_ANCHORED_FILES
    def test_secret_upload_requires_explicit_apply_and_hidden_terminal(self):
        (self.project / ".env").write_text("TOKEN=synthetic\n")
        setup_args = self.parse("setup", "--apply", "--account-context", "personal", "--actor-role", "owner",
                                "--repo", "owner/repo", "--review-scope", "root",
                                "--secret-target", "repository", "--local-secret-store", "none",
                                "--env-history-reviewed", "yes", "--rotation-decision", "not-applicable")
        agent1.dispatch(self.project, self.defaults, setup_args)
        args = self.parse("env-migrate", "--env-file", ".env", "--repo", "owner/repo",
                          "--name", "TOKEN", "--apply")
        with patch.object(sys.stdin, "isatty", return_value=False), patch("subprocess.run") as runner:
            with self.assertRaisesRegex(ValueError, "interactive terminal"):
                agent1.dispatch(self.project, self.defaults, args)
            self.assertFalse(any(call.args and call.args[0][:2] == ["gh", "secret"]
                                 for call in runner.call_args_list))

    @REQUIRES_ANCHORED_FILES
    def test_guest_with_verified_repo_admin_can_set_and_read_back_name_only(self):
        self.setup_secret_target(actor_role="guest")
        secret = "SYNTHETIC_HIDDEN_INPUT"
        commands = []

        def fake_run(command, **kwargs):
            commands.append((command, kwargs))
            if command[:3] == ["gh", "api", "user"]:
                return subprocess.CompletedProcess(command, 0, "guest-admin\n", "")
            if command[:3] == ["gh", "api", "repos/owner/repo"]:
                return subprocess.CompletedProcess(command, 0, "true\n", "")
            if command[:3] == ["gh", "secret", "set"]:
                self.assertEqual(kwargs.get("input"), secret)
                return subprocess.CompletedProcess(command, 0, "", "")
            if command[:3] == ["gh", "secret", "list"]:
                return subprocess.CompletedProcess(command, 0, '[{"name":"TOKEN"}]', "")
            self.fail(f"Unexpected command: {command}")

        args = self.parse("env-migrate", "--env-file", ".env", "--repo", "owner/repo",
                          "--name", "TOKEN", "--apply")
        with patch.object(sys.stdin, "isatty", return_value=True), \
                patch.object(sys.stderr, "isatty", return_value=True), \
                patch("shutil.which", return_value="/usr/bin/gh"), \
                patch("getpass.getpass", return_value=secret) as prompt, \
                patch("subprocess.run", side_effect=fake_run):
            result = agent1.dispatch(self.project, self.defaults, args)
        prompt.assert_called_once()
        self.assertEqual([command[:3] for command, _kwargs in commands],
                         [["gh", "api", "user"], ["gh", "api", "repos/owner/repo"],
                          ["gh", "secret", "set"], ["gh", "secret", "list"]])
        self.assertEqual(commands[1][0][-2:], ["--jq", ".permissions.admin"])
        self.assertEqual(commands[3][0][-2:], ["--json", "name"])
        self.assertTrue(result["providerAdminVerified"])
        self.assertEqual(result["metadataReadback"],
                         {"state": "verified", "scope": "repository", "name": "TOKEN"})
        self.assertFalse(result["valueVerified"])
        self.assertNotIn(secret, json.dumps(result))

    @REQUIRES_ANCHORED_FILES
    def test_environment_readback_failure_is_unknown_after_set(self):
        self.setup_secret_target(target="environment")
        commands = []

        def fake_run(command, **kwargs):
            commands.append(command)
            if command[:3] == ["gh", "api", "user"]:
                return subprocess.CompletedProcess(command, 0, "admin\n", "")
            if command[:3] == ["gh", "api", "repos/owner/repo"]:
                return subprocess.CompletedProcess(command, 0, "true\n", "")
            if command[:3] == ["gh", "secret", "set"]:
                return subprocess.CompletedProcess(command, 0, "", "")
            if command[:3] == ["gh", "secret", "list"]:
                return subprocess.CompletedProcess(command, 1, "", "unavailable")
            self.fail(f"Unexpected command: {command}")

        args = self.parse("env-migrate", "--env-file", ".env", "--repo", "owner/repo",
                          "--environment", "stage", "--name", "TOKEN", "--apply")
        with patch.object(sys.stdin, "isatty", return_value=True), \
                patch.object(sys.stderr, "isatty", return_value=True), \
                patch("shutil.which", return_value="/usr/bin/gh"), \
                patch("getpass.getpass", return_value="synthetic"), \
                patch("subprocess.run", side_effect=fake_run):
            result = agent1.dispatch(self.project, self.defaults, args)
        self.assertEqual(commands[2][-2:], ["--env", "stage"])
        self.assertEqual(commands[3][-4:], ["--env", "stage", "--json", "name"])
        self.assertTrue(result["secretSet"])
        self.assertEqual(result["metadataReadback"],
                         {"state": "unknown", "scope": "environment", "name": "TOKEN"})

    @REQUIRES_ANCHORED_FILES
    def test_false_missing_or_failed_admin_capability_stops_before_secret_prompt(self):
        self.setup_secret_target(actor_role="guest")
        args = self.parse("env-migrate", "--env-file", ".env", "--repo", "owner/repo",
                          "--name", "TOKEN", "--apply")
        for exit_code, answer in ((0, "false\n"), (0, "null\n"), (0, ""), (1, "true\n")):
            with self.subTest(exit_code=exit_code, answer=answer):
                commands = []

                def fake_run(command, **_kwargs):
                    commands.append(command)
                    if command[:3] == ["gh", "api", "user"]:
                        return subprocess.CompletedProcess(command, 0, "guest\n", "")
                    if command[:3] == ["gh", "api", "repos/owner/repo"]:
                        return subprocess.CompletedProcess(command, exit_code, answer, "")
                    self.fail(f"Secret command ran without verified admin: {command}")

                with patch.object(sys.stdin, "isatty", return_value=True), \
                        patch.object(sys.stderr, "isatty", return_value=True), \
                        patch("shutil.which", return_value="/usr/bin/gh"), \
                        patch("getpass.getpass") as prompt, \
                        patch("subprocess.run", side_effect=fake_run):
                    with self.assertRaisesRegex(ValueError, "admin capability could not be verified"):
                        agent1.dispatch(self.project, self.defaults, args)
                prompt.assert_not_called()
                self.assertEqual(len(commands), 2)


if __name__ == "__main__":
    unittest.main()
