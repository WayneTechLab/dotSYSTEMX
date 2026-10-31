"""The optional service is a bounded read-only protocol, not a host daemon."""

import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE))
sys.path.insert(0, str(SOURCE / "scripts"))
import session_service as service


class SessionServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="systemx-service-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / ".SYSTEMX"
        self.root.mkdir()

    def serve(self, *requests):
        source = io.BytesIO(b"".join(requests))
        output = io.BytesIO()
        result = service.serve(self.root, self.root, source, output)
        responses = [json.loads(line) for line in output.getvalue().splitlines()]
        return result, responses

    def test_explicit_session_exits_on_eof_and_does_not_write(self):
        before = sorted(path.relative_to(self.root).as_posix() for path in self.root.rglob("*"))
        result, responses = self.serve(b'{"id":"p1","method":"ping"}\n',
                                       b'{"id":"p2","method":"capabilities"}\n')
        self.assertEqual(result, {"ended": "eof", "requestsHandled": 2})
        self.assertEqual(responses[0], {"id": "p1", "ok": True, "result": {"alive": True}})
        self.assertFalse(responses[1]["result"]["persistentInstall"])
        self.assertFalse(responses[1]["result"]["networkListener"])
        self.assertFalse(responses[1]["result"]["requiresElevation"])
        self.assertNotIn("privileged", responses[1]["result"])
        self.assertEqual(responses[1]["result"]["hostPrivileges"], "inherited-from-launcher")
        self.assertEqual(before, sorted(path.relative_to(self.root).as_posix() for path in self.root.rglob("*")))

    def test_assessment_is_fixed_and_stop_ends_the_session(self):
        with patch.object(service, "_assess", return_value={"warnings": [], "profile": "all-in-one"}) as assess:
            result, responses = self.serve(b'{"id":"a1","method":"assess"}\n',
                                           b'{"id":"s1","method":"stop"}\n',
                                           b'{"id":"p3","method":"ping"}\n')
        assess.assert_called_once_with(self.root, self.root)
        self.assertEqual(result, {"ended": "requested", "requestsHandled": 2})
        self.assertEqual(responses[0]["result"]["profile"], "all-in-one")
        self.assertEqual(responses[1]["result"]["ended"], "requested")

    def test_agent0_and_setup_io_are_fixed_read_only_methods(self):
        with patch.object(service, "_roster", return_value={"rows": [], "accessGranted": False}) as roster, \
             patch.object(service, "_settings", return_value={"rulesSummary": {"count": 0},
                                                                 "executed": False}) as settings, \
             patch.object(service, "_onboard", return_value={"selection": {"provider": None},
                                                                "valuesReturned": False}) as onboard:
            result, responses = self.serve(
                b'{"id":"r1","method":"roster"}\n',
                b'{"id":"s1","method":"settings"}\n',
                b'{"id":"o1","method":"onboard"}\n')
        self.assertEqual(result, {"ended": "eof", "requestsHandled": 3})
        roster.assert_called_once_with(self.root)
        settings.assert_called_once_with(self.root, self.root)
        onboard.assert_called_once_with(self.root)
        self.assertEqual([row["id"] for row in responses], ["r1", "s1", "o1"])
        self.assertTrue(all(row["ok"] for row in responses))
        self.assertFalse(responses[0]["result"]["accessGranted"])
        self.assertFalse(responses[1]["result"]["executed"])
        self.assertIsNone(responses[2]["result"]["selection"]["provider"])

    def test_rejects_extra_fields_duplicate_fields_and_commands(self):
        result, responses = self.serve(
            b'{"id":"a1","method":"ping","command":"rm"}\n',
            b'{"id":"a2","id":"a3","method":"ping"}\n',
            b'{"id":"a4","method":"execute"}\n',
            b'{"id":"a5","method":"roster","project":"other"}\n',
            b'{"id":"ok","method":"ping"}\n')
        self.assertEqual(result["requestsHandled"], 5)
        self.assertEqual([row["ok"] for row in responses], [False, False, False, False, True])
        self.assertTrue(all("rm" not in json.dumps(row) for row in responses))

    def test_oversized_request_ends_without_echoing_payload(self):
        result, responses = self.serve(b"X" * (service.MAX_LINE_BYTES + 1))
        self.assertEqual(result["ended"], "protocol-limit")
        self.assertFalse(responses[0]["ok"])
        self.assertNotIn("XXX", json.dumps(responses[0]))

    def test_assessment_failure_is_generic_and_session_continues(self):
        with patch.object(service, "_assess", side_effect=RuntimeError("SECRET_VALUE_IN_ERROR")):
            result, responses = self.serve(b'{"id":"a1","method":"assess"}\n',
                                           b'{"id":"p1","method":"ping"}\n')
        self.assertEqual(result["requestsHandled"], 2)
        self.assertFalse(responses[0]["ok"])
        self.assertNotIn("SECRET_VALUE_IN_ERROR", json.dumps(responses))
        self.assertTrue(responses[1]["ok"])

    def test_oversized_assessment_result_is_bounded_with_same_id(self):
        with patch.object(service, "_assess", return_value={"private": "X" * service.MAX_RESPONSE_BYTES}):
            result, responses = self.serve(b'{"id":"a1","method":"assess"}\n')
        self.assertEqual(result["requestsHandled"], 1)
        self.assertEqual(responses[0]["id"], "a1")
        self.assertFalse(responses[0]["ok"])
        self.assertNotIn("XXXX", json.dumps(responses[0]))

    def test_child_scope_is_explicit_and_exact_case(self):
        child = Path(self.temp.name) / "project" / ".SYSTEMXP"
        child.mkdir(parents=True)
        self.assertEqual(service.status(child)["scope"], str(child))
        link = Path(self.temp.name) / "linked-project" / ".SYSTEMXP"
        link.parent.mkdir()
        link.symlink_to(child, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "real exact-case"):
            service.status(link)


if __name__ == "__main__":
    unittest.main()
