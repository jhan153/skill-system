import unittest

from kanboard_plan_sync.kanboard_client import KanboardClient, KanboardError


class FakeTransport:
    """Records JSON-RPC payloads and returns canned results."""

    def __init__(self, results):
        self.results = results  # list of result/error dicts per call
        self.calls = []

    def __call__(self, payload):
        self.calls.append(payload)
        return self.results[len(self.calls) - 1]


class KanboardClientTest(unittest.TestCase):
    def test_call_returns_result_and_builds_payload(self):
        transport = FakeTransport([{"jsonrpc": "2.0", "id": 1, "result": 42}])
        client = KanboardClient("http://x", token="t", transport=transport)
        out = client.call("createProject", name="P")
        self.assertEqual(out, 42)
        payload = transport.calls[0]
        self.assertEqual(payload["method"], "createProject")
        self.assertEqual(payload["params"], {"name": "P"})
        self.assertEqual(payload["jsonrpc"], "2.0")

    def test_error_raises(self):
        transport = FakeTransport(
            [{"jsonrpc": "2.0", "id": 1, "error": {"code": -32601, "message": "nope"}}]
        )
        client = KanboardClient("http://x", token="t", transport=transport)
        with self.assertRaises(KanboardError):
            client.call("badMethod")

    def test_ids_increment(self):
        transport = FakeTransport([{"result": 1}, {"result": 2}])
        client = KanboardClient("http://x", token="t", transport=transport)
        client.call("a")
        client.call("b")
        self.assertEqual(transport.calls[0]["id"], 1)
        self.assertEqual(transport.calls[1]["id"], 2)

    def test_wrappers_use_expected_methods(self):
        transport = FakeTransport([{"result": {"id": 7}}, {"result": 99}])
        client = KanboardClient("http://x", token="t", transport=transport)
        client.get_project_by_name("P")
        client.create_task(project_id=1, title="T", reference="plan:A1", column_id=2)
        self.assertEqual(transport.calls[0]["method"], "getProjectByName")
        self.assertEqual(transport.calls[1]["method"], "createTask")
        self.assertEqual(transport.calls[1]["params"]["reference"], "plan:A1")

    def test_http_transport_requires_token(self):
        client = KanboardClient("http://x", token=None)  # default http transport
        with self.assertRaises(KanboardError):
            client.call("getProjectByName", name="P")


if __name__ == "__main__":
    unittest.main()
