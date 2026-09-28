"""Public alpha IDs, stable isolation, ordering, and bounded release discovery."""

import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("versions_manager_test", SOURCE / "manager.py")
manager = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(manager)


def release(version, prerelease=False, draft=False):
    return {"tag_name": "v" + version, "prerelease": prerelease, "draft": draft}


class VersionTests(unittest.TestCase):
    def test_exact_ids_and_python_mapping(self):
        for value in ("0.0.0", "1.5.0", "1.6.0-alpha.1", "1.6.0-alpha.10"):
            self.assertEqual(manager.version_id(value), value)
        self.assertEqual(manager.package_version("1.6.0-alpha.1"), "1.6.0a1")
        self.assertEqual(manager.package_version("1.5.0"), "1.5.0")

    def test_ambiguous_and_escaping_ids_rejected(self):
        for value in (None, 1, "v1.6.0", "Alpha1", "01.6.0", "1.6.0-alpha.0",
                      "1.6.0-alpha.01", "1.6.0a1", "1.6.0-beta.1", "1.6.0+local",
                      "1.6.0-alpha.1/../x", "1.6.0\n", "1.6.٠"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                manager.version_id(value)

    def test_numeric_order_and_final_graduation(self):
        expected = ["1.5.0", "1.6.0-alpha.2", "1.6.0-alpha.10", "1.6.0", "1.6.1-alpha.1", "2.0.0"]
        self.assertEqual(sorted(reversed(expected), key=manager.version_key), expected)

    def test_stable_never_accepts_alpha_or_drafts(self):
        for item in (release("1.6.0-alpha.1"), release("1.6.0-alpha.1", True),
                     release("1.6.0", True), release("1.6.0", draft=True), []):
            with self.subTest(item=item), patch.object(manager, "get_url", return_value=json.dumps(item).encode()):
                with self.assertRaises(ValueError):
                    manager.latest_version()

    def test_stable_uses_stable_endpoint(self):
        with patch.object(manager, "get_url", return_value=json.dumps(release("1.5.0")).encode()) as fetch:
            self.assertEqual(manager.latest_version(), "1.5.0")
            self.assertTrue(fetch.call_args.args[0].endswith("/releases/latest"))

    def test_alpha_discovery_orders_and_ignores_mislabeled_releases(self):
        values = [release("1.6.0-alpha.2", True), release("1.5.0"), release("1.6.0-alpha.10", True),
                  release("2.0.0-alpha.1"), release("9.0.0", True), release("9.0.0", draft=True),
                  release("latest"), release("8.0.0-beta.1", True)]
        with patch.object(manager, "get_url", return_value=json.dumps(values).encode()):
            self.assertEqual(manager.latest_version(channel="alpha"), "1.6.0-alpha.10")
        values.append(release("1.6.0"))
        with patch.object(manager, "get_url", return_value=json.dumps(values).encode()):
            self.assertEqual(manager.latest_version(channel="alpha"), "1.6.0")

    def test_discovery_paginates_and_fails_on_truncation(self):
        page = [release("1.5.0")] * 100
        with patch.object(manager, "get_url", side_effect=[json.dumps(page).encode(),
                         json.dumps([release("1.6.0-alpha.1", True)]).encode()]) as fetch:
            self.assertEqual(manager.latest_version(channel="alpha"), "1.6.0-alpha.1")
            self.assertTrue(fetch.call_args.args[0].endswith("page=2"))
        with patch.object(manager, "get_url", return_value=json.dumps(page).encode()) as fetch:
            with self.assertRaisesRegex(ValueError, "limit reached"):
                manager.latest_version(channel="alpha")
            self.assertEqual(fetch.call_count, 10)

    def test_empty_or_invalid_discovery_fails_closed(self):
        for values in ([], {}, [release("1.6.0-alpha.1")]):
            with self.subTest(values=values), patch.object(manager, "get_url", return_value=json.dumps(values).encode()):
                with self.assertRaises(ValueError):
                    manager.latest_version(channel="alpha")

    def test_unknown_channel_does_not_fetch(self):
        with patch.object(manager, "get_url", side_effect=AssertionError("No network expected")):
            with self.assertRaises(ValueError):
                manager.latest_version(channel="nightly")


if __name__ == "__main__":
    unittest.main()
