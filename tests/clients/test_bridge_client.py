import unittest
import uuid
from ipaddress import IPv4Address
from types import SimpleNamespace
from unittest.mock import patch

from hue_entertainment_pykit.lowl.clients.bridge_client import BridgeClient
from hue_entertainment_pykit.lowl.enums.endpoint_enum import EndpointEnum
from hue_entertainment_pykit.lowl.enums.http_method_enum import HttpMethodEnum
from hue_entertainment_pykit.lowl.models.bridge.hue.bridge_api_hue import BridgeApiHue
from hue_entertainment_pykit.lowl.models.bridge.hue.bridge_config_hue import BridgeConfigHue
from hue_entertainment_pykit.lowl.models.bridge.hue.bridge_device_hue import BridgeDeviceHue
from hue_entertainment_pykit.lowl.models.bridge.hue.bridge_hue import BridgeHue
from hue_entertainment_pykit.lowl.models.request.request_body import RequestBody
from hue_entertainment_pykit.lowl.models.request.request_header import RequestHeader


def _extract_dict_from_request_body(rb: RequestBody) -> dict:
    for v in vars(rb).values():
        if isinstance(v, dict):
            return v
    raise AssertionError("RequestBody does not contain an underlying dict")


def _extract_username_from_header(hd: RequestHeader) -> str:
    for k, v in vars(hd).items():
        if v == 'application/json':
            continue
        if isinstance(v, str):
            return v
    raise AssertionError("RequestHeader does not contain a username/app-key string")


class TestBridgeClient(unittest.TestCase):
    def test_generate_api_keys_posts_and_returns_model(self):
        ip = IPv4Address("192.168.1.50")
        app = "tester"
        body_out = {"username": "u", "clientkey": "ck"}

        def side_effect(method, endpoint, ip_arg, **kwargs):
            self.assertEqual(method, HttpMethodEnum.POST)
            self.assertEqual(endpoint, EndpointEnum.API)
            self.assertEqual(ip_arg, ip)
            self.assertIn("body", kwargs)
            self.assertIsInstance(kwargs["body"], RequestBody)
            payload = _extract_dict_from_request_body(kwargs["body"])
            self.assertEqual(payload["devicetype"], f"hep#{app}")
            self.assertTrue(payload["generateclientkey"])
            return body_out, {"h": "v"}

        with patch("hue_entertainment_pykit.lowl.models.bridge.hue.bridge_api_hue.BridgeApiHue", SimpleNamespace), \
                patch.object(BridgeClient, "_send_request", side_effect=side_effect) as mocked:
            model = BridgeClient.generate_api_keys(ip, app)

        mocked.assert_called_once()

        self.assertIsInstance(model, BridgeApiHue)
        self.assertEqual(model.username, "u")
        self.assertEqual(model.clientkey, "ck")

    def test_fetch_bridge_gets_and_uses_header(self):
        ip = IPv4Address("192.168.1.60")
        hue_application_key = "user123"
        id = uuid.uuid4()
        rid = uuid.uuid4()
        body_out = [{"id": id, 'owner': {'rid': rid}, 'bridge_id': '1'}]

        def side_effect(method, endpoint, ip_arg, **kwargs):
            self.assertEqual(method, HttpMethodEnum.GET)
            self.assertEqual(endpoint, EndpointEnum.BRIDGE)
            self.assertEqual(ip_arg, ip)
            self.assertIn("header", kwargs)
            self.assertIsInstance(kwargs["header"], RequestHeader)
            self.assertEqual(_extract_username_from_header(kwargs["header"]), hue_application_key)
            return body_out, {"x": "y"}

        with patch("hue_entertainment_pykit.lowl.models.bridge.hue.bridge_hue.BridgeHue", SimpleNamespace), \
                patch.object(BridgeClient, "_send_request", side_effect=side_effect) as mocked:
            model = BridgeClient.fetch_bridge(ip, hue_application_key)

        mocked.assert_called_once()
        self.assertIsInstance(model, BridgeHue)
        self.assertEqual(model.id, id)
        self.assertEqual(model.owner.rid, rid)
        self.assertEqual(model.bridge_id, "1")

    def test_fetch_config_gets_and_returns_config_model(self):
        ip = IPv4Address("192.168.1.61")
        username = "u"
        body_out = {"swversion": '1', 'bridgeid': '1'}

        def side_effect(method, endpoint, ip_arg, **kwargs):
            self.assertEqual(method, HttpMethodEnum.GET)
            self.assertEqual(endpoint, EndpointEnum.CONFIG)
            self.assertEqual(ip_arg, ip)
            self.assertIsInstance(kwargs.get("header"), RequestHeader)
            self.assertEqual(_extract_username_from_header(kwargs["header"]), username)
            return body_out, {}

        with patch("hue_entertainment_pykit.lowl.models.bridge.hue.bridge_config_hue.BridgeConfigHue",
                   SimpleNamespace), \
                patch.object(BridgeClient, "_send_request", side_effect=side_effect) as mocked:
            model = BridgeClient.fetch_config(ip, username)

        mocked.assert_called_once()
        self.assertIsInstance(model, BridgeConfigHue)
        self.assertEqual(model.swversion, '1')
        self.assertEqual(model.bridgeid, '1')

    def test_fetch_device_gets_with_query_rid_and_returns_model(self):
        ip = IPv4Address("192.168.1.62")
        username = "u2"
        id = uuid.uuid4()
        rid = uuid.uuid4()
        body_out = [{
            'id': id,
            'metadata': {'name': '1'},
            'services': [{'rid': rid, 'rtype': '1'}]
        }]

        def side_effect(method, endpoint, ip_arg, **kwargs):
            self.assertEqual(method, HttpMethodEnum.GET)
            self.assertEqual(endpoint, EndpointEnum.DEVICE)
            self.assertEqual(ip_arg, ip)
            self.assertIsInstance(kwargs.get("header"), RequestHeader)
            self.assertEqual(_extract_username_from_header(kwargs["header"]), username)
            self.assertIn("body", kwargs)
            payload = _extract_dict_from_request_body(kwargs["body"])
            self.assertEqual(payload.get("query_rid"), str(rid))
            return body_out, {"X": "Y"}

        with patch("hue_entertainment_pykit.lowl.models.bridge.hue.bridge_device_hue.BridgeDeviceHue",
                   SimpleNamespace), \
                patch.object(BridgeClient, "_send_request", side_effect=side_effect) as mocked:
            model = BridgeClient.fetch_device(ip, username, rid)

        mocked.assert_called_once()
        self.assertIsInstance(model, BridgeDeviceHue)
        self.assertEqual(model.id, id)
        self.assertEqual(model.metadata.name, '1')
        self.assertEqual(model.services[0].rid, rid)
        self.assertEqual(model.services[0].rtype, '1')


if __name__ == "__main__":
    unittest.main()
