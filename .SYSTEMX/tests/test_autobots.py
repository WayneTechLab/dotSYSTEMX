"""AUTOBOT bounded, opt-in context and immutable-response behavior."""

from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import shutil
import unittest
from unittest.mock import patch

import test_systemx


class AutobotTests(unittest.TestCase):
    setUp = test_systemx.SystemxTests.setUp
    run_cli = test_systemx.SystemxTests.run_cli
    assert_ok = test_systemx.SystemxTests.assert_ok

    def value(self, *args):
        result = self.run_cli(*args)
        self.assert_ok(result)
        return json.loads(result.stdout[result.stdout.index("{"):])

    def rejected(self, *args):
        result = self.run_cli(*args)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        return result

    def files(self, root=None):
        root = root or self.systemx
        return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}

    def init(self):
        return self.value("autobot", "init", "--apply")

    def request(self, *extra, apply=True):
        return self.value("autobot", "request", "--caller", "agent.0", "--purpose", "Resolve interface tokens",
                          "--input-revision", "revision-1", "--bot", "autobot.design", *extra,
                          *(["--apply"] if apply else []))

    def completion(self, identifier, *extra, apply=True):
        return self.value("autobot", "complete", identifier, "--summary", "Reference accepted layout evidence",
                          "--response-revision", "response-1", "--evidence", "fixture/original-evidence", *extra,
                          *(["--apply"] if apply else []))

    def test_public_seed_has_ten_slots_and_no_registered_alpha_or_requests(self):
        catalog = self.value("autobot", "list")["catalog"]
        self.assertEqual(catalog["maximum"], 10)
        self.assertEqual(catalog["coordinator"], "agent.a")
        self.assertEqual(len(catalog["bots"]), 10)
        self.assertEqual(catalog["bots"][0]["file"], "AUTOBOT/Design.MD")
        self.assertEqual(catalog["bots"][-1]["file"], "AUTOBOT/Archive.MD")
        self.assertEqual(json.loads((self.systemx / "AGENTS/REGISTRY.json").read_text())["agents"][0]["id"], "agent.0")
        self.assertEqual(len(json.loads((self.systemx / "AGENTS/REGISTRY.json").read_text())["agents"]), 1)
        self.assertEqual(self.value("agent-a", "status")["total"], 0)
        self.rejected("autobot", "request", "--caller", "agent.0", "--purpose", "fixture",
                      "--input-revision", "r1", "--bot", "autobot.design", "--apply")

    def test_init_is_previewed_preserving_idempotent_and_logged(self):
        private = self.systemx / "AUTOBOT/Brand.MD"
        private.write_text("Accepted private project brand\n")
        before = self.files()
        preview = self.value("autobot", "init")
        self.assertEqual(preview["register"], ["agent.a"])
        self.assertEqual(before, self.files())
        result = self.init()
        self.assertFalse(result["runtimeStarted"])
        self.assertEqual(private.read_text(), "Accepted private project brand\n")
        self.assertTrue((self.systemx / result["receipt"]).is_file())
        self.assertEqual(json.loads((self.systemx / result["receipt"]).read_text())["state"], "complete")
        agents = json.loads((self.systemx / "AGENTS/REGISTRY.json").read_text())["agents"]
        self.assertEqual(agents[-1], {"id": "agent.a", "role": "autobot-coordinator", "memory": "AGENTS/agent.a/MEMORY.md"})
        before = self.files()
        self.assertEqual(self.init()["add"], [])
        self.assertEqual(before, self.files())

    def test_context_reads_only_selected_files_and_carries_original_digests(self):
        (self.systemx / "AUTOBOT/Soul.MD").write_text("UNSELECTED_PRIVATE_FACT\n")
        data = self.systemx / "DATA/private.txt"
        data.parent.mkdir(exist_ok=True)
        data.write_text("DO_NOT_SCAN_DATA\n")
        before = self.files()
        packet = self.value("autobot", "context", "--bot", "autobot.design", "--bot", "autobot.tokens")
        self.assertEqual([item["path"] for item in packet["sources"]],
                         ["AUTOBOT/AGENTA.MD", "AUTOBOT/Design.MD", "AUTOBOT/Tokens.MD"])
        self.assertTrue(all(len(item["sha256"]) == 64 for item in packet["sources"]))
        self.assertFalse(packet["executed"])
        self.assertNotIn("UNSELECTED_PRIVATE_FACT", json.dumps(packet))
        self.assertNotIn("DO_NOT_SCAN_DATA", json.dumps(packet))
        self.assertEqual(before, self.files())

    def test_request_preview_then_retained_reuse_without_reprocessing(self):
        self.init()
        before = self.files()
        preview = self.request(apply=False)
        self.assertEqual(before, self.files())
        stored = self.request()
        self.assertEqual(stored["request"]["id"], preview["request"]["id"])
        self.assertFalse(stored["reused"])
        self.assertFalse(stored["executed"])
        before = self.files()
        retry = self.request()
        self.assertTrue(retry["reused"])
        self.assertEqual(before, self.files())
        self.assertEqual(retry["request"]["state"], "requested")

    def test_complete_is_previewed_immutable_idempotent_and_does_not_accept_tasks(self):
        self.init()
        identifier = self.request()["request"]["id"]
        tasks = (self.systemx / "WORK/TASKS.json").read_bytes()
        before = self.files()
        preview = self.completion(identifier, apply=False)
        self.assertFalse(preview["taskAccepted"])
        self.assertEqual(before, self.files())
        complete = self.completion(identifier)
        self.assertTrue(complete["request"]["resultFresh"])
        before = self.files()
        self.assertFalse(self.completion(identifier)["changed"])
        self.assertEqual(before, self.files())
        retry = self.request()
        self.assertTrue(retry["reused"])
        self.assertEqual(retry["request"]["completion"], complete["request"]["completion"])
        self.rejected("autobot", "complete", identifier, "--summary", "Different claim",
                      "--response-revision", "r2", "--evidence", "proof", "--apply")
        self.assertEqual((self.systemx / "WORK/TASKS.json").read_bytes(), tasks)

    def test_changed_file_revision_and_policy_make_distinct_requests_and_stale_history(self):
        self.init()
        original = self.request()["request"]["id"]
        self.completion(original)
        (self.systemx / "AUTOBOT/Design.MD").write_text("Accepted new design revision\n")
        stale = self.value("autobot", "status", original)["request"]
        self.assertFalse(stale["contextCurrent"])
        self.assertFalse(stale["resultFresh"])
        self.rejected("autobot", "complete", original, "--summary", "fixture", "--response-revision", "r2", "--evidence", "proof")
        changed_file = self.request()["request"]["id"]
        changed_revision = self.request("--input-revision", "revision-2")["request"]["id"]
        catalog_path = self.systemx / "AUTOBOT/CATALOG.json"
        catalog = json.loads(catalog_path.read_text())
        catalog["bots"][0]["functions"].append("Accepted new project constraint")
        catalog_path.write_text(json.dumps(catalog))
        changed_policy = self.request()["request"]["id"]
        self.assertEqual(len({original, changed_file, changed_revision, changed_policy}), 4)

    def test_unselected_file_change_does_not_force_reprocessing(self):
        self.init()
        original = self.request()["request"]["id"]
        self.completion(original)
        (self.systemx / "AUTOBOT/Research.MD").write_text("Unselected update\n")
        before = self.files()
        reused = self.request()
        self.assertTrue(reused["reused"])
        self.assertTrue(reused["request"]["resultFresh"])
        self.assertEqual(before, self.files())

    def test_only_registered_core_callers_tools_and_existing_tasks_are_accepted(self):
        self.init()
        for caller in ("agent.x", "agent.y", "agent.z", "agent.99", "autobot.design"):
            self.rejected("autobot", "request", "--caller", caller, "--purpose", "fixture",
                          "--input-revision", "r1", "--bot", "autobot.design")
        for caller in ("agent.0", "agent.a", "tools"):
            self.assertFalse(self.request("--caller", caller, apply=False)["executed"])
        self.rejected("autobot", "request", "--caller", "agent.0", "--purpose", "fixture",
                      "--input-revision", "r1", "--bot", "autobot.design", "--task", "TASK-999")
        self.assert_ok(self.run_cli("task-add", "--title", "Fixture", "--acceptance", "Original proof"))
        self.assertEqual(self.request("--task", "TASK-001")["request"]["identity"]["task"], "TASK-001")

    def test_catalog_rejects_eleventh_slot_unknown_fields_and_wrong_case(self):
        path = self.systemx / "AUTOBOT/CATALOG.json"
        original = path.read_text()
        for change in (lambda d: d["bots"].append(d["bots"][0]),
                       lambda d: d.update({"automatic": True}),
                       lambda d: d["bots"][0].update({"file": "AUTOBOT/design.md"}),
                       lambda d: d["bots"][0].update({"id": "autobot.custom"})):
            data = json.loads(original)
            change(data)
            path.write_text(json.dumps(data))
            self.rejected("autobot", "list")
        path.write_text(original)
        self.rejected("autobot", "context", "--bot", "autobot.design", "--bot", "autobot.design")
        self.rejected("autobot", "context", "--bot", "../DATA/private")
        self.rejected("autobot", "context", "--bot", "agent.a")

    def test_symlink_hardlink_and_case_attacks_are_refused(self):
        path = self.systemx / "AUTOBOT/Design.MD"
        original = path.read_bytes()
        outside = self.root / "outside.md"
        outside.write_text("Do not read this source")
        path.unlink()
        try:
            path.symlink_to(outside)
        except (OSError, NotImplementedError):
            path.write_bytes(original)
            self.skipTest("Symbolic links unavailable")
        self.rejected("autobot", "context", "--bot", "autobot.design")
        path.unlink()
        os.link(outside, path)
        self.rejected("autobot", "context", "--bot", "autobot.design")
        path.unlink()
        wrong = path.with_name("design.md")
        wrong.write_bytes(original)
        self.rejected("autobot", "context", "--bot", "autobot.design")
        wrong.unlink()
        path.write_bytes(original)
        self.assertEqual(outside.read_text(), "Do not read this source")

    def test_context_and_response_limits_refuse_oversized_inputs(self):
        self.init()
        path = self.systemx / "AUTOBOT/Design.MD"
        original = path.read_bytes()
        path.write_text("A" * (64 * 1024))
        self.rejected("autobot", "context", "--bot", "autobot.design")
        path.write_text("A" * (256 * 1024 + 1))
        self.rejected("autobot", "context", "--bot", "autobot.design")
        path.write_bytes(original)
        self.rejected("autobot", "request", "--caller", "agent.0", "--purpose", "A" * 4097,
                      "--input-revision", "r1", "--bot", "autobot.design", "--apply")
        identifier = self.request()["request"]["id"]
        self.rejected("autobot", "complete", identifier, "--summary", "A" * 8193,
                      "--response-revision", "r1", "--evidence", "proof", "--apply")

    def test_unknown_or_tampered_receipts_fail_closed_without_rewriting(self):
        self.init()
        identifier = self.request()["request"]["id"]
        self.rejected("autobot", "status", "ABR-" + "0" * 20)
        self.rejected("autobot", "complete", "ABR-" + "0" * 20, "--summary", "fixture",
                      "--response-revision", "r1", "--evidence", "proof", "--apply")
        path = self.systemx / "AUTOBOT/REQUESTS.json"
        data = json.loads(path.read_text())
        data["requests"][0]["identity"]["purpose"] = "Tampered request"
        path.write_text(json.dumps(data))
        before = path.read_bytes()
        self.rejected("autobot", "status", identifier)
        self.rejected("autobot", "init", "--apply")
        self.assertEqual(path.read_bytes(), before)

    def test_legacy_scope_can_opt_in_without_root_private_facts(self):
        (self.systemx / "AUTOBOT/Brand.MD").write_text("ROOT_PRIVATE_BRAND\n")
        self.value("projects", "add", "Project-A", "--apply")
        child = self.systemx / "Projects/Project-A/.SYSTEMXP"
        if (child / "AUTOBOT").exists():
            shutil.rmtree(child / "AUTOBOT")
        preview = self.value("projects", "autobot", "init", "--project", "Project-A")
        self.assertIn("AUTOBOT/Brand.MD", preview["add"])
        self.assertFalse((child / "AUTOBOT").exists())
        self.value("projects", "autobot", "init", "--project", "Project-A", "--apply")
        self.assertNotIn("ROOT_PRIVATE_BRAND", (child / "AUTOBOT/Brand.MD").read_text())
        self.assertEqual((child / "AUTOBOT/Brand.MD").read_bytes(),
                         (self.systemx / "templates/autobot/Brand.MD").read_bytes())
        self.value("projects", "agent-a", "request", "--project", "Project-A", "--caller", "agent.0",
                   "--purpose", "Child design", "--input-revision", "r1", "--bot", "autobot.design", "--apply")
        self.assertEqual(self.value("autobot", "status")["total"], 0)
        self.assertEqual(self.value("projects", "autobot", "status", "--project", "Project-A")["total"], 1)

    def test_core_agent_role_is_reserved_and_normal_context_does_not_load_panel(self):
        self.rejected("agent-add", "agent.a", "--role", "arbitrary")
        self.init()
        (self.systemx / "AUTOBOT/Memory.MD").write_text("ON_DEMAND_ONLY_MEMORY\n")
        result = self.run_cli("context", "--agent", "agent.0")
        self.assert_ok(result)
        self.assertNotIn("ON_DEMAND_ONLY_MEMORY", result.stdout)

    def test_initialized_missing_records_fail_validation_and_init_can_restore_without_overwriting(self):
        self.init()
        (self.systemx / "AUTOBOT/Design.MD").unlink()
        (self.systemx / "AUTOBOT/Brand.MD").write_text("Preserve adopted brand\n")
        self.rejected("validate")
        repaired = self.init()
        self.assertIn("AUTOBOT/Design.MD", repaired["add"])
        self.assertEqual((self.systemx / "AUTOBOT/Brand.MD").read_text(), "Preserve adopted brand\n")

    def test_validation_allows_request_ledger_above_individual_context_file_limit(self):
        self.init()
        path = self.systemx / "AUTOBOT/REQUESTS.json"
        # Legal JSON whitespace makes a >256 KiB ledger without processing
        # thousands of unrelated requests; its separate capacity is 8 MiB.
        path.write_text('{"schemaVersion": 1, "requests": []}' + ' ' * (300 * 1024))
        result = self.run_cli("validate")
        self.assert_ok(result)
        self.assertEqual(self.value("autobot", "status")["total"], 0)
        before = path.read_bytes()
        self.value("autobot", "init", "--apply")
        self.assertEqual(path.read_bytes(), before)

    def test_parallel_identical_requests_share_one_retained_identity(self):
        self.init()
        command = ("autobot", "request", "--caller", "agent.0", "--purpose", "Parallel bounded context",
                   "--input-revision", "r1", "--bot", "autobot.design", "--apply")
        with ThreadPoolExecutor(max_workers=10) as pool:
            outputs = list(pool.map(lambda _: self.run_cli(*command), range(10)))
        for result in outputs:
            self.assert_ok(result)
        values = [json.loads(result.stdout) for result in outputs]
        self.assertEqual(len({value["request"]["id"] for value in values}), 1)
        self.assertEqual(self.value("autobot", "status")["total"], 1)

    def test_blank_seeds_accept_crlf_without_weakening_live_context_hashes(self):
        path = self.systemx / "AUTOBOT/Design.MD"
        original = path.read_bytes()
        path.write_bytes(original.replace(b"\n", b"\r\n"))
        # Call only the AUTOBOT blank validator: the distribution manifest is
        # regenerated by the release owner after all source edits are frozen.
        import sys
        with patch.object(sys, "path", [str(test_systemx.SOURCE),
                                        str(test_systemx.SOURCE / "scripts"), *sys.path]):
            import autobots
            autobots.validate_template(self.systemx, self.systemx)
        self.init()
        first = self.request()["request"]["id"]
        path.write_bytes(original)
        second = self.request()["request"]["id"]
        self.assertNotEqual(first, second)

    def test_deep_json_nesting_fails_closed_without_a_traceback(self):
        path = self.systemx / "AUTOBOT/CATALOG.json"
        path.write_text("[" * 2000 + "0" + "]" * 2000)
        result = self.rejected("autobot", "list")
        self.assertIn("AUTOBOT", result.stderr)


if __name__ == "__main__":
    unittest.main()
