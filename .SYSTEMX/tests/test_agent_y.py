"""Isolated contract tests for Agent Y's CLI handoff and owned PR lane.

The fixtures use a disposable Git repository and fake executables. No provider,
GitHub account, or network service is contacted by this suite.
"""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

import test_systemx

PROMPT_MARKER = "PRIVATE_CONTEXT_NOT_FOR_JOB_RECORDS_OR_PR_BODIES"


class AgentYTests(unittest.TestCase):
    setUp = test_systemx.SystemxTests.setUp
    assert_ok = test_systemx.SystemxTests.assert_ok

    def cli(self, *args, env=None):
        return subprocess.run([sys.executable, "-B", str(self.runner), *args],
                              cwd=self.temp.name, env=env, text=True,
                              capture_output=True, timeout=20)

    def value(self, *args, env=None):
        result = self.cli(*args, env=env)
        self.assert_ok(result)
        return json.loads(result.stdout[result.stdout.index("{"):])

    def rejected(self, *args, env=None):
        result = self.cli(*args, env=env)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        return result

    def records(self):
        return {path.relative_to(self.systemx).as_posix(): path.read_bytes()
                for path in self.systemx.rglob("*") if path.is_file()}

    def git(self, *args, cwd=None):
        result = subprocess.run(["git", *args], cwd=cwd or self.root,
                                text=True, capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout.strip()

    def git_state(self):
        return (self.git("show-ref"), self.git("worktree", "list", "--porcelain"),
                self.git("status", "--porcelain", "--untracked-files=all"))

    def init_repository(self):
        """A local committed fixture; remote operations stay inside tempdir."""
        self.git("init", "--initial-branch=main")
        self.git("config", "user.name", "Agent Y fixture")
        self.git("config", "user.email", "agent-y@example.invalid")
        (self.root / "app.txt").write_text("Original application\n", encoding="utf-8")
        self.prompt = self.root / "instructions.txt"
        self.prompt.write_text("Update app.txt and report the result. " + PROMPT_MARKER + "\n",
                               encoding="utf-8")
        self.git("add", ".SYSTEMX", "app.txt")
        self.git("add", "instructions.txt")
        self.git("commit", "-m", "Fixture base")
        base = self.git("rev-parse", "HEAD")
        self.origin = Path(self.temp.name) / "origin.git"
        self.git("init", "--bare", str(self.origin))
        self.git("remote", "add", "origin", str(self.origin))
        self.git("push", "--set-upstream", "origin", "main")
        self.git("symbolic-ref", "HEAD", "refs/heads/main", cwd=self.origin)
        self.git("fetch", "origin", "main")
        self.assertEqual(self.git("status", "--porcelain", "--untracked-files=all"), "")
        return base

    def ready_task(self, *, owner="agent.y"):
        self.value("roles-init", "--apply")
        result = self.cli("task-add", "--title", "Fixture change", "--owner", owner,
                          "--acceptance", "app.txt contains the approved change",
                          "--scope", "app.txt")
        self.assert_ok(result)
        self.assertIn("TASK-001", result.stdout)
        self.assert_ok(self.cli("task-set", "TASK-001", "--status", "in_progress",
                                "--next", "Run the bounded CLI handoff"))
        return self.init_repository()

    def prepare_args(self, *, provider="codex", branch="codex/agent-y/TASK-001-fixture",
                     allow_path="app.txt", prompt_file=None):
        return ("agent-y", "prepare", "--task", "TASK-001", "--provider", provider,
                "--repo", str(self.root), "--base", "main",
                "--prompt-file", str(prompt_file or self.prompt), "--allow-path", allow_path,
                "--branch", branch)

    def fake_path(self):
        folder = Path(self.temp.name) / "fake-tools"
        folder.mkdir(exist_ok=True)
        env = dict(os.environ)
        env["PATH"] = str(folder) + os.pathsep + env.get("PATH", "")
        env["TMPDIR"] = self.temp.name
        return folder, env

    @staticmethod
    def fake_executable(folder, name, body):
        path = folder / name
        path.write_text("#!/usr/bin/env python3\n" + body, encoding="utf-8")
        path.chmod(0o755)
        return path

    def fake_github_identity(self, folder):
        """Spoof identity discovery only; every Git mutation uses local origin."""
        real_git = shutil.which("git")
        self.assertIsNotNone(real_git)
        return self.fake_executable(
            folder, "git", "import subprocess, sys\n"
            "args = sys.argv[1:]\n"
            "if args[-3:] == ['remote', 'get-url', 'origin'] or "
            "args[-4:] == ['remote', 'get-url', '--push', 'origin']:\n"
            "    print('https://github.com/FixtureOrg/fixture-repo.git')\n"
            "else:\n"
            "    sys.exit(subprocess.call([" + repr(real_git) + ", *args]))\n")

    def fake_git_remote_race(self, folder, *, branch, replacement_oid, mode):
        """Move one local bare-origin ref at the controller's push boundary."""
        self.assertIn(mode, {"create", "delete"})
        real_git = shutil.which("git")
        self.assertIsNotNone(real_git)
        marker = Path(self.temp.name) / ("remote-race-" + mode)
        target_arg = ("HEAD:" if mode == "create" else "") + "refs/heads/" + branch
        body = (
            "import subprocess, sys\n"
            "from pathlib import Path\n"
            "args = sys.argv[1:]\n"
            "if args[-3:] == ['remote', 'get-url', 'origin'] or "
            "args[-4:] == ['remote', 'get-url', '--push', 'origin']:\n"
            "    print('https://github.com/FixtureOrg/fixture-repo.git')\n"
            "else:\n"
            "    marker = Path(" + repr(str(marker)) + ")\n"
            "    if " + repr(target_arg) + " in args and " +
            ("'--delete' in args" if mode == "delete" else "True") + " and not marker.exists():\n"
            "        subprocess.run([" + repr(real_git) + ", '--git-dir', " + repr(str(self.origin)) +
            ", 'update-ref', 'refs/heads/' + " + repr(branch) + ", " + repr(replacement_oid) +
            "], check=True)\n"
            "        marker.write_text('race injected')\n"
            "    sys.exit(subprocess.call([" + repr(real_git) + ", *args]))\n")
        self.fake_executable(folder, "git", body)
        return marker

    def fake_git_local_ref_race(self, folder, *, branch, replacement_oid):
        """Replace the local branch immediately before controller CAS deletion."""
        real_git = shutil.which("git")
        self.assertIsNotNone(real_git)
        marker = Path(self.temp.name) / "local-ref-race"
        body = (
            "import subprocess, sys\n"
            "from pathlib import Path\n"
            "args = sys.argv[1:]\n"
            "if args[-3:] == ['remote', 'get-url', 'origin'] or "
            "args[-4:] == ['remote', 'get-url', '--push', 'origin']:\n"
            "    print('https://github.com/FixtureOrg/fixture-repo.git')\n"
            "else:\n"
            "    marker = Path(" + repr(str(marker)) + ")\n"
            "    if 'update-ref' in args and '-d' in args and " + repr("refs/heads/" + branch) +
            " in args and not marker.exists():\n"
            "        subprocess.run([" + repr(real_git) + ", '-C', " + repr(str(self.root)) +
            ", 'update-ref', " + repr("refs/heads/" + branch) + ", " + repr(replacement_oid) +
            "], check=True)\n"
            "        marker.write_text('local ref race injected')\n"
            "    sys.exit(subprocess.call([" + repr(real_git) + ", *args]))\n")
        self.fake_executable(folder, "git", body)
        return marker

    def fake_gh(self, folder, *, fail_create_after_write=False):
        """Return a mutable fake PR state; all Git transport stays local."""
        real_git = shutil.which("git")
        self.assertIsNotNone(real_git)
        state = Path(self.temp.name) / "fake-gh-state.json"
        calls = Path(self.temp.name) / "fake-gh-calls.jsonl"
        body = (
            "import json, os, subprocess, sys\n"
            "from pathlib import Path\n"
            "args = sys.argv[1:]\n"
            "state_path = Path(" + repr(str(state)) + ")\n"
            "calls_path = Path(" + repr(str(calls)) + ")\n"
            "origin = Path(" + repr(str(self.origin)) + ")\n"
            "state = json.loads(state_path.read_text()) if state_path.exists() else {}\n"
            "body = Path(args[args.index('--body-file') + 1]).read_text() if '--body-file' in args else ''\n"
            "with calls_path.open('a') as output:\n"
            "    output.write(json.dumps({'argv': args, 'body': body, "
            "'GH_HOST': os.environ.get('GH_HOST', ''), 'GH_REPO': os.environ.get('GH_REPO', '')}) + '\\n')\n"
            "if args[:2] == ['repo', 'view']:\n"
            "    print(json.dumps({'nameWithOwner': 'FixtureOrg/fixture-repo'}))\n"
            "elif args[:2] == ['pr', 'list']:\n"
            "    print('[]')\n"
            "elif args[:2] == ['pr', 'create']:\n"
            "    branch = args[args.index('--head') + 1]\n"
            "    head = subprocess.check_output([" + repr(real_git) + ", '--git-dir', str(origin), "
            "'rev-parse', 'refs/heads/' + branch], text=True).strip()\n"
            "    state = {'number': 1, 'state': 'OPEN', 'headRefName': branch, 'headRefOid': head, "
            "'headRepositoryOwner': {'login': 'FixtureOrg'}, "
            "'headRepository': {'nameWithOwner': 'FixtureOrg/fixture-repo'}, "
            "'baseRepository': {'nameWithOwner': 'FixtureOrg/fixture-repo'}, 'isCrossRepository': False, "
            "'baseRefName': args[args.index('--base') + 1], "
            "'url': 'https://github.com/FixtureOrg/fixture-repo/pull/1', 'isDraft': True, 'mergedAt': None}\n"
            "    state_path.write_text(json.dumps(state))\n"
            "    if " + repr(fail_create_after_write) + ":\n"
            "        sys.exit(2)\n"
            "    print(state['url'])\n"
            "elif args[:2] == ['pr', 'view']:\n"
            "    print(json.dumps(state))\n"
            "elif args[:1] == ['api'] and len(args) == 2 and args[1].startswith('repos/FixtureOrg/fixture-repo/pulls/'):\n"
            "    print(json.dumps({'number': state.get('number'), "
            "'base': {'repo': {'full_name': (state.get('baseRepository') or {}).get('nameWithOwner')}}, "
            "'head': {'repo': {'full_name': (state.get('headRepository') or {}).get('nameWithOwner')}, "
            "'sha': state.get('headRefOid')}}))\n"
            "elif args[:2] == ['pr', 'ready']:\n"
            "    state['isDraft'] = False\n"
            "    state_path.write_text(json.dumps(state))\n"
            "elif args[:2] == ['pr', 'close']:\n"
            "    state['state'] = 'CLOSED'\n"
            "    state_path.write_text(json.dumps(state))\n"
            "else:\n"
            "    sys.exit(2)\n")
        self.fake_executable(folder, "gh", body)
        return state, calls

    def fake_editing_codex(self, folder, marker):
        """Simulate one bounded provider edit; Agent Y owns the local commit."""
        return self.fake_executable(
            folder, "codex", "import json, os, sys\n"
            "from pathlib import Path\n"
            "worktree = Path(sys.argv[sys.argv.index('-C') + 1])\n"
            "packet = sys.stdin.read()\n"
            "(worktree / 'app.txt').write_text('Provider-owned change\\n')\n"
            "Path(" + repr(str(marker)) + ").write_text(json.dumps({'argv': sys.argv[1:], "
            "'got_prompt': " + repr(PROMPT_MARKER) + " in packet}))\n")

    def test_role_activation_is_preview_first_and_keeps_jobs_blank(self):
        before = self.records()
        preview = self.value("roles-init")
        self.assertIn("agent.y", preview["register"])
        self.assertEqual(before, self.records())
        result = self.value("roles-init", "--apply")
        self.assertFalse(result["runtimeStarted"])
        registry = json.loads((self.systemx / "AGENTS/REGISTRY.json").read_text())
        self.assertIn("agent.y", [entry["id"] for entry in registry["agents"]])
        jobs = json.loads((self.systemx / "AGENTS/agent.y/JOBS.json").read_text())
        self.assertEqual(jobs["jobs"], [])
        self.assert_ok(self.cli("validate"))
        after = self.records()
        self.value("roles-init", "--apply")
        self.assertEqual(after, self.records())

    def test_root_and_child_private_sidecars_are_git_ignored(self):
        self.init_repository()
        for relative in (".SYSTEMX/local/agent-y/secret.json",
                         ".SYSTEMX/Projects/Project-A/.SYSTEMXP/local/agent-y/secret.json"):
            with self.subTest(relative=relative):
                self.git("check-ignore", "--quiet", "--", relative)

    def test_prepare_refuses_adopted_gitignore_that_exposes_sidecar_or_archive(self):
        # Installation preserves a customized .gitignore, including one that
        # predates Agent Y. A local sidecar must never be the first warning.
        (self.systemx / ".gitignore").write_text("# project-specific ignores\n", encoding="utf-8")
        self.ready_task()
        folder, env = self.fake_path()
        self.fake_executable(folder, "codex", "pass\n")
        before = self.records()
        rejected = self.rejected(*self.prepare_args(), "--apply", env=env)
        self.assertIn("not Git-ignored", rejected.stderr)
        self.assertEqual(before, self.records())
        self.assertEqual(json.loads((self.systemx / "AGENTS/agent.y/JOBS.json").read_text())["jobs"], [])
        self.assertFalse((self.systemx / "state/agent-y").exists())

    def test_prepare_requires_archive_ignore_even_when_sidecar_is_ignored(self):
        (self.systemx / ".gitignore").write_text("/state/agent-y/*.json\n", encoding="utf-8")
        self.ready_task()
        folder, env = self.fake_path()
        self.fake_executable(folder, "codex", "pass\n")
        rejected = self.rejected(*self.prepare_args(), "--apply", env=env)
        self.assertIn("archives", rejected.stderr)
        self.assertFalse((self.systemx / "state/agent-y").exists())

    def test_prepare_refuses_previously_tracked_private_agent_y_state(self):
        self.ready_task()
        legacy = self.systemx / "state/agent-y/legacy.json"
        legacy.parent.mkdir(parents=True)
        legacy.write_text("fixture only\n", encoding="utf-8")
        self.git("add", "-f", ".SYSTEMX/state/agent-y/legacy.json")
        self.git("commit", "-m", "Fixture force-added private state")
        self.git("push", "origin", "main")
        self.git("fetch", "origin", "main")
        folder, env = self.fake_path()
        self.fake_executable(folder, "codex", "pass\n")
        rejected = self.rejected(*self.prepare_args(), "--apply", env=env)
        self.assertIn("already Git-tracked", rejected.stderr)
        self.assertEqual(json.loads((self.systemx / "AGENTS/agent.y/JOBS.json").read_text())["jobs"], [])

    def test_existing_sidecar_refuses_later_ignore_removal(self):
        self.ready_task()
        folder, env = self.fake_path()
        self.fake_executable(folder, "codex", "pass\n")
        prepared = self.value(*self.prepare_args(), "--apply", env=env)
        sidecar = self.systemx / "state/agent-y" / (prepared["job"]["id"] + ".json")
        before = sidecar.read_bytes()
        (self.systemx / ".gitignore").write_text("# removed /state/ rule\n", encoding="utf-8")
        rejected = self.rejected("agent-y", "run", prepared["job"]["id"], env=env)
        self.assertIn("not Git-ignored", rejected.stderr)
        self.assertEqual(sidecar.read_bytes(), before)

    def test_prepare_preview_is_read_only_and_apply_records_one_owned_job(self):
        base = self.ready_task()
        folder, env = self.fake_path()
        marker = Path(self.temp.name) / "provider-was-run"
        self.fake_executable(folder, "codex", "from pathlib import Path\nPath(" +
                             repr(str(marker)) + ").write_text('run')\n")
        before = self.records()
        preview = self.value(*self.prepare_args(), env=env)
        self.assertFalse(preview["applied"])
        self.assertEqual(before, self.records())
        self.assertFalse(marker.exists())
        applied = self.value(*self.prepare_args(), "--apply", env=env)
        self.assertFalse(marker.exists())
        self.assertTrue(applied.get("applied"))
        jobs_text = (self.systemx / "AGENTS/agent.y/JOBS.json").read_text()
        jobs = json.loads(jobs_text)["jobs"]
        for private in (PROMPT_MARKER, str(self.root), str(self.prompt), str(folder)):
            self.assertNotIn(private, jobs_text)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["task"], "TASK-001")
        self.assertEqual(jobs[0]["provider"], "codex")
        self.assertEqual(jobs[0]["base"], "main")
        sidecar = self.systemx / "state" / "agent-y" / (applied["job"]["id"] + ".json")
        self.assertTrue(sidecar.is_file())
        self.assertEqual(sidecar.stat().st_mode & 0o077, 0)
        self.assertEqual(sidecar.parent.stat().st_mode & 0o077, 0)
        self.assertIn(str(self.root), sidecar.read_text())
        self.assertIn(str(self.prompt), sidecar.read_text())
        self.git("check-ignore", "--quiet", "--", sidecar.relative_to(self.root).as_posix())
        distributed = json.loads((self.systemx / "config/distribution.json").read_text())["files"]
        self.assertNotIn(sidecar.relative_to(self.systemx).as_posix(), distributed)
        self.assertEqual(self.git("rev-parse", "HEAD"), base)
        self.assert_ok(self.cli("agent-y", "validate"))

    def test_prepared_cli_identity_survives_path_substitution(self):
        self.ready_task()
        folder, env = self.fake_path()
        original_marker = Path(self.temp.name) / "prepared-provider-ran.json"
        original = self.fake_editing_codex(folder, original_marker)
        prepared = self.value(*self.prepare_args(), "--apply", env=env)
        identifier = prepared["job"]["id"]
        sidecar = json.loads((self.systemx / "state/agent-y" / (identifier + ".json")).read_text())
        self.assertEqual(sidecar["schemaVersion"], 2)
        self.assertEqual(sidecar["executable"]["path"], str(original.resolve()))
        self.assertEqual(sidecar["executable"]["sha256"], hashlib.sha256(original.read_bytes()).hexdigest())
        self.assertNotIn(str(original), (self.systemx / "AGENTS/agent.y/JOBS.json").read_text())
        replacement_folder = Path(self.temp.name) / "replacement-tools"
        replacement_folder.mkdir()
        substituted_marker = Path(self.temp.name) / "path-substitute-ran"
        self.fake_executable(replacement_folder, "codex", "from pathlib import Path\nPath(" +
                             repr(str(substituted_marker)) + ").write_text('unsafe provider ran')\n")
        env["PATH"] = str(replacement_folder) + os.pathsep + env["PATH"]
        result = self.value("agent-y", "run", identifier, "--apply", env=env)
        self.assertEqual(result["job"]["state"], "review_pending")
        self.assertTrue(original_marker.exists())
        self.assertFalse(substituted_marker.exists())

    def test_changed_prepared_executable_is_rejected_before_worktree_creation(self):
        self.ready_task()
        folder, env = self.fake_path()
        marker = Path(self.temp.name) / "changed-provider-ran"
        original = self.fake_executable(folder, "codex", "pass\n")
        prepared = self.value(*self.prepare_args(), "--apply", env=env)
        identifier = prepared["job"]["id"]
        self.fake_executable(folder, "codex", "from pathlib import Path\nPath(" +
                             repr(str(marker)) + ").write_text('changed code ran')\n")
        self.rejected("agent-y", "run", identifier, "--apply", env=env)
        self.assertFalse(marker.exists())
        self.assertFalse((Path(self.temp.name) / "systemx-agent-y").exists())
        self.assertEqual(json.loads((self.systemx / "AGENTS/agent.y/JOBS.json").read_text())
                         ["jobs"][0]["state"], "prepared")

    def test_configured_provider_cannot_switch_executable_after_prepare(self):
        self.ready_task()
        folder, env = self.fake_path()
        adapter = self.fake_executable(folder, "fixture-provider", "pass\n")
        prepared = self.value(*self.prepare_args(provider="configured"),
                              "--command", str(adapter), "--apply", env=env)
        other = self.fake_executable(folder, "different-provider", "pass\n")
        self.rejected("agent-y", "run", prepared["job"]["id"],
                      "--command", str(other), "--apply", env=env)
        self.assertFalse((Path(self.temp.name) / "systemx-agent-y").exists())
        self.assertEqual(json.loads((self.systemx / "AGENTS/agent.y/JOBS.json").read_text())
                         ["jobs"][0]["state"], "failed")

    def test_legacy_prepared_sidecar_fails_closed_and_can_be_abandoned_for_reprepare(self):
        self.ready_task()
        folder, env = self.fake_path()
        self.fake_executable(folder, "codex", "pass\n")
        prepared = self.value(*self.prepare_args(), "--apply", env=env)
        identifier = prepared["job"]["id"]
        sidecar_path = self.systemx / "state/agent-y" / (identifier + ".json")
        sidecar = json.loads(sidecar_path.read_text())
        sidecar.pop("executable")
        sidecar["schemaVersion"] = 1
        sidecar_path.write_text(json.dumps(sidecar))
        self.rejected("agent-y", "run", identifier, "--apply", env=env)
        self.assertFalse((Path(self.temp.name) / "systemx-agent-y").exists())
        self.assertEqual(json.loads((self.systemx / "AGENTS/agent.y/JOBS.json").read_text())
                         ["jobs"][0]["state"], "prepared")
        preview = self.value("agent-y", "abandon", identifier, "--reason", "CLI reviewed again", env=env)
        self.assertFalse(preview["applied"])
        retired = self.value("agent-y", "abandon", identifier, "--reason", "CLI reviewed again",
                             "--apply", env=env)
        self.assertEqual(retired["job"]["state"], "failed")
        self.assertFalse(retired["branchDeleted"])
        self.git("add", ".SYSTEMX")
        self.git("commit", "-m", "Retire old prepared handoff")
        self.git("push", "origin", "main")
        self.git("fetch", "origin", "main")
        replacement = self.value(*self.prepare_args(branch="codex/agent-y/TASK-001-new-attempt"),
                                 "--apply", env=env)
        self.assertNotEqual(replacement["job"]["id"], identifier)
        new_sidecar = self.systemx / "state/agent-y" / (replacement["job"]["id"] + ".json")
        self.assertEqual(json.loads(new_sidecar.read_text())["schemaVersion"], 2)

    def test_prepare_refuses_missing_provider_and_dirty_worktree(self):
        self.ready_task()
        folder, env = self.fake_path()
        missing = Path(self.temp.name) / "no-such-provider"
        before = self.records()
        self.rejected(*self.prepare_args(provider="configured"),
                      "--command", str(missing), "--apply", env=env)
        self.assertEqual(before, self.records())
        self.fake_executable(folder, "codex", "pass\n")
        before = self.records()
        self.rejected(*self.prepare_args(), "--open-draft-pr", "--apply", env=env)
        self.assertEqual(before, self.records())
        (self.root / "app.txt").write_text("Uncommitted user work\n", encoding="utf-8")
        before, refs = self.records(), self.git_state()
        self.rejected(*self.prepare_args(), "--apply", env=env)
        self.assertEqual(before, self.records())
        self.assertEqual(refs, self.git_state())
        self.assertEqual((self.root / "app.txt").read_text(), "Uncommitted user work\n")

    def test_configured_adapter_arguments_stay_out_of_public_job_ledger(self):
        self.ready_task()
        folder, env = self.fake_path()
        adapter = self.fake_executable(folder, "fixture-provider", "pass\n")
        env["AGENT_Y_TEST_SECRET"] = "PRIVATE_ENV_SENTINEL"
        private_arg = "PRIVATE_ADAPTER_ARGUMENT"
        prepared = self.value(*self.prepare_args(provider="configured"),
                              "--command", str(adapter), "--arg", private_arg, "--apply", env=env)
        public = (self.systemx / "AGENTS/agent.y/JOBS.json").read_text()
        for private in (str(self.root), str(self.prompt), str(adapter), private_arg,
                        PROMPT_MARKER, "PRIVATE_ENV_SENTINEL"):
            self.assertNotIn(private, public)
        sidecar = self.systemx / "state" / "agent-y" / (prepared["job"]["id"] + ".json")
        self.assertTrue(sidecar.is_file())
        self.assertEqual(sidecar.stat().st_mode & 0o077, 0)
        self.assertEqual(json.loads(sidecar.read_text())["command"], [])
        self.rejected("agent-y", "run", prepared["job"]["id"], "--command", str(adapter),
                      "--arg", private_arg, "--apply", env=env)
        self.assertIn(str(adapter), sidecar.read_text())
        self.assertIn(private_arg, sidecar.read_text())
        self.assertNotIn(private_arg, (self.systemx / "AGENTS/agent.y/JOBS.json").read_text())
        self.git("check-ignore", "--quiet", "--", sidecar.relative_to(self.root).as_posix())

    def test_prepare_refuses_wrong_owner_and_path_escape(self):
        self.ready_task(owner="agent.0")
        folder, env = self.fake_path()
        self.fake_executable(folder, "codex", "pass\n")
        before = self.records()
        self.rejected(*self.prepare_args(), "--apply", env=env)
        self.assertEqual(before, self.records())
        self.assert_ok(self.cli("task-set", "TASK-001", "--owner", "agent.y"))
        self.git("add", ".SYSTEMX")
        self.git("commit", "-m", "Assign Agent Y")
        self.git("push", "origin", "main")
        self.git("fetch", "origin", "main")
        before = self.records()
        self.rejected(*self.prepare_args(allow_path="../outside.txt"), "--apply", env=env)
        self.assertEqual(before, self.records())
        for branch in ("main", "-x", "codex/agent-y/TASK-001@{1}"):
            with self.subTest(branch=branch):
                before, refs = self.records(), self.git_state()
                self.rejected(*self.prepare_args(branch=branch), "--apply", env=env)
                self.assertEqual(before, self.records())
                self.assertEqual(refs, self.git_state())

    def test_prepare_refuses_prompt_outside_repo_or_following_symlink(self):
        self.ready_task()
        folder, env = self.fake_path()
        self.fake_executable(folder, "codex", "pass\n")
        outside = Path(self.temp.name) / "outside-instructions.txt"
        outside.write_text("Not an approved prompt source\n", encoding="utf-8")
        before = self.records()
        self.rejected(*self.prepare_args(prompt_file=outside), "--apply", env=env)
        self.assertEqual(before, self.records())
        link = self.root / "prompt-link.txt"
        link.symlink_to(outside)
        self.git("add", "prompt-link.txt")
        self.git("commit", "-m", "Add prompt symlink fixture")
        self.git("push", "origin", "main")
        self.git("fetch", "origin", "main")
        before = self.records()
        self.rejected(*self.prepare_args(prompt_file=link), "--apply", env=env)
        self.assertEqual(before, self.records())
        large = self.root / "large-instructions.txt"
        large.write_bytes(b"x" * 65537)
        self.git("add", "large-instructions.txt")
        self.git("commit", "-m", "Add oversized prompt fixture")
        self.git("push", "origin", "main")
        self.git("fetch", "origin", "main")
        before = self.records()
        self.rejected(*self.prepare_args(prompt_file=large), "--apply", env=env)
        self.assertEqual(before, self.records())

    def test_fake_cli_run_returns_reviewable_work_without_completing_task(self):
        self.ready_task()
        folder, env = self.fake_path()
        invocation = Path(self.temp.name) / "provider-invocation.json"
        secret_names = ("GH_TOKEN", "GITHUB_TOKEN", "COPILOT_GITHUB_TOKEN", "AGENT_Y_TEST_SECRET")
        for name in secret_names:
            env[name] = "sentinel-never-expose-to-provider"
        self.fake_executable(folder, "codex", "import json, os, sys\n"
                             "from pathlib import Path\n"
                             "worktree = Path(sys.argv[sys.argv.index('-C') + 1])\n"
                             "packet = sys.stdin.read()\n"
                             "(worktree / 'app.txt').write_text('Approved fixture change\\n')\n"
                             "Path(" + repr(str(invocation)) + ").write_text(json.dumps({'argv': sys.argv[1:], 'cwd': os.getcwd(), "
                             "'got_prompt': " + repr(PROMPT_MARKER) + " in packet, "
                             "'leaked': [name for name in " + repr(secret_names) + " if name in os.environ]}))\n")
        prepared = self.value(*self.prepare_args(), "--apply", env=env)
        identifier = prepared["job"]["id"]
        self.assertFalse(invocation.exists())
        preview = self.value("agent-y", "run", identifier, env=env)
        self.assertFalse(preview["applied"])
        self.assertFalse(invocation.exists())
        result = self.value("agent-y", "run", identifier, "--apply", env=env)
        self.assertTrue(invocation.exists())
        observed = json.loads(invocation.read_text())
        self.assertTrue(observed["got_prompt"])
        self.assertEqual(observed["leaked"], [])
        self.assertEqual(result["job"]["id"], identifier)
        self.assertEqual(result["job"]["state"], "review_pending")
        self.assertNotIn(str(self.root), (self.systemx / "AGENTS/agent.y/JOBS.json").read_text())
        self.assertNotIn(PROMPT_MARKER, (self.systemx / "AGENTS/agent.y/JOBS.json").read_text())
        task = json.loads((self.systemx / "WORK/TASKS.json").read_text())["tasks"][0]
        self.assertEqual(task["status"], "in_progress")
        self.assertEqual(task["owner"], "agent.y")
        self.assert_ok(self.cli("agent-y", "validate"))

    def test_out_of_scope_provider_edits_fail_without_publishing_or_task_acceptance(self):
        self.ready_task()
        folder, env = self.fake_path()
        self.fake_executable(folder, "codex", "import sys\n"
                             "from pathlib import Path\n"
                             "worktree = Path(sys.argv[sys.argv.index('-C') + 1])\n"
                             "sys.stdin.read()\n"
                             "(worktree / 'other.txt').write_text('Unapproved edit\\n')\n"
                             "(worktree / '.SYSTEMX/WORK/TASKS.json').write_text('tampered')\n")
        prepared = self.value(*self.prepare_args(), "--apply", env=env)
        self.rejected("agent-y", "run", prepared["job"]["id"], "--apply", env=env)
        jobs = json.loads((self.systemx / "AGENTS/agent.y/JOBS.json").read_text())["jobs"]
        self.assertEqual(jobs[0]["state"], "failed")
        self.assertEqual(self.git("ls-remote", "origin", "refs/heads/" + jobs[0]["branch"]), "")
        task = json.loads((self.systemx / "WORK/TASKS.json").read_text())["tasks"][0]
        self.assertEqual(task["status"], "in_progress")
        self.assertEqual(task["owner"], "agent.y")
        self.assert_ok(self.cli("agent-y", "validate"))

    def test_remote_base_drift_refuses_run_before_provider_starts(self):
        prepared_base = self.ready_task()
        folder, env = self.fake_path()
        marker = Path(self.temp.name) / "provider-ran-after-base-drift"
        self.fake_executable(folder, "codex", "from pathlib import Path\nPath(" +
                             repr(str(marker)) + ").write_text('ran')\n")
        prepared = self.value(*self.prepare_args(), "--apply", env=env)
        clone = Path(self.temp.name) / "external-clone"
        self.git("clone", str(self.origin), str(clone), cwd=self.temp.name)
        self.git("config", "user.name", "Concurrent fixture writer", cwd=clone)
        self.git("config", "user.email", "concurrent@example.invalid", cwd=clone)
        (clone / "new-remote-file.txt").write_text("Concurrent work\n", encoding="utf-8")
        self.git("add", "new-remote-file.txt", cwd=clone)
        self.git("commit", "-m", "Move remote main after Agent Y prepare", cwd=clone)
        moved_base = self.git("rev-parse", "HEAD", cwd=clone)
        self.git("push", "origin", "main", cwd=clone)
        self.assertNotEqual(moved_base, prepared_base)
        self.assertEqual(self.git("rev-parse", "refs/remotes/origin/main"), prepared_base)
        self.rejected("agent-y", "run", prepared["job"]["id"], "--apply", env=env)
        self.assertFalse(marker.exists())
        self.assertEqual(self.git("ls-remote", "origin", "refs/heads/" + prepared["job"]["branch"]), "")
        job = json.loads((self.systemx / "AGENTS/agent.y/JOBS.json").read_text())["jobs"][0]
        self.assertEqual(job["state"], "prepared")
        self.assertEqual(json.loads((self.systemx / "WORK/TASKS.json").read_text())["tasks"][0]["status"],
                         "in_progress")

    def test_prompt_packet_uses_verified_bytes_when_file_changes_later(self):
        self.ready_task()
        folder, env = self.fake_path()
        injected = Path(self.temp.name) / "prompt-mutated-after-read"
        new_marker = "CHANGED_AFTER_AGENT_Y_VERIFIED_PROMPT"
        real_git = shutil.which("git")
        self.assertIsNotNone(real_git)
        self.fake_executable(folder, "git", "import subprocess, sys\n"
                             "from pathlib import Path\n"
                             "args = sys.argv[1:]\n"
                             "marker = Path(" + repr(str(injected)) + ")\n"
                             "if 'worktree' in args and 'add' in args and not marker.exists():\n"
                             "    Path(" + repr(str(self.prompt)) + ").write_text(" + repr(new_marker + "\n") + ")\n"
                             "    marker.write_text('changed')\n"
                             "sys.exit(subprocess.call([" + repr(real_git) + ", *args]))\n")
        observation = Path(self.temp.name) / "captured-packet.json"
        self.fake_executable(folder, "codex", "import json, sys\n"
                             "from pathlib import Path\n"
                             "worktree = Path(sys.argv[sys.argv.index('-C') + 1])\n"
                             "packet = sys.stdin.read()\n"
                             "(worktree / 'app.txt').write_text('Safe captured prompt result\\n')\n"
                             "Path(" + repr(str(observation)) + ").write_text(json.dumps({'old': " +
                             repr(PROMPT_MARKER) + " in packet, 'new': " + repr(new_marker) + " in packet}))\n")
        prepared = self.value(*self.prepare_args(), "--apply", env=env)
        self.assertEqual(prepared["job"]["promptSha256"],
                         hashlib.sha256(self.prompt.read_bytes()).hexdigest())
        result = self.value("agent-y", "run", prepared["job"]["id"], "--apply", env=env)
        self.assertEqual(result["job"]["state"], "review_pending")
        self.assertTrue(injected.exists())
        self.assertEqual(self.prompt.read_text(), new_marker + "\n")
        self.assertEqual(json.loads(observation.read_text()), {"old": True, "new": False})

    def test_provider_created_commit_cannot_bypass_scope_diff(self):
        self.ready_task()
        folder, env = self.fake_path()
        self.fake_github_identity(folder)
        gh_state, _ = self.fake_gh(folder)
        marker = Path(self.temp.name) / "provider-made-unauthorized-commit"
        self.fake_executable(folder, "codex", "import subprocess, sys\n"
                             "from pathlib import Path\n"
                             "worktree = Path(sys.argv[sys.argv.index('-C') + 1])\n"
                             "sys.stdin.read()\n"
                             "(worktree / 'unapproved.txt').write_text('Unapproved committed content\\n')\n"
                             "subprocess.run(['git', '-C', str(worktree), 'add', 'unapproved.txt'], check=True)\n"
                             "subprocess.run(['git', '-C', str(worktree), 'commit', '-m', 'Provider bypass attempt'], check=True)\n"
                             "(worktree / 'app.txt').write_text('Allowed but after unauthorized commit\\n')\n"
                             "Path(" + repr(str(marker)) + ").write_text('provider returned success')\n")
        prepared = self.value(*self.prepare_args(), "--open-draft-pr", "--apply", env=env)
        self.rejected("agent-y", "run", prepared["job"]["id"], "--apply", env=env)
        self.assertTrue(marker.exists())
        self.assertFalse(gh_state.exists())
        self.assertEqual(self.git("ls-remote", "origin", "refs/heads/" + prepared["job"]["branch"]), "")
        job = json.loads((self.systemx / "AGENTS/agent.y/JOBS.json").read_text())["jobs"][0]
        self.assertEqual(job["state"], "failed")
        self.assertEqual(json.loads((self.systemx / "WORK/TASKS.json").read_text())["tasks"][0]["status"],
                         "in_progress")

    def test_task_reassignment_during_provider_run_blocks_commit_and_publication(self):
        base = self.ready_task()
        folder, env = self.fake_path()
        self.fake_github_identity(folder)
        gh_state, _ = self.fake_gh(folder)
        marker = Path(self.temp.name) / "provider-reassigned-task"
        self.fake_executable(folder, "codex", "import subprocess, sys\n"
                             "from pathlib import Path\n"
                             "worktree = Path(sys.argv[sys.argv.index('-C') + 1])\n"
                             "sys.stdin.read()\n"
                             "(worktree / 'app.txt').write_text('Change after lost task ownership\\n')\n"
                             "subprocess.run([sys.executable, '-B', " + repr(str(self.runner)) +
                             ", 'task-set', 'TASK-001', '--status', 'cancelled', '--owner', 'agent.0', "
                             "'--note', 'Owner cancelled while CLI was running'], check=True)\n"
                             "Path(" + repr(str(marker)) + ").write_text('reassigned')\n")
        prepared = self.value(*self.prepare_args(), "--open-draft-pr", "--apply", env=env)
        self.rejected("agent-y", "run", prepared["job"]["id"], "--apply", env=env)
        self.assertTrue(marker.exists())
        self.assertFalse(gh_state.exists())
        self.assertEqual(self.git("ls-remote", "origin", "refs/heads/" + prepared["job"]["branch"]), "")
        self.assertEqual(self.git("rev-parse", "refs/heads/" + prepared["job"]["branch"]), base)
        job = json.loads((self.systemx / "AGENTS/agent.y/JOBS.json").read_text())["jobs"][0]
        self.assertEqual(job["state"], "failed")
        task = json.loads((self.systemx / "WORK/TASKS.json").read_text())["tasks"][0]
        self.assertEqual(task["status"], "cancelled")
        self.assertEqual(task["owner"], "agent.0")

    def test_failed_pre_worktree_run_cannot_reuse_deterministic_job_id(self):
        self.ready_task()
        folder, env = self.fake_path()
        self.fake_executable(folder, "codex", "pass\n")
        prepared = self.value(*self.prepare_args(), "--apply", env=env)
        identifier = prepared["job"]["id"]
        # Passing configured-only flags to Codex fails after the run is claimed,
        # before Agent Y creates the worktree or any branch.
        self.rejected("agent-y", "run", identifier, "--command", "/does/not/exist", "--apply", env=env)
        self.assertEqual(json.loads((self.systemx / "AGENTS/agent.y/JOBS.json").read_text())["jobs"][0]["state"],
                         "failed")
        self.assertFalse((Path(self.temp.name) / "systemx-agent-y").exists())
        before = (self.systemx / "AGENTS/agent.y/JOBS.json").read_bytes()
        self.rejected(*self.prepare_args(), "--apply", env=env)
        self.assertEqual(before, (self.systemx / "AGENTS/agent.y/JOBS.json").read_bytes())
        self.assertEqual(len(json.loads(before)["jobs"]), 1)
        self.assert_ok(self.cli("agent-y", "validate"))

    def test_failed_unpublished_job_without_result_cannot_auto_delete_sole_branch(self):
        self.ready_task()
        folder, env = self.fake_path()
        self.fake_executable(folder, "codex", "import sys\nsys.stdin.read()\n")
        prepared = self.value(*self.prepare_args(), "--apply", env=env)
        identifier = prepared["job"]["id"]
        self.rejected("agent-y", "run", identifier, "--apply", env=env)
        job = json.loads((self.systemx / "AGENTS/agent.y/JOBS.json").read_text())["jobs"][0]
        self.assertEqual(job["state"], "failed")
        self.assertEqual(job["headOid"], "")
        sidecar = self.systemx / "state/agent-y" / (identifier + ".json")
        worktree = Path(json.loads(sidecar.read_text())["worktree"])
        self.assertTrue(worktree.is_dir())
        self.assert_ok(self.cli("task-set", "TASK-001", "--status", "cancelled",
                                "--note", "Owner cancelled the empty fixture run"))
        self.rejected("agent-y", "cleanup", identifier, "--apply", env=env)
        self.assertTrue(worktree.is_dir())
        self.assertEqual(self.git("rev-parse", "refs/heads/" + job["branch"]), job["baseOid"])
        self.assertEqual(self.git("ls-remote", "origin", "refs/heads/" + job["branch"]), "")

    def test_offline_draft_pr_is_owned_and_close_preserves_branch(self):
        self.ready_task()
        folder, env = self.fake_path()
        env["GH_HOST"] = "evil.example"
        env["GH_REPO"] = "OtherOrg/foreign-repo"
        self.fake_github_identity(folder)
        gh_state, gh_calls = self.fake_gh(folder)
        invocation = Path(self.temp.name) / "provider-ran.json"
        self.fake_editing_codex(folder, invocation)
        hook_marker = Path(self.temp.name) / "controller-ran-pre-push-hook"
        self.fake_executable(self.root / ".git/hooks", "pre-push",
                             "from pathlib import Path\nPath(" + repr(str(hook_marker)) +
                             ").write_text('unsafe hook ran')\n")
        prepared = self.value(*self.prepare_args(), "--open-draft-pr", "--apply", env=env)
        identifier = prepared["job"]["id"]
        planned_worktrees = Path(self.temp.name) / "systemx-agent-y"
        self.assertFalse(planned_worktrees.exists())
        self.assertFalse(self.value("agent-y", "run", identifier, env=env)["applied"])
        self.assertFalse(planned_worktrees.exists())
        self.assertFalse(invocation.exists())
        result = self.value("agent-y", "run", identifier, "--apply", env=env)
        self.assertTrue(invocation.exists())
        self.assertEqual(result["job"]["state"], "draft_pr")
        # Older completed channels must remain manageable without an executable
        # pin, even though an older prepared channel cannot start a new run.
        sidecar_path = self.systemx / "state/agent-y" / (identifier + ".json")
        sidecar = json.loads(sidecar_path.read_text())
        sidecar.pop("executable")
        sidecar["schemaVersion"] = 1
        sidecar_path.write_text(json.dumps(sidecar))
        self.assertFalse(hook_marker.exists())
        head = result["job"]["headOid"]
        self.assertEqual(self.git("ls-remote", "origin", "refs/heads/" + result["job"]["branch"]).split()[0], head)
        remote_pr = json.loads(gh_state.read_text())
        self.assertEqual(remote_pr["headRefOid"], head)
        self.assertEqual(remote_pr["baseRefName"], "main")
        self.assertTrue(remote_pr["isDraft"])
        self.assertNotIn(PROMPT_MARKER, gh_calls.read_text())
        self.assertNotIn(str(self.root), gh_calls.read_text())
        for call in map(json.loads, gh_calls.read_text().splitlines()):
            self.assertEqual(call["GH_HOST"], "github.com")
            self.assertEqual(call["GH_REPO"], "")
        task = json.loads((self.systemx / "WORK/TASKS.json").read_text())["tasks"][0]
        self.assertEqual(task["status"], "in_progress")
        self.rejected("agent-y", "pr-close", identifier, "--reason", "abandoned", "--apply", env=env)
        self.assertEqual(json.loads(gh_state.read_text())["state"], "OPEN")
        self.assert_ok(self.cli("task-set", "TASK-001", "--status", "cancelled",
                                "--note", "Owner cancelled this fixture"))
        clean_pr = json.loads(gh_state.read_text())
        for changed in (
                {"headRepository": {"nameWithOwner": "FixtureOrg/foreign-repo"}},
                {"baseRepository": {"nameWithOwner": "FixtureOrg/foreign-repo"}},
                {"headRefOid": result["job"]["baseOid"]}):
            with self.subTest(remote_change=changed):
                gh_state.write_text(json.dumps({**clean_pr, **changed}))
                self.rejected("agent-y", "pr-close", identifier,
                              "--reason", "Owner cancelled this fixture", env=env)
                gh_state.write_text(json.dumps(clean_pr))
        self.assertFalse(self.value("agent-y", "pr-close", identifier,
                                    "--reason", "Owner cancelled this fixture", env=env)["applied"])
        self.assertEqual(json.loads(gh_state.read_text())["state"], "OPEN")
        closed = self.value("agent-y", "pr-close", identifier,
                            "--reason", "Owner cancelled this fixture", "--apply", env=env)
        self.assertEqual(closed["job"]["state"], "closed")
        self.assertEqual(json.loads(gh_state.read_text())["state"], "CLOSED")
        self.assertEqual(self.git("ls-remote", "origin", "refs/heads/" + result["job"]["branch"]).split()[0], head)

    def test_pr_ready_reconciles_remote_success_after_local_save_failure(self):
        self.ready_task()
        folder, env = self.fake_path()
        self.fake_github_identity(folder)
        gh_state, gh_calls = self.fake_gh(folder)
        self.fake_editing_codex(folder, Path(self.temp.name) / "provider-ran.json")
        prepared = self.value(*self.prepare_args(), "--open-draft-pr", "--apply", env=env)
        identifier = prepared["job"]["id"]
        published = self.value("agent-y", "run", identifier, "--apply", env=env)
        head = published["job"]["headOid"]
        self.assert_ok(self.cli("task-set", "TASK-001", "--status", "needs_review",
                                "--evidence", "commit:" + head))
        self.assert_ok(self.cli("task-set", "TASK-001", "--status", "done", "--reviewer", "agent.0",
                                "--evidence", "reviewed-fixture"))
        remote_pr = json.loads(gh_state.read_text())
        remote_pr["isDraft"] = False
        gh_state.write_text(json.dumps(remote_pr))
        calls_before = gh_calls.read_text()
        ready = self.value("agent-y", "pr-ready", identifier, "--apply", env=env)
        self.assertEqual(ready["job"]["state"], "ready")
        new_calls = gh_calls.read_text()[len(calls_before):]
        self.assertFalse(any(json.loads(line)["argv"][:2] == ["pr", "ready"]
                             for line in new_calls.splitlines()))

    def test_pr_ready_refuses_stale_remote_base_without_changing_pr(self):
        prepared_base = self.ready_task()
        folder, env = self.fake_path()
        self.fake_github_identity(folder)
        gh_state, gh_calls = self.fake_gh(folder)
        self.fake_editing_codex(folder, Path(self.temp.name) / "provider-ran.json")
        prepared = self.value(*self.prepare_args(), "--open-draft-pr", "--apply", env=env)
        identifier = prepared["job"]["id"]
        published = self.value("agent-y", "run", identifier, "--apply", env=env)
        head = published["job"]["headOid"]
        self.assert_ok(self.cli("task-set", "TASK-001", "--status", "needs_review",
                                "--evidence", "commit:" + head))
        self.assert_ok(self.cli("task-set", "TASK-001", "--status", "done", "--reviewer", "agent.0",
                                "--evidence", "reviewed-fixture"))
        self.assertFalse(self.value("agent-y", "pr-ready", identifier, env=env)["applied"])

        clone = Path(self.temp.name) / "external-clone"
        self.git("clone", str(self.origin), str(clone), cwd=self.temp.name)
        self.git("config", "user.name", "Concurrent fixture writer", cwd=clone)
        self.git("config", "user.email", "concurrent@example.invalid", cwd=clone)
        (clone / "new-remote-file.txt").write_text("Concurrent work\n", encoding="utf-8")
        self.git("add", "new-remote-file.txt", cwd=clone)
        self.git("commit", "-m", "Move remote main after Agent Y draft", cwd=clone)
        moved_base = self.git("rev-parse", "HEAD", cwd=clone)
        self.git("push", "origin", "main", cwd=clone)
        self.assertNotEqual(moved_base, prepared_base)
        self.assertEqual(self.git("rev-parse", "refs/remotes/origin/main"), prepared_base)
        calls_before = gh_calls.read_text()
        for apply in ((), ("--apply",)):
            rejected = self.rejected("agent-y", "pr-ready", identifier, *apply, env=env)
            self.assertIn("Remote base no longer matches", rejected.stderr)
        self.assertFalse(any(json.loads(line)["argv"][:2] == ["pr", "ready"]
                             for line in gh_calls.read_text()[len(calls_before):].splitlines()))
        self.assertTrue(json.loads(gh_state.read_text())["isDraft"])
        job = json.loads((self.systemx / "AGENTS/agent.y/JOBS.json").read_text())["jobs"][0]
        self.assertEqual(job["state"], "draft_pr")

    def test_pr_ready_rechecks_base_under_lock_before_gh_mutation(self):
        self.ready_task()
        folder, env = self.fake_path()
        self.fake_github_identity(folder)
        gh_state, gh_calls = self.fake_gh(folder)
        self.fake_editing_codex(folder, Path(self.temp.name) / "provider-ran.json")
        prepared = self.value(*self.prepare_args(), "--open-draft-pr", "--apply", env=env)
        identifier = prepared["job"]["id"]
        published = self.value("agent-y", "run", identifier, "--apply", env=env)
        head = published["job"]["headOid"]
        self.assert_ok(self.cli("task-set", "TASK-001", "--status", "needs_review",
                                "--evidence", "commit:" + head))
        self.assert_ok(self.cli("task-set", "TASK-001", "--status", "done", "--reviewer", "agent.0",
                                "--evidence", "reviewed-fixture"))
        clone = Path(self.temp.name) / "external-clone"
        self.git("clone", str(self.origin), str(clone), cwd=self.temp.name)
        self.git("config", "user.name", "Concurrent fixture writer", cwd=clone)
        self.git("config", "user.email", "concurrent@example.invalid", cwd=clone)
        (clone / "new-remote-file.txt").write_text("Concurrent work\n", encoding="utf-8")
        self.git("add", "new-remote-file.txt", cwd=clone)
        self.git("commit", "-m", "Prepare concurrent base advance", cwd=clone)
        moved_base = self.git("rev-parse", "HEAD", cwd=clone)
        self.git("push", "origin", "HEAD:refs/heads/concurrent-candidate", cwd=clone)
        real_git = shutil.which("git")
        self.assertIsNotNone(real_git)
        reads = Path(self.temp.name) / "base-reads"
        body = (
            "import subprocess, sys\nfrom pathlib import Path\n"
            "args = sys.argv[1:]\n"
            "if args[-3:] == ['remote', 'get-url', 'origin'] or "
            "args[-4:] == ['remote', 'get-url', '--push', 'origin']:\n"
            "    print('https://github.com/FixtureOrg/fixture-repo.git')\n"
            "else:\n"
            "    marker = Path(" + repr(str(reads)) + ")\n"
            "    if args[-4:] == ['ls-remote', '--heads', 'origin', 'refs/heads/main']:\n"
            "        count = int(marker.read_text()) if marker.exists() else 0\n"
            "        marker.write_text(str(count + 1))\n"
            "        if count == 1:\n"
            "            subprocess.run([" + repr(real_git) + ", '--git-dir', " + repr(str(self.origin)) +
            ", 'update-ref', 'refs/heads/main', " + repr(moved_base) + "], check=True)\n"
            "    sys.exit(subprocess.call([" + repr(real_git) + ", *args]))\n")
        self.fake_executable(folder, "git", body)
        calls_before = gh_calls.read_text()
        rejected = self.rejected("agent-y", "pr-ready", identifier, "--apply", env=env)
        self.assertIn("Remote base no longer matches", rejected.stderr)
        self.assertEqual(reads.read_text(), "2")
        self.assertFalse(any(json.loads(line)["argv"][:2] == ["pr", "ready"]
                             for line in gh_calls.read_text()[len(calls_before):].splitlines()))
        self.assertTrue(json.loads(gh_state.read_text())["isDraft"])
        job = json.loads((self.systemx / "AGENTS/agent.y/JOBS.json").read_text())["jobs"][0]
        self.assertEqual(job["state"], "draft_pr")

    def test_pr_close_reconciles_remote_success_after_local_save_failure(self):
        self.ready_task()
        folder, env = self.fake_path()
        self.fake_github_identity(folder)
        gh_state, gh_calls = self.fake_gh(folder)
        self.fake_editing_codex(folder, Path(self.temp.name) / "provider-ran.json")
        prepared = self.value(*self.prepare_args(), "--open-draft-pr", "--apply", env=env)
        identifier = prepared["job"]["id"]
        published = self.value("agent-y", "run", identifier, "--apply", env=env)
        branch, head = published["job"]["branch"], published["job"]["headOid"]
        self.assert_ok(self.cli("task-set", "TASK-001", "--status", "cancelled",
                                "--note", "Owner cancelled this PR"))
        remote_pr = json.loads(gh_state.read_text())
        remote_pr["state"] = "CLOSED"
        gh_state.write_text(json.dumps(remote_pr))
        calls_before = gh_calls.read_text()
        closed = self.value("agent-y", "pr-close", identifier,
                            "--reason", "Owner cancelled this PR", "--apply", env=env)
        self.assertEqual(closed["job"]["state"], "closed")
        new_calls = gh_calls.read_text()[len(calls_before):]
        self.assertFalse(any(json.loads(line)["argv"][:2] == ["pr", "close"]
                             for line in new_calls.splitlines()))
        self.assertEqual(self.git("ls-remote", "origin", "refs/heads/" + branch).split()[0], head)

    def test_draft_branch_create_lease_refuses_remote_race(self):
        base = self.ready_task()
        folder, env = self.fake_path()
        branch = "codex/agent-y/TASK-001-fixture"
        race = self.fake_git_remote_race(folder, branch=branch, replacement_oid=base, mode="create")
        gh_state, _ = self.fake_gh(folder)
        self.fake_editing_codex(folder, Path(self.temp.name) / "provider-ran.json")
        prepared = self.value(*self.prepare_args(branch=branch), "--open-draft-pr", "--apply", env=env)
        self.rejected("agent-y", "run", prepared["job"]["id"], "--apply", env=env)
        self.assertTrue(race.exists())
        self.assertFalse(gh_state.exists())
        self.assertEqual(self.git("ls-remote", "origin", "refs/heads/" + branch).split()[0], base)
        job = json.loads((self.systemx / "AGENTS/agent.y/JOBS.json").read_text())["jobs"][0]
        self.assertEqual(job["state"], "failed")
        self.assertEqual(json.loads((self.systemx / "WORK/TASKS.json").read_text())["tasks"][0]["status"],
                         "in_progress")

    def test_ambiguous_gh_create_failure_preserves_published_branch_and_worktree(self):
        self.ready_task()
        folder, env = self.fake_path()
        self.fake_github_identity(folder)
        gh_state, gh_calls = self.fake_gh(folder, fail_create_after_write=True)
        self.fake_editing_codex(folder, Path(self.temp.name) / "provider-ran.json")
        prepared = self.value(*self.prepare_args(), "--open-draft-pr", "--apply", env=env)
        identifier, branch = prepared["job"]["id"], prepared["job"]["branch"]
        self.rejected("agent-y", "run", identifier, "--apply", env=env)
        self.assertTrue(gh_state.is_file())
        remote = json.loads(gh_state.read_text())
        self.assertEqual(remote["headRefName"], branch)
        self.assertEqual(self.git("ls-remote", "origin", "refs/heads/" + branch).split()[0],
                         remote["headRefOid"])
        job = json.loads((self.systemx / "AGENTS/agent.y/JOBS.json").read_text())["jobs"][0]
        self.assertEqual(job["state"], "failed")
        sidecar = self.systemx / "state/agent-y" / (identifier + ".json")
        self.assertTrue(Path(json.loads(sidecar.read_text())["worktree"]).is_dir())
        self.assertEqual(json.loads((self.systemx / "WORK/TASKS.json").read_text())["tasks"][0]["status"],
                         "in_progress")
        calls = [json.loads(line)["argv"] for line in gh_calls.read_text().splitlines()]
        self.assertEqual(sum(args[:2] == ["pr", "create"] for args in calls), 1)
        self.rejected(*self.prepare_args(), "--open-draft-pr", "--apply", env=env)
        self.assertEqual(sum(args[:2] == ["pr", "create"] for args in calls), 1)

    def test_pr_branch_delete_lease_refuses_head_moved_at_push_boundary(self):
        base = self.ready_task()
        folder, env = self.fake_path()
        self.fake_github_identity(folder)
        gh_state, _ = self.fake_gh(folder)
        self.fake_editing_codex(folder, Path(self.temp.name) / "provider-ran.json")
        prepared = self.value(*self.prepare_args(), "--open-draft-pr", "--apply", env=env)
        identifier = prepared["job"]["id"]
        result = self.value("agent-y", "run", identifier, "--apply", env=env)
        branch, head = result["job"]["branch"], result["job"]["headOid"]
        self.assert_ok(self.cli("task-set", "TASK-001", "--status", "needs_review",
                                "--evidence", "commit:" + head))
        self.assert_ok(self.cli("task-set", "TASK-001", "--status", "done",
                                "--reviewer", "agent.0", "--evidence", "reviewed-fixture"))
        remote_pr = json.loads(gh_state.read_text())
        remote_pr.update(state="MERGED", isDraft=False, mergedAt="2026-01-01T00:00:00Z")
        gh_state.write_text(json.dumps(remote_pr))
        race = self.fake_git_remote_race(folder, branch=branch, replacement_oid=base, mode="delete")
        failed = self.rejected("agent-y", "pr-cleanup", identifier, "--apply", env=env)
        self.assertTrue(race.exists(), failed.stdout + failed.stderr)
        self.assertEqual(self.git("ls-remote", "origin", "refs/heads/" + branch).split()[0], base)
        self.assertNotEqual(base, head)
        self.assertEqual(json.loads((self.systemx / "AGENTS/agent.y/JOBS.json").read_text())["jobs"][0]["state"],
                         "draft_pr")
        sidecar = self.systemx / "state/agent-y" / (identifier + ".json")
        self.assertTrue(Path(json.loads(sidecar.read_text())["worktree"]).is_dir())

    def test_merged_cleanup_local_ref_delete_uses_expected_oid(self):
        base = self.ready_task()
        folder, env = self.fake_path()
        self.fake_github_identity(folder)
        gh_state, _ = self.fake_gh(folder)
        self.fake_editing_codex(folder, Path(self.temp.name) / "provider-ran.json")
        prepared = self.value(*self.prepare_args(), "--open-draft-pr", "--apply", env=env)
        identifier = prepared["job"]["id"]
        result = self.value("agent-y", "run", identifier, "--apply", env=env)
        branch, head = result["job"]["branch"], result["job"]["headOid"]
        self.assertNotEqual(head, base)
        self.assert_ok(self.cli("task-set", "TASK-001", "--status", "needs_review",
                                "--evidence", "commit:" + head))
        self.assert_ok(self.cli("task-set", "TASK-001", "--status", "done", "--owner", "agent.0",
                                "--reviewer", "agent.0", "--evidence", "reviewed-fixture"))
        remote_pr = json.loads(gh_state.read_text())
        remote_pr.update(state="MERGED", isDraft=False, mergedAt="2026-01-01T00:00:00Z")
        gh_state.write_text(json.dumps(remote_pr))
        race = self.fake_git_local_ref_race(folder, branch=branch, replacement_oid=base)
        self.rejected("agent-y", "pr-cleanup", identifier, "--apply", env=env)
        self.assertTrue(race.exists())
        self.assertEqual(self.git("rev-parse", "refs/heads/" + branch), base)
        archive = self.systemx / "state/agent-y/archives" / (identifier + ".bundle")
        self.assertTrue(archive.is_file())
        self.git("bundle", "verify", str(archive))
        self.assertEqual(json.loads((self.systemx / "AGENTS/agent.y/JOBS.json").read_text())["jobs"][0]["state"],
                         "draft_pr")

    def test_accepted_merged_pr_cleanup_keeps_verified_private_bundle(self):
        self.ready_task()
        folder, env = self.fake_path()
        self.fake_github_identity(folder)
        gh_state, _ = self.fake_gh(folder)
        self.fake_editing_codex(folder, Path(self.temp.name) / "provider-ran.json")
        prepared = self.value(*self.prepare_args(), "--open-draft-pr", "--apply", env=env)
        identifier = prepared["job"]["id"]
        published = self.value("agent-y", "run", identifier, "--apply", env=env)
        branch, head = published["job"]["branch"], published["job"]["headOid"]
        self.assert_ok(self.cli("task-set", "TASK-001", "--status", "needs_review",
                                "--evidence", "commit:" + head))
        self.assert_ok(self.cli("task-set", "TASK-001", "--status", "done", "--owner", "agent.0",
                                "--reviewer", "agent.0", "--evidence", "reviewed-fixture"))
        remote_pr = json.loads(gh_state.read_text())
        remote_pr.update(state="MERGED", isDraft=False, mergedAt="2026-01-01T00:00:00Z")
        gh_state.write_text(json.dumps(remote_pr))
        archive = self.systemx / "state/agent-y/archives" / (identifier + ".bundle")
        self.assertFalse(self.value("agent-y", "pr-cleanup", identifier, env=env)["applied"])
        self.assertFalse(archive.exists())
        result = self.value("agent-y", "pr-cleanup", identifier, "--apply", env=env)
        self.assertEqual(result["job"]["state"], "merged")
        self.assertTrue(result["remoteBranchDeleted"])
        self.assertEqual(self.git("ls-remote", "origin", "refs/heads/" + branch), "")
        self.assertTrue(archive.is_file())
        self.assertEqual(archive.stat().st_mode & 0o077, 0)
        self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(), result["archiveSha256"])
        self.git("bundle", "verify", str(archive))
        self.git("check-ignore", "--quiet", "--", archive.relative_to(self.root).as_posix())
        local_ref = subprocess.run(["git", "show-ref", "--verify", "--quiet", "refs/heads/" + branch],
                                   cwd=self.root, text=True, capture_output=True)
        self.assertNotEqual(local_ref.returncode, 0)

    def test_merged_cleanup_preserves_ignored_worktree_file(self):
        self.ready_task()
        folder, env = self.fake_path()
        self.fake_github_identity(folder)
        gh_state, _ = self.fake_gh(folder)
        self.fake_editing_codex(folder, Path(self.temp.name) / "provider-ran.json")
        prepared = self.value(*self.prepare_args(), "--open-draft-pr", "--apply", env=env)
        identifier = prepared["job"]["id"]
        published = self.value("agent-y", "run", identifier, "--apply", env=env)
        branch, head = published["job"]["branch"], published["job"]["headOid"]
        sidecar = self.systemx / "state/agent-y" / (identifier + ".json")
        worktree = Path(json.loads(sidecar.read_text())["worktree"])
        ignored = worktree / ".SYSTEMX/local/user-notes.txt"
        ignored.parent.mkdir(parents=True, exist_ok=True)
        ignored.write_bytes(b"User material the controller must preserve\n")
        self.assertEqual(self.git("status", "--porcelain", "--untracked-files=all", cwd=worktree), "")
        self.assertIn(".SYSTEMX/local/", self.git("status", "--porcelain=v1", "--ignored=matching",
                                                  "--untracked-files=all", cwd=worktree))
        self.assert_ok(self.cli("task-set", "TASK-001", "--status", "needs_review",
                                "--evidence", "commit:" + head))
        self.assert_ok(self.cli("task-set", "TASK-001", "--status", "done", "--owner", "agent.0",
                                "--reviewer", "agent.0", "--evidence", "reviewed-fixture"))
        remote_pr = json.loads(gh_state.read_text())
        remote_pr.update(state="MERGED", isDraft=False, mergedAt="2026-01-01T00:00:00Z")
        gh_state.write_text(json.dumps(remote_pr))
        self.rejected("agent-y", "pr-cleanup", identifier, env=env)
        self.rejected("agent-y", "pr-cleanup", identifier, "--apply", env=env)
        self.assertEqual(ignored.read_bytes(), b"User material the controller must preserve\n")
        self.assertEqual(self.git("ls-remote", "origin", "refs/heads/" + branch).split()[0], head)
        self.assertEqual(self.git("rev-parse", "refs/heads/" + branch), head)
        self.assertEqual(json.loads((self.systemx / "AGENTS/agent.y/JOBS.json").read_text())
                         ["jobs"][0]["state"], "draft_pr")
        self.assertFalse((self.systemx / "state/agent-y/archives" / (identifier + ".bundle")).exists())

    def test_merged_cleanup_rechecks_ignored_files_after_remote_delete(self):
        self.ready_task()
        folder, env = self.fake_path()
        self.fake_github_identity(folder)
        gh_state, _ = self.fake_gh(folder)
        self.fake_editing_codex(folder, Path(self.temp.name) / "provider-ran.json")
        prepared = self.value(*self.prepare_args(), "--open-draft-pr", "--apply", env=env)
        identifier = prepared["job"]["id"]
        published = self.value("agent-y", "run", identifier, "--apply", env=env)
        branch, head = published["job"]["branch"], published["job"]["headOid"]
        sidecar = self.systemx / "state/agent-y" / (identifier + ".json")
        worktree = Path(json.loads(sidecar.read_text())["worktree"])
        ignored = worktree / ".SYSTEMX/local/late-output.txt"
        marker = Path(self.temp.name) / "late-ignored-file-created"
        self.assert_ok(self.cli("task-set", "TASK-001", "--status", "needs_review",
                                "--evidence", "commit:" + head))
        self.assert_ok(self.cli("task-set", "TASK-001", "--status", "done", "--owner", "agent.0",
                                "--reviewer", "agent.0", "--evidence", "reviewed-fixture"))
        remote_pr = json.loads(gh_state.read_text())
        remote_pr.update(state="MERGED", isDraft=False, mergedAt="2026-01-01T00:00:00Z")
        gh_state.write_text(json.dumps(remote_pr))
        real_git = shutil.which("git")
        self.assertIsNotNone(real_git)
        self.fake_executable(folder, "git",
                             "import subprocess, sys\n"
                             "from pathlib import Path\n"
                             "args = sys.argv[1:]\n"
                             "if args[-3:] == ['remote', 'get-url', 'origin'] or "
                             "args[-4:] == ['remote', 'get-url', '--push', 'origin']:\n"
                             "    print('https://github.com/FixtureOrg/fixture-repo.git')\n"
                             "else:\n"
                             "    code = subprocess.call([" + repr(real_git) + ", *args])\n"
                             "    marker = Path(" + repr(str(marker)) + ")\n"
                             "    if code == 0 and 'push' in args and '--delete' in args and not marker.exists():\n"
                             "        ignored = Path(" + repr(str(ignored)) + ")\n"
                             "        ignored.parent.mkdir(parents=True, exist_ok=True)\n"
                             "        ignored.write_text('Late provider output\\n')\n"
                             "        marker.write_text('created')\n"
                             "    sys.exit(code)\n")
        self.rejected("agent-y", "pr-cleanup", identifier, "--apply", env=env)
        self.assertTrue(marker.exists())
        self.assertEqual(ignored.read_text(), "Late provider output\n")
        self.assertEqual(self.git("ls-remote", "origin", "refs/heads/" + branch), "")
        self.assertEqual(self.git("rev-parse", "refs/heads/" + branch), head)
        self.assertTrue((self.systemx / "state/agent-y/archives" / (identifier + ".bundle")).is_file())
        self.assertEqual(json.loads((self.systemx / "AGENTS/agent.y/JOBS.json").read_text())
                         ["jobs"][0]["state"], "draft_pr")
