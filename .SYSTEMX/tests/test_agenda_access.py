"""Agenda decisions stay blank; fixed role defaults grant nothing."""

from argparse import Namespace
import json
from pathlib import Path
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile


DEFAULTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DEFAULTS))
sys.path.insert(0, str(DEFAULTS / "scripts"))
import agenda_access as agenda  # noqa: E402


class AgendaAccessTests(unittest.TestCase):
    def fixture(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name) / ".SYSTEMX"
        for folder in ("AUTOBOT", "GLOBAL", "AGENTS/agent.0", "AGENTS/agent.a", "WORK", "PLAN"):
            (root / folder).mkdir(parents=True, exist_ok=True)
        for relative in (agenda.AGENDA, agenda.ACCESS):
            (root / relative).write_bytes((DEFAULTS / relative).read_bytes())
        (root / "AUTOBOT/Rules.MD").write_text("# Reviewed advisory rules\n", encoding="utf-8")
        (root / "WORK/TASKS.json").write_text('{"schemaVersion":1,"tasks":[]}\n', encoding="utf-8")
        (root / "WORK/FOCUS.json").write_text(
            '{"schemaVersion":1,"objective":"","taskIds":[],"checkpoint":"","updatedAt":""}\n',
            encoding="utf-8")
        (root / "PLAN/MASTER-PLAN.md").write_text("# Blank plan\n", encoding="utf-8")
        (root / "AGENTS/agent.0/MEMORY.md").write_text("# Agent 0\n", encoding="utf-8")
        (root / "AGENTS/agent.a/MEMORY.md").write_text("# Agent Alpha\n", encoding="utf-8")
        (root / "AGENTS/REGISTRY.json").write_text(json.dumps({"schemaVersion": 1, "agents": [
            {"id": "agent.0", "role": "coordinator", "memory": "AGENTS/agent.0/MEMORY.md"},
            {"id": "agent.a", "role": "autobot-coordinator", "memory": "AGENTS/agent.a/MEMORY.md"}]}), encoding="utf-8")
        return root

    def decision(self, root):
        value = {"schemaVersion": 1, "decisions": [{
            "id": "ACC-001", "actor": "=HYPERLINK(\"https://example.test\")",
            "resource": "selected advisory context", "action": "read", "environment": "fixture",
            "decision": "reviewed-intent", "owner": "user", "policyRef": "fixture/policy",
            "evidence": ["fixture/review"], "reviewedAt": "2026-10-30T20:00:00Z",
            "recheck": "when source changes"}]}
        (root / agenda.ACCESS).write_text(json.dumps(value), encoding="utf-8")

    def args(self, root, apply=False):
        return Namespace(id="AGA-001", bot="autobot.rules", value="include",
                         provider_rules="AUTOBOT/Rules.MD", access_decision_id="ACC-001",
                         reason="Explicit fixture selection", reviewed_at="2026-10-30T20:01:00Z",
                         evidence=["fixture/review"],
                         expected_revision=agenda.status(root)["agendaRevision"], apply=apply)

    def decision_args(self, root, actor="agent.0", apply=False):
        return Namespace(id="ACC-002", actor=actor, resource="example resource",
                         action="read", environment="fixture", decision="gap",
                         owner="user", policy_ref="", evidence=["fixture/review"],
                         reviewed_at="2026-10-30T20:01:00Z", recheck="on scope change",
                         expected_revision=agenda.status(root)["accessRevision"], apply=apply)

    def test_public_template_tables_are_blank(self):
        agenda.validate_template(DEFAULTS)
        status = agenda.status(DEFAULTS)
        self.assertTrue(status["initialized"])
        self.assertEqual((status["agendaOptions"], status["accessDecisions"]), (0, 0))
        self.assertEqual(status["roleDefaults"], 20)
        self.assertFalse(status["accessGranted"])
        tables = agenda.table(DEFAULTS, "csv")
        self.assertTrue(tables["agendaCsv"].startswith("id,botId,setting,value,"))
        self.assertTrue(tables["accessCsv"].startswith("id,actor,resource,action,"))
        self.assertTrue(tables["roleCsv"].startswith("id,actor,kind,instanceRule,"))
        roles = agenda.table(DEFAULTS)["roleRows"]
        self.assertEqual(len(roles), 20)
        self.assertTrue(all(row["templateGrant"] == "none" and row["requiresReview"] is True
                            for row in roles))
        self.assertEqual({row["actor"] for row in roles if row["kind"] == "autobot"},
                         {"autobot." + item[0] for item in agenda.autobots.SLOTS})
        self.assertEqual({row["actor"] for row in roles if row["kind"].endswith("pattern")},
                         {"agent.numeric-worker", "native.subagent", "agentb.instance"})

    def test_legacy_selected_scope_is_accepted_without_implied_role_grants(self):
        root = self.fixture()
        legacy = {"schemaVersion": 1, "decisions": []}
        (root / agenda.ACCESS).write_text(json.dumps(legacy), encoding="utf-8")
        self.assertEqual(agenda.status(root)["roleDefaults"], 0)
        self.assertFalse(agenda.status(root)["accessGranted"])
        self.assertEqual(agenda.table(root)["roleRows"], [])

    def test_legacy_role_upgrade_preserves_existing_decisions(self):
        root = self.fixture()
        self.decision(root)
        before = agenda.table(root)["accessRows"]
        args = Namespace(expected_revision=agenda.status(root)["accessRevision"], apply=False)
        preview = agenda.upgrade_roles(root, args)
        self.assertTrue(preview["changed"])
        self.assertEqual(preview["decisionsPreserved"], 1)
        self.assertEqual(agenda.status(root)["roleDefaults"], 0)
        args.apply = True
        applied = agenda.upgrade_roles(root, args)
        self.assertTrue(applied["applied"])
        self.assertEqual(agenda.status(root)["roleDefaults"], 20)
        self.assertEqual(agenda.table(root)["accessRows"], before)
        with self.assertRaisesRegex(ValueError, "changed since"):
            agenda.upgrade_roles(root, args)

    def test_role_catalog_cannot_be_changed_into_a_grant(self):
        root = self.fixture()
        access = json.loads((root / agenda.ACCESS).read_text(encoding="utf-8"))
        access["roleDefaults"][0]["templateGrant"] = "enabled"
        (root / agenda.ACCESS).write_text(json.dumps(access), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "fixed default-deny catalog"):
            agenda.status(root)

    def test_decision_add_previews_then_records_without_grant(self):
        root = self.fixture()
        args = self.decision_args(root)
        preview = agenda.add_decision(root, args)
        self.assertFalse(preview["applied"])
        self.assertFalse(preview["accessGranted"])
        self.assertFalse(preview["identityVerified"])
        self.assertEqual(agenda.status(root)["accessDecisions"], 0)
        args.apply = True
        applied = agenda.add_decision(root, args)
        self.assertTrue(applied["applied"])
        self.assertEqual(agenda.status(root)["accessDecisions"], 1)
        self.assertEqual(agenda.table(root)["accessRows"][0]["actor"], "agent.0")
        with self.assertRaisesRegex(ValueError, "changed since"):
            agenda.add_decision(root, args)

    def test_decision_add_validates_instance_and_duplicate_scope(self):
        root = self.fixture()
        args = self.decision_args(root, actor="agent.42")
        with self.assertRaisesRegex(ValueError, "Register this numeric worker"):
            agenda.add_decision(root, args)
        args.actor = "agentb:UNKNOWN"
        with self.assertRaises(ValueError):
            agenda.add_decision(root, args)
        args.actor = "native-subagent:codex:worker-1"
        self.assertEqual(agenda.add_decision(root, args)["actorKind"], "native-instance")
        args.actor = "agent.0"
        args.apply = True
        agenda.add_decision(root, args)
        args.expected_revision = agenda.status(root)["accessRevision"]
        args.id = "ACC-003"
        with self.assertRaisesRegex(ValueError, "already exists"):
            agenda.add_decision(root, args)

    def test_agent_one_with_another_role_is_a_numeric_instance(self):
        root = self.fixture()
        registry_path = root / "AGENTS/REGISTRY.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        registry["agents"].append({"id": "agent.1", "role": "implementation",
                                   "memory": "AGENTS/agent.1/MEMORY.md"})
        (root / "AGENTS/agent.1").mkdir(parents=True)
        (root / "AGENTS/agent.1/MEMORY.md").write_text("# Worker\n", encoding="utf-8")
        registry_path.write_text(json.dumps(registry), encoding="utf-8")
        args = self.decision_args(root, actor="agent.1")
        self.assertEqual(agenda.add_decision(root, args)["actorKind"], "numeric-instance")

    def test_workbook_export_is_explicit_current_and_detects_stale_json(self):
        root = self.fixture()
        args = Namespace(output=agenda.WORKBOOK_DEFAULT, expected_revision="", apply=False)
        preview = agenda.workbook_export(root, args)
        self.assertFalse(preview["applied"])
        self.assertTrue(preview["wouldChange"])
        self.assertFalse((root / agenda.WORKBOOK_DEFAULT).exists())
        args.expected_revision = preview["sourceRevision"]
        args.apply = True
        applied = agenda.workbook_export(root, args)
        self.assertTrue(applied["applied"])
        self.assertTrue(agenda.workbook_check(root)["current"])
        first_bytes = (root / agenda.WORKBOOK_DEFAULT).read_bytes()
        with zipfile.ZipFile(root / agenda.WORKBOOK_DEFAULT) as archive:
            self.assertEqual(len(archive.namelist()), 8)
            role_xml = archive.read("xl/worksheets/sheet1.xml")
            self.assertNotIn(b"<f>", role_xml)
            ns = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
            role_cells = {cell.attrib["r"]: cell.findtext("x:is/x:t", namespaces=ns)
                          for cell in ET.fromstring(role_xml).findall(".//x:c", ns)}
            for row_number, role in enumerate(agenda.ROLE_DEFAULTS, 6):
                self.assertEqual(role_cells["B" + str(row_number)], role["actor"])
        self.assertFalse(agenda.workbook_export(root, args)["wouldChange"])
        self.assertEqual((root / agenda.WORKBOOK_DEFAULT).read_bytes(), first_bytes)

        decision = self.decision_args(root, apply=True)
        agenda.add_decision(root, decision)
        stale = agenda.workbook_check(root)
        self.assertFalse(stale["current"])
        self.assertNotEqual(stale["expectedSha256"], stale["actualSha256"])
        with self.assertRaisesRegex(ValueError, "changed since preview"):
            agenda.workbook_export(root, args)
        args.expected_revision = stale["sourceRevision"]
        updated = agenda.workbook_export(root, args)
        self.assertTrue(updated["current"])
        self.assertNotEqual((root / agenda.WORKBOOK_DEFAULT).read_bytes(), first_bytes)

    def test_workbook_output_is_local_and_formula_like_text_is_inert(self):
        root = self.fixture()
        with self.assertRaisesRegex(ValueError, "inside selected-scope local"):
            agenda.workbook_check(root, "GLOBAL/ACCESS-MATRIX.xlsx")
        args = self.decision_args(root, apply=True)
        args.resource = '=HYPERLINK("https://example.test")'
        agenda.add_decision(root, args)
        preview = agenda.workbook_export(root, Namespace(output=agenda.WORKBOOK_DEFAULT,
                                                         expected_revision="", apply=False))
        agenda.workbook_export(root, Namespace(output=agenda.WORKBOOK_DEFAULT,
                                               expected_revision=preview["sourceRevision"], apply=True))
        with zipfile.ZipFile(root / agenda.WORKBOOK_DEFAULT) as archive:
            data = archive.read("xl/worksheets/sheet2.xml")
            self.assertIn(b't="inlineStr"', data)
            self.assertIn(b'=HYPERLINK(', data)
            self.assertNotIn(b"<f>", data)

    def test_workbook_revision_changes_when_provider_rules_change(self):
        root = self.fixture()
        self.decision(root)
        agenda.set_option(root, self.args(root, apply=True))
        first = agenda.workbook_export(root, Namespace(output=agenda.WORKBOOK_DEFAULT,
                                                       expected_revision="", apply=False))
        agenda.workbook_export(root, Namespace(output=agenda.WORKBOOK_DEFAULT,
                                              expected_revision=first["sourceRevision"], apply=True))
        (root / "AUTOBOT/Rules.MD").write_text("# Changed after export\n", encoding="utf-8")
        stale = agenda.workbook_check(root)
        self.assertFalse(stale["current"])
        self.assertNotEqual(stale["sourceRevision"], first["sourceRevision"])
        with self.assertRaisesRegex(ValueError, "changed since preview"):
            agenda.workbook_export(root, Namespace(output=agenda.WORKBOOK_DEFAULT,
                                                  expected_revision=first["sourceRevision"], apply=True))

    def test_distributed_workbook_role_view_matches_json(self):
        namespace = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
        with zipfile.ZipFile(DEFAULTS / "GLOBAL/ACCESS-MATRIX.xlsx") as archive:
            sheet = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
            cells = {cell.attrib["r"]: (cell.attrib.get("t"), cell.findtext("x:v", namespaces=namespace))
                     for cell in sheet.findall(".//x:c", namespace)}
        for index, field in enumerate(agenda.ROLE_COLUMNS):
            self.assertEqual(cells[chr(ord("A") + index) + "12"][1], field)
        for row_number, role in enumerate(agenda.ROLE_DEFAULTS, 13):
            for column_number, field in enumerate(agenda.ROLE_COLUMNS):
                kind, value = cells[chr(ord("A") + column_number) + str(row_number)]
                if field == "requiresReview":
                    self.assertEqual((kind, value), ("b", "1"))
                else:
                    self.assertEqual(value or "", str(role[field]))
        self.assertNotIn("A33", cells)
        self.assertNotIn("A7", cells)

    def test_init_previews_then_adds_only_blank_selected_scope_records(self):
        root = self.fixture()
        (root / agenda.AGENDA).unlink()
        (root / agenda.ACCESS).unlink()
        preview = agenda.initialize(root, DEFAULTS)
        self.assertEqual(preview["add"], [agenda.AGENDA, agenda.ACCESS])
        self.assertFalse(preview["applied"])
        self.assertFalse((root / agenda.AGENDA).exists())
        applied = agenda.initialize(root, DEFAULTS, apply=True)
        self.assertTrue(applied["applied"])
        self.assertEqual(agenda.status(root)["agendaOptions"], 0)
        self.assertEqual(agenda.status(root)["roleDefaults"], 20)
        self.assertEqual((root / agenda.AGENDA).read_bytes(), (DEFAULTS / agenda.AGENDA).read_bytes())

    def test_child_init_uses_blank_templates_after_root_records_are_populated(self):
        parent = self.fixture()
        child = self.fixture()
        for template in agenda.SEEDS.values():
            target = parent / template
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((DEFAULTS / template).read_bytes())
        self.decision(parent)
        agenda.set_option(parent, self.args(parent, apply=True))
        self.assertEqual(agenda.status(parent)["agendaOptions"], 1)
        (child / agenda.AGENDA).unlink()
        (child / agenda.ACCESS).unlink()

        preview = agenda.initialize(child, parent)
        self.assertFalse(preview["applied"])
        self.assertEqual(preview["add"], [agenda.AGENDA, agenda.ACCESS])
        applied = agenda.initialize(child, parent, apply=True)
        self.assertTrue(applied["applied"])
        self.assertEqual(agenda.status(child)["agendaOptions"], 0)
        self.assertEqual(agenda.status(child)["accessDecisions"], 0)
        self.assertEqual(agenda.status(child)["roleDefaults"], 20)
        self.assertEqual(agenda.status(parent)["agendaOptions"], 1)
        for record, template in agenda.SEEDS.items():
            self.assertEqual((child / record).read_bytes(), (parent / template).read_bytes())

    def test_preview_apply_and_revision_guard_preserve_advisory_boundary(self):
        root = self.fixture()
        self.decision(root)
        before = (root / agenda.AGENDA).read_bytes()
        args = self.args(root)
        preview = agenda.set_option(root, args)
        self.assertTrue(preview["changed"])
        self.assertFalse(preview["applied"])
        self.assertEqual((root / agenda.AGENDA).read_bytes(), before)
        args.apply = True
        applied = agenda.set_option(root, args)
        self.assertTrue(applied["applied"])
        self.assertFalse(applied["accessGranted"])
        self.assertEqual(agenda.status(root)["agendaOptions"], 1)
        self.assertTrue(agenda.table(root)["agendaRows"][0]["rulesCurrent"])
        self.assertIn("'=HYPERLINK", agenda.table(root, "csv")["accessCsv"])
        with self.assertRaisesRegex(ValueError, "changed since"):
            agenda.set_option(root, args)

    def test_stale_rule_and_noncanonical_path_are_visible_or_rejected(self):
        root = self.fixture()
        self.decision(root)
        args = self.args(root, apply=True)
        agenda.set_option(root, args)
        (root / "AUTOBOT/Rules.MD").write_text("# Changed rules\n", encoding="utf-8")
        self.assertEqual(agenda.status(root)["staleRules"], 1)
        self.assertFalse(agenda.table(root)["agendaRows"][0]["rulesCurrent"])
        args = self.args(root)
        args.provider_rules = "AUTOBOT/../AGENTS/agent.0/MEMORY.MD"
        with self.assertRaises(ValueError):
            agenda.set_option(root, args)

    def test_fixed_bot_rules_must_match_and_beta_rules_need_access_reference(self):
        root = self.fixture()
        self.decision(root)
        args = self.args(root)
        args.bot = "autobot.design"
        with self.assertRaisesRegex(ValueError, "must match the selected bot"):
            agenda.set_option(root, args)
        beta_rules = root / "AGENTB/.SYSTEMXB-DEMO/Rules.MD"
        beta_rules.parent.mkdir(parents=True)
        beta_rules.write_text("# Reviewed provider rules\n", encoding="utf-8")
        args.bot = "autobot.rules"
        args.value = "exclude"
        args.provider_rules = "AGENTB/.SYSTEMXB-DEMO/Rules.MD"
        args.access_decision_id = ""
        with self.assertRaisesRegex(ValueError, "accessDecisionId"):
            agenda.set_option(root, args)

    def test_include_rejects_denied_or_gap_and_reports_later_conflict(self):
        root = self.fixture()
        self.decision(root)
        args = self.args(root)
        access = json.loads((root / agenda.ACCESS).read_text())
        for state in ("denied", "gap"):
            access["decisions"][0]["decision"] = state
            (root / agenda.ACCESS).write_text(json.dumps(access), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "reviewed-intent"):
                agenda.set_option(root, args)
        access["decisions"][0]["decision"] = "reviewed-intent"
        (root / agenda.ACCESS).write_text(json.dumps(access), encoding="utf-8")
        args.apply = True
        agenda.set_option(root, args)
        access["decisions"][0]["decision"] = "denied"
        (root / agenda.ACCESS).write_text(json.dumps(access), encoding="utf-8")
        self.assertEqual(agenda.status(root)["accessConflicts"], 1)
        self.assertTrue(agenda.table(root)["agendaRows"][0]["accessConflict"])
        args = self.args(root, apply=True)
        args.value = "exclude"
        agenda.set_option(root, args)
        self.assertEqual(agenda.status(root)["accessConflicts"], 0)


if __name__ == "__main__":
    unittest.main()
