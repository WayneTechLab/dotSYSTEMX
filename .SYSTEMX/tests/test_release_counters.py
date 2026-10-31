"""Provider counts remain exact or unknown across partial failures."""

import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch


SOURCE = Path(__file__).resolve().parents[1] / "scripts" / "release_counters.py"
SPEC = importlib.util.spec_from_file_location("release_counters_test", SOURCE)
counters = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(counters)


def record(identifier, **fields):
    return {"id": identifier, **fields}


class ReleaseCounterTests(unittest.TestCase):
    def test_published_categories_and_deployment_records_are_distinct(self):
        def page(repository, endpoint, number):
            self.assertEqual(repository, "WayneTechLab/dotSYSTEMX")
            self.assertEqual(number, 1)
            if endpoint == "releases":
                return [record(1, draft=False, tag_name="v1.11.0-alpha.7"),
                        record(2, draft=False, tag_name="v1.11.0-beta.1"),
                        record(3, draft=False, tag_name="media-field-guide-v3.0"),
                        record(4, draft=False, tag_name="special-event"),
                        record(5, draft=True, tag_name="v1.11.0")]
            return [record(10), record(11)]
        with patch.object(counters, "fetch_page", side_effect=page):
            result = counters.snapshot()
        self.assertTrue(result["complete"])
        self.assertEqual(result["publishedReleases"], counters.observed(4))
        self.assertEqual(result["softwareReleases"], counters.observed(2))
        self.assertEqual(result["mediaReleases"], counters.observed(1))
        self.assertEqual(result["otherReleases"], counters.observed(1))
        self.assertEqual(result["deploymentRecords"], counters.observed(2))
        self.assertTrue(result["observedAt"].endswith("Z"))

    def test_provider_failure_does_not_become_zero_or_hide_other_observation(self):
        def page(repository, endpoint, number):
            if endpoint == "releases":
                raise OSError("synthetic provider failure")
            return []
        with patch.object(counters, "fetch_page", side_effect=page):
            result = counters.snapshot()
        self.assertFalse(result["complete"])
        self.assertEqual(result["softwareReleases"], counters.unknown())
        self.assertEqual(result["publishedReleases"], counters.unknown())
        self.assertEqual(result["deploymentRecords"], counters.observed(0))

    def test_duplicate_page_records_refuse_an_exact_count(self):
        first = [record(value, draft=False, tag_name="v1.0.0") for value in range(1, 101)]
        def page(repository, endpoint, number):
            if endpoint == "deployments":
                return []
            return first if number == 1 else [first[-1]]
        with patch.object(counters, "fetch_page", side_effect=page):
            result = counters.snapshot()
        self.assertEqual(result["publishedReleases"], counters.unknown())
        self.assertEqual(result["deploymentRecords"], counters.observed(0))

    def test_invalid_repository_cannot_change_host_or_path(self):
        for value in ("", "owner", "owner/repo/extra", "owner/repo?per_page=1", "https://host/x"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                counters.snapshot(value)


if __name__ == "__main__":
    unittest.main()
