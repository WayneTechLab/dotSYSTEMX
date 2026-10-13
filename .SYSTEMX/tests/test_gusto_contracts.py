"""Portable HR contract integrity checks; no provider or host runtime is invoked."""

import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1] / "GUSTO"


def read(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


class GustoContractTests(unittest.TestCase):
    def test_route_capability_role_and_schema_references_agree(self):
        capabilities = read("CAPABILITIES.json")["capabilities"]
        cap_by_id = {item["id"]: item for item in capabilities}
        self.assertEqual(len(cap_by_id), len(capabilities))
        roles = read("ROLES.json")["roles"]
        role_by_id = {item["id"]: item for item in roles}
        self.assertEqual(set(role_by_id), {
            "employer-owner", "payroll-admin", "hr-admin", "manager",
            "employee", "contractor", "auditor"})
        routes = read("ROUTES.json")["routes"]
        self.assertEqual(len({route["id"] for route in routes}), len(routes))
        self.assertEqual(len({route["path"] for route in routes}), len(routes))
        schema = read("contracts/routes.schema.json")
        required = set(schema["properties"]["routes"]["items"]["required"])
        prefixes = {"admin": "/admin/hr", "employee": "/employee",
                    "manager": "/manager/hr", "contractor": "/contractor"}
        for route in routes:
            with self.subTest(route=route["id"]):
                self.assertEqual(set(route), required)
                self.assertIn(route["capabilityId"], cap_by_id)
                cap = cap_by_id[route["capabilityId"]]
                self.assertEqual(route["backing"], cap["backing"])
                prefix = prefixes[route["portal"]]
                self.assertTrue(route["path"] == prefix or route["path"].startswith(prefix + "/"))
                self.assertTrue(route["sections"] and route["emptyState"] and route["errorState"])
                for role in route["roles"]:
                    self.assertIn(role, role_by_id)
                    self.assertIn(cap["id"], role_by_id[role]["readCapabilities"])
                for action in route["actions"]:
                    self.assertIn(action["mode"], {"mock", "live-gated"})

    def test_workflows_and_fixture_collections_are_real_references(self):
        inventory = read("sdk/endpoint-inventory.json")
        fixture = read("mock/fixtures/demo-company.json")
        for cap in read("CAPABILITIES.json")["capabilities"]:
            with self.subTest(capability=cap["id"]):
                self.assertIn(cap["deliveryStatus"], {"specification", "mock", "live-gated"})
                for workflow in cap["providerWorkflowExports"]:
                    self.assertIn(workflow, inventory["flows"])
                for collection in cap["mockFixtureCollections"]:
                    value = fixture
                    for part in collection.split("."):
                        self.assertIn(part, value)
                        value = value[part]
                if cap["backing"] == "systemx-native":
                    self.assertFalse(cap["providerWorkflowExports"])
                    self.assertFalse(cap["providerApiAreas"])

    def test_vendor_inventory_matches_published_pin_and_license(self):
        pin = read("VERSION-PIN.json")
        sdk = pin["sdk"]
        raw = (ROOT / sdk["inventoryPath"]).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), sdk["inventorySha256"])
        inventory = json.loads(raw)
        self.assertEqual({key: len(value) for key, value in inventory.items()}, sdk["inventoryCounts"])
        self.assertEqual(sdk["package"], "@gusto/embedded-react-sdk")
        self.assertFalse(pin["runtimeIncluded"])
        license_bytes = (ROOT / "sdk/LICENSE-APACHE-2.0.txt").read_bytes()
        self.assertEqual(hashlib.sha256(license_bytes).hexdigest(), sdk["licenseSha256"])
        license_text = license_bytes.decode("utf-8")
        self.assertIn("Apache License", license_text)
        self.assertIn("Version 2.0", license_text)

    def test_demo_references_are_synthetic_and_resources_are_bound(self):
        fixture = read("mock/fixtures/demo-company.json")
        self.assertEqual(fixture["mode"], "mock")
        self.assertIs(fixture["synthetic"], True)
        employees = {item["id"] for item in fixture["employees"]}
        contractors = {item["id"] for item in fixture["contractors"]}
        payrolls = {item["id"] for item in fixture["payrolls"]}
        self.assertIn(fixture["actors"]["managerEmployeeId"], employees)
        self.assertIn(fixture["actors"]["selfEmployeeId"], employees)
        self.assertIn(fixture["actors"]["selfContractorId"], contractors)
        def walk(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    self.assertNotIn(key.lower(), {
                        "access_token", "refresh_token", "client_secret", "ssn",
                        "socialsecuritynumber", "bankaccountnumber", "routingnumber", "taxid"})
                    if key in {"email", "workEmail"}:
                        self.assertTrue(child.endswith("@example.invalid"))
                    if key in {"employeeId", "managerId", "managerEmployeeId", "selfEmployeeId"} and child:
                        self.assertIn(child, employees)
                    if key in {"contractorId", "selfContractorId"}:
                        self.assertIn(child, contractors)
                    if key == "payrollId":
                        self.assertIn(child, payrolls)
                    if key.endswith("Cents"):
                        self.assertIs(type(child), int)
                        self.assertGreaterEqual(child, 0)
                    walk(child)
            elif isinstance(value, list):
                for child in value:
                    walk(child)
        walk(fixture)
        self.assertTrue(all(item["status"] == "disabled" and item["runs"] == 0
                            for item in fixture["native"]["automations"]))

    def test_default_policy_does_not_widen_payroll_or_manager_authority(self):
        roles = {role["id"]: role for role in read("ROLES.json")["roles"]}
        self.assertEqual(roles["employee"]["scope"], "self")
        self.assertEqual(roles["contractor"]["scope"], "self")
        self.assertEqual(roles["manager"]["scope"], "direct-reports")
        self.assertFalse(roles["auditor"]["writeCapabilities"])
        for role in ["manager", "hr-admin", "employee", "contractor", "auditor"]:
            self.assertNotIn("employee-compensation", roles[role]["readCapabilities"])
            self.assertNotIn("payroll", roles[role]["writeCapabilities"])
        connector = read("examples/connector.example.json")
        self.assertEqual(connector["mode"], "disabled")
        self.assertEqual(connector["companyId"], "")
        self.assertFalse(connector["allowedActions"])
        self.assertFalse(connector["readOnlyActions"])
        self.assertFalse(connector["writeActions"])


if __name__ == "__main__":
    unittest.main()
