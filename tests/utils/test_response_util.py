import unittest
from requests.structures import CaseInsensitiveDict

from hue_entertainment_pykit.lowl.exceptions.low_hepk_exceptions import BridgeApiError
from hue_entertainment_pykit.lowl.utils.response_util import ResponseUtil
from hue_entertainment_pykit.lowl.exceptions.link_button_not_pressed_exception import (
    LinkButtonNotPressedError,
)


class _FakeResponse:
    def __init__(self, status_code=200, reason="OK", headers=None, body=None):
        self.status_code = status_code
        self.reason = reason
        self.headers = headers or CaseInsensitiveDict()
        self._body = body if body is not None else {}

    def json(self):
        return self._body


class TestResponseUtil(unittest.TestCase):
    def test_non_ok_status_raises_bridge_exception(self):
        resp = _FakeResponse(status_code=400, reason="Bad Request")
        with self.assertRaises(BridgeApiError) as ctx:
            ResponseUtil.unwrap(resp)
        self.assertIn("Response status: 400, Bad Request", str(ctx.exception))

    def test_error_type_101_raises_link_button_exception(self):
        body = {"error": {"type": 101, "address": "/", "description": "link not pressed"}}
        resp = _FakeResponse(status_code=200, body=body)
        with self.assertRaises(LinkButtonNotPressedError) as ctx:
            ResponseUtil.unwrap(resp)
        self.assertIn("Hue Bridge link button not pressed.", str(ctx.exception))

    def test_error_other_type_raises_bridge_exception(self):
        body = {"error": {"type": 901, "address": "/", "description": "some failure"}}
        resp = _FakeResponse(status_code=200, body=body)
        with self.assertRaises(BridgeApiError) as ctx:
            ResponseUtil.unwrap(resp)
        self.assertIn("Bridge communication error: some failure", str(ctx.exception))

    def test_returns_data_tuple_when_data_key_present(self):
        headers = CaseInsensitiveDict({"X-Test": "1"})
        payload = {"data": {"a": 1, "b": 2}}
        resp = _FakeResponse(status_code=200, headers=headers, body=payload)
        data, out_headers = ResponseUtil.unwrap(resp)
        self.assertEqual(data, {"a": 1, "b": 2})
        self.assertEqual(out_headers["X-Test"], "1")

    def test_returns_full_body_when_apiversion_present(self):
        headers = CaseInsensitiveDict({"X-Api": "v2"})
        payload = {"apiversion": "2.0", "name": "bridge"}
        resp = _FakeResponse(status_code=200, headers=headers, body=payload)
        data, out_headers = ResponseUtil.unwrap(resp)
        self.assertEqual(data, payload)
        self.assertEqual(out_headers["X-Api"], "v2")

    def test_list_success_shape_returns_success_dict(self):
        headers = CaseInsensitiveDict({"K": "V"})
        payload = [{"success": {"/lights/1/state": {"on": True}}}]
        resp = _FakeResponse(status_code=200, headers=headers, body=payload)
        data, out_headers = ResponseUtil.unwrap(resp)
        self.assertEqual(data, {"/lights/1/state": {"on": True}})
        self.assertEqual(out_headers["K"], "V")

    def test_list_error_shape_raises_bridge_exception(self):
        payload = [{"error": {"type": 3, "address": "/lights/999", "description": "resource, not available"}}]
        resp = _FakeResponse(status_code=200, body=payload)
        with self.assertRaises(BridgeApiError) as ctx:
            ResponseUtil.unwrap(resp)
        self.assertIn("resource, not available", str(ctx.exception))

    def test_unexpected_shape_raises_api_exception(self):
        payload = {"unexpected": True}
        resp = _FakeResponse(status_code=200, body=payload)
        with self.assertRaises(BridgeApiError) as ctx:
            ResponseUtil.unwrap(resp)
        self.assertIn("Response data has changed", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()