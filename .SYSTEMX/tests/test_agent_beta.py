"""Agent Beta offline setup and BOT/DOT workspace behavior in temporary copies."""

import argparse
import json
import os
from pathlib import Path
import sys
import unittest

import test_systemx


sys.path.insert(0, str(test_systemx.SOURCE))
sys.path.insert(0, str(test_systemx.SOURCE / "scripts"))
import agent_beta
import agenda_access
import project_workspaces


class AgentBetaTests(unittest.TestCase):
    setUp = test_systemx.SystemxTests.setUp
    run_cli = test_systemx.SystemxTests.run_cli
    assert_ok = test_systemx.SystemxTests.assert_ok

    def files(self):
        return {path.relative_to(self.systemx).as_posix(): path.read_bytes()
                for path in self.systemx.rglob("*") if path.is_file()}

    def setup_beta(self):
        return agent_beta.initialize(self.systemx, self.systemx, apply=True)

    def add_access_decision(self, identifier, actor, decision="reviewed-intent"):
        revision = agenda_access.status(self.systemx)["accessRevision"]
        return agenda_access.add_decision(self.systemx, argparse.Namespace(
            id=identifier, actor=actor, resource="fixture:" + identifier,
            action="reference", environment="test", decision=decision,
            owner="agent.0", policy_ref="policy:fixture" if decision == "reviewed-intent" else "",
            evidence=["fixture"], reviewed_at=agent_beta.memory.now(), recheck="",
            expected_revision=revision, apply=True))

    def test_public_seed_is_blank_and_setup_requires_apply(self):
        agent_beta.validate_template(self.systemx, self.systemx)
        self.assertEqual(agent_beta.load_bots(self.systemx), {"schemaVersion": 1, "bots": []})
        self.assertFalse(agent_beta.dispatch(self.systemx, self.systemx,
                         argparse.Namespace(beta_action="status"))["registered"])
        before = self.files()
        plan = agent_beta.initialize(self.systemx, self.systemx)
        self.assertEqual(plan["register"], ["agent.b"])
        self.assertEqual(plan["add"], [agent_beta.MEMORY])
        self.assertFalse(plan["runtimeStarted"])
        self.assertEqual(before, self.files())
        applied = self.setup_beta()
        self.assertTrue(applied["applied"])
        self.assertEqual((self.systemx / agent_beta.MEMORY).read_text(),
                         (self.systemx / "AGENTB/MEMORY.md").read_text())
        registry = json.loads((self.systemx / "AGENTS/REGISTRY.json").read_text())
        self.assertEqual(registry["agents"][-1], {"id": "agent.b", "role": "bot-coordinator",
                                                  "memory": agent_beta.MEMORY})
        after = self.files()
        self.assertEqual(self.setup_beta()["add"], [])
        self.assertEqual(after, self.files())

    def test_crlf_beta_memory_and_ignore_seeds_validate_and_initialize(self):
        for relative in ("AGENTB/MEMORY.md", "AGENTB/.gitignore",
                         "templates/agentb/MEMORY.md", "templates/agentb/.gitignore"):
            path = self.systemx / relative
            original = path.read_bytes()
            self.assertIn(b"\n", original)
            path.write_bytes(original.replace(b"\n", b"\r\n"))
        self.assertEqual(agent_beta._text(self.systemx, "AGENTB/MEMORY.md"),
                         agent_beta.BLANK_MEMORY)
        self.assertEqual(agent_beta._text(self.systemx, "AGENTB/.gitignore"),
                         agent_beta.BLANK_GITIGNORE)
        agent_beta.validate_template(self.systemx, self.systemx)
        before = self.files()
        self.assertEqual(agent_beta.initialize(self.systemx, self.systemx)["register"], ["agent.b"])
        self.assertEqual(before, self.files())
        self.assertTrue(agent_beta.initialize(self.systemx, self.systemx, apply=True)["applied"])
        self.assertEqual((self.systemx / agent_beta.MEMORY).read_bytes(),
                         agent_beta.BLANK_MEMORY.encode("utf-8"))
        agent_beta.validate_optional(self.systemx)

        ignore = self.systemx / "AGENTB/.gitignore"
        ignore.write_bytes(b"/.SYSTEMXB-*/\r")
        with self.assertRaisesRegex(ValueError, "bare carriage return"):
            agent_beta.validate_optional(self.systemx)

    def test_populated_root_does_not_seed_child_bot_index(self):
        self.setup_beta()
        agent_beta.add_bot(self.systemx, "ROOTBOT", apply=True)
        self.assertEqual(len(agent_beta.load_bots(self.systemx)["bots"]), 1)
        project_workspaces.Workspaces(self.systemx, self.systemx).add("Demo", apply=True)
        child = self.systemx / "Projects/Demo/.SYSTEMXP"
        before = {path.relative_to(child).as_posix(): path.read_bytes()
                  for path in child.rglob("*") if path.is_file()}
        preview = agent_beta.initialize(child, self.systemx)
        self.assertEqual(preview["register"], ["agent.b"])
        self.assertEqual(before, {path.relative_to(child).as_posix(): path.read_bytes()
                                  for path in child.rglob("*") if path.is_file()})
        agent_beta.initialize(child, self.systemx, apply=True)
        self.assertEqual(agent_beta.load_bots(child), {"schemaVersion": 1, "bots": []})
        self.assertFalse((child / "AGENTB/.SYSTEMXB-ROOTBOT").exists())
        self.assertEqual(len(agent_beta.load_bots(self.systemx)["bots"]), 1)
        agent_beta.validate_optional(child)

    def test_bot_add_and_task_reference_are_local_previewed_and_idempotent(self):
        self.setup_beta()
        before = self.files()
        plan = agent_beta.add_bot(self.systemx, "DESIGN", "dot")
        self.assertEqual(plan["path"], "AGENTB/.SYSTEMXB-DESIGN")
        self.assertFalse(plan["online"])
        self.assertEqual(before, self.files())
        created = agent_beta.add_bot(self.systemx, "DESIGN", "dot", apply=True)
        self.assertTrue(created["created"])
        self.assertTrue(created["applied"])
        bot = json.loads((self.systemx / "AGENTB/.SYSTEMXB-DESIGN/BOT.json").read_text())
        self.assertEqual(bot, {"schemaVersion": 1, "name": "DESIGN", "kind": "dot",
                               "source": "local", "provider": "", "providerIdentity": "",
                               "accessDecisionId": "", "online": False, "taskIds": []})
        self.assertEqual((self.systemx / "AGENTB/.SYSTEMXB-DESIGN/Rules.MD").read_text(),
                         "# Provider rules\n\n")
        self.assertEqual(agent_beta.load_bots(self.systemx)["bots"],
                         [{"name": "DESIGN", "kind": "dot", "path": "AGENTB/.SYSTEMXB-DESIGN"}])
        after = self.files()
        self.assertFalse(agent_beta.add_bot(self.systemx, "DESIGN", "dot", apply=True)["created"])
        self.assertEqual(after, self.files())
        agent_beta.memory.add_task(self.systemx, argparse.Namespace(
            title="Fixture", owner="agent.0", acceptance=["Evidence"], scope=[],
            depends_on=[], milestone="", next=""))
        before = self.files()
        preview = agent_beta.assign_task(self.systemx, "DESIGN", "TASK-001")
        self.assertEqual(preview["bot"]["taskIds"], ["TASK-001"])
        self.assertEqual(before, self.files())
        self.assertTrue(agent_beta.assign_task(self.systemx, "DESIGN", "TASK-001", apply=True)["applied"])
        self.assertFalse(agent_beta.assign_task(self.systemx, "DESIGN", "TASK-001", apply=True)["changed"])
        self.assertEqual(json.loads((self.systemx / "AGENTB/.SYSTEMXB-DESIGN/BOT.json").read_text())
                         ["taskIds"], ["TASK-001"])
        agent_beta.validate_optional(self.systemx)

    def test_online_source_is_only_a_reference_and_access_decision_must_exist(self):
        self.setup_beta()
        with self.assertRaises(ValueError):
            agent_beta.add_bot(self.systemx, "REMOTE", source="online-reference",
                               provider="github", provider_identity="bot_alias",
                               access_decision_id="ACC-001", apply=True)
        with self.assertRaises(ValueError):
            agent_beta.add_bot(self.systemx, "SECRET", source="online-reference",
                               provider="github", provider_identity="ghp_example_token", apply=True)
        access = {"schemaVersion": 1, "decisions": [{
            "id": "ACC-001", "actor": "agentb:REMOTE", "resource": "fixture", "action": "reference",
            "environment": "test", "decision": "reviewed-intent", "owner": "agent.0",
            "policyRef": "", "evidence": ["fixture"], "reviewedAt": agent_beta.memory.now(),
            "recheck": ""}]}
        (self.systemx / "GLOBAL/ACCESS-MATRIX.json").write_text(json.dumps(access))
        before = self.files()
        preview = agent_beta.add_bot(self.systemx, "REMOTE", source="online-reference",
                                     provider="github", provider_identity="bot_alias",
                                     access_decision_id="ACC-001")
        self.assertFalse(preview["online"])
        self.assertEqual(before, self.files())
        created = agent_beta.add_bot(self.systemx, "REMOTE", source="online-reference",
                                     provider="github", provider_identity="bot_alias",
                                     access_decision_id="ACC-001", apply=True)
        self.assertTrue(created["created"])
        bot = json.loads((self.systemx / "AGENTB/.SYSTEMXB-REMOTE/BOT.json").read_text())
        self.assertEqual((bot["source"], bot["provider"], bot["providerIdentity"],
                          bot["accessDecisionId"], bot["online"]),
                         ("online-reference", "github", "bot_alias", "ACC-001", False))
        self.assertFalse(agent_beta.add_bot(self.systemx, "REMOTE", source="online-reference",
                                            provider="github", provider_identity="bot_alias",
                                            access_decision_id="ACC-001", apply=True)["created"])
        with self.assertRaises(ValueError):
            agent_beta.add_bot(self.systemx, "REMOTE", source="online-reference",
                               provider="github", provider_identity="another_alias", apply=True)
        agent_beta.validate_optional(self.systemx)

    def test_access_link_completes_bot_then_agenda_decision_workflow(self):
        self.setup_beta()
        agent_beta.add_bot(self.systemx, "REMOTE", source="online-reference",
                           provider="github", provider_identity="bot_alias", apply=True)
        self.assertTrue(self.add_access_decision("ACC-001", "agentb:REMOTE")["applied"])
        before = self.files()
        preview = agent_beta.link_access(self.systemx, "REMOTE", "ACC-001")
        parser = argparse.ArgumentParser()
        agent_beta.add_cli(parser.add_subparsers(dest="action", required=True))
        cli_args = parser.parse_args(["agent-beta", "access-link", "REMOTE",
                                      "--access-decision-id", "ACC-001"])
        self.assertEqual(agent_beta.dispatch(self.systemx, self.systemx, cli_args), preview)
        self.assertEqual(preview["accessDecision"], {"id": "ACC-001", "actor": "agentb:REMOTE",
                                                      "resource": "fixture:ACC-001", "action": "reference",
                                                      "environment": "test", "decision": "reviewed-intent"})
        self.assertFalse(preview["applied"])
        self.assertFalse(preview["online"])
        self.assertFalse(preview["accessGranted"])
        self.assertEqual(before, self.files())
        with self.assertRaisesRegex(ValueError, "requires --expected-revision"):
            agent_beta.link_access(self.systemx, "REMOTE", "ACC-001", apply=True)
        self.assertEqual(before, self.files())

        applied = agent_beta.link_access(self.systemx, "REMOTE", "ACC-001",
                                         preview["revisionBefore"], apply=True)
        self.assertTrue(applied["applied"])
        self.assertTrue(applied["changed"])
        self.assertNotEqual(applied["revisionBefore"], applied["revisionAfter"])
        bot = json.loads((self.systemx / "AGENTB/.SYSTEMXB-REMOTE/BOT.json").read_text())
        self.assertEqual(bot["accessDecisionId"], "ACC-001")
        self.assertFalse(bot["online"])
        agent_beta.validate_optional(self.systemx)

        unchanged = agent_beta.link_access(self.systemx, "REMOTE", "ACC-001")
        self.assertFalse(agent_beta.link_access(self.systemx, "REMOTE", "ACC-001",
                                                unchanged["revisionBefore"], apply=True)["applied"])
        self.add_access_decision("ACC-002", "agentb:REMOTE")
        replacement = agent_beta.link_access(self.systemx, "REMOTE", "ACC-002")
        self.assertTrue(agent_beta.link_access(self.systemx, "REMOTE", "ACC-002",
                                               replacement["revisionBefore"], apply=True)["applied"])
        self.assertEqual(json.loads((self.systemx / "AGENTB/.SYSTEMXB-REMOTE/BOT.json").read_text())
                         ["accessDecisionId"], "ACC-002")

    def test_access_link_refuses_wrong_actor_denial_and_stale_revision(self):
        self.setup_beta()
        agent_beta.add_bot(self.systemx, "REMOTE", apply=True)
        self.add_access_decision("ACC-001", "agent.0")
        self.add_access_decision("ACC-002", "agentb:REMOTE", decision="denied")
        self.add_access_decision("ACC-003", "agentb:REMOTE")
        before = self.files()
        for identifier in ("ACC-001", "ACC-002", "ACC-999"):
            with self.subTest(identifier=identifier), self.assertRaises(ValueError):
                agent_beta.link_access(self.systemx, "REMOTE", identifier, apply=False)
        with self.assertRaisesRegex(ValueError, "Unknown Agent Beta bot"):
            agent_beta.link_access(self.systemx, "MISSING", "ACC-003")
        self.assertEqual(before, self.files())

        preview = agent_beta.link_access(self.systemx, "REMOTE", "ACC-003")
        self.add_access_decision("ACC-004", "agent.0")
        before_apply = self.files()
        with self.assertRaisesRegex(ValueError, "changed since preview"):
            agent_beta.link_access(self.systemx, "REMOTE", "ACC-003",
                                   preview["revisionBefore"], apply=True)
        self.assertEqual(before_apply, self.files())
        self.assertEqual(json.loads((self.systemx / "AGENTB/.SYSTEMXB-REMOTE/BOT.json").read_text())
                         ["accessDecisionId"], "")
        (self.systemx / "AUTOBOT/AGENDA.json").unlink()
        with self.assertRaisesRegex(ValueError, "initialized together"):
            agent_beta.link_access(self.systemx, "REMOTE", "ACC-003")

    def test_malformed_access_matrix_row_is_rejected_before_bot_write(self):
        self.setup_beta()
        matrix = self.systemx / "GLOBAL/ACCESS-MATRIX.json"
        matrix.write_text(json.dumps({"schemaVersion": 1, "decisions": [{"id": "ACC-001"}]}))
        before = self.files()
        with self.assertRaises(ValueError):
            agent_beta.add_bot(self.systemx, "REMOTE", source="online-reference",
                               provider="github", provider_identity="bot_alias",
                               access_decision_id="ACC-001", apply=True)
        with self.assertRaises(ValueError):
            agent_beta.add_bot(self.systemx, "LOCAL", apply=True)
        self.assertEqual(before, self.files())
        self.assertFalse((self.systemx / "AGENTB/.SYSTEMXB-REMOTE").exists())
        self.assertFalse((self.systemx / "AGENTB/.SYSTEMXB-LOCAL").exists())

    def test_unsafe_names_conflicts_online_state_and_unindexed_workspace_are_rejected(self):
        self.setup_beta()
        for name in ("lower", "../ESCAPE", "A/B", "A\\B", ".X", "1BOT", "A" * 33, "A B"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                agent_beta.add_bot(self.systemx, name, apply=True)
        self.assertFalse((self.root / "ESCAPE").exists())
        agent_beta.add_bot(self.systemx, "CIPHER", apply=True)
        with self.assertRaises(ValueError):
            agent_beta.add_bot(self.systemx, "CIPHER", "dot", apply=True)
        path = self.systemx / "AGENTB/.SYSTEMXB-CIPHER/BOT.json"
        data = json.loads(path.read_text())
        data["online"] = True
        path.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            agent_beta.validate_optional(self.systemx)
        data["online"] = False
        path.write_text(json.dumps(data))
        (self.systemx / "AGENTB/.SYSTEMXB-ORPHAN").mkdir()
        with self.assertRaises(ValueError):
            agent_beta.validate_optional(self.systemx)

    def test_symlinked_bot_record_is_rejected_and_cli_interface_is_read_only_by_default(self):
        self.setup_beta()
        agent_beta.add_bot(self.systemx, "PROBE", apply=True)
        path = self.systemx / "AGENTB/.SYSTEMXB-PROBE/BOT.json"
        outside = self.root / "outside.json"
        outside.write_bytes(path.read_bytes())
        path.unlink()
        try:
            path.symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest("Symbolic links unavailable")
        with self.assertRaises(ValueError):
            agent_beta.load_bots(self.systemx)
        path.unlink()
        os.link(outside, path)
        with self.assertRaises(ValueError):
            agent_beta.load_bots(self.systemx)
        path.unlink()
        path.write_bytes(outside.read_bytes())
        parser = argparse.ArgumentParser()
        agent_beta.add_cli(parser.add_subparsers(dest="action", required=True))
        args = parser.parse_args(["agent-beta", "bot-add", "SECOND"])
        before = self.files()
        result = agent_beta.dispatch(self.systemx, self.systemx, args)
        self.assertFalse(result["applied"])
        self.assertEqual(before, self.files())


if __name__ == "__main__":
    unittest.main()
