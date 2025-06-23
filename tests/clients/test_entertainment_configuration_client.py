import unittest
from ipaddress import IPv4Address
from unittest.mock import patch, ANY
from uuid import UUID

import hue_entertainment_pykit.lowl.clients.entertainment_configuration_client as ecc


class DummyRequestBody:
    def __init__(self):
        self.data = {}

    def set_key_and_or_value(self, key, value):
        self.data[key] = value
        return self


class TestEntertainmentConfigurationClient(unittest.TestCase):
    def setUp(self):
        self.ip = IPv4Address("192.168.1.50")
        self.hak = "test-app-key"
        self.username = "u-123"
        self.ec_id = UUID("12345678-1234-5678-1234-567812345678")

    @patch("hue_entertainment_pykit.lowl.clients.entertainment_configuration_client.EntertainmentConfigurationHue")
    @patch("hue_entertainment_pykit.lowl.clients.entertainment_configuration_client.RequestHeader")
    @patch.object(ecc.EntertainmentConfigurationClient, "_send_request")
    def test_fetch_all(self, mock_send, mock_header, mock_model):
        body = [{"id": "a"}, {"id": "b"}]
        mock_send.return_value = (body, {"h": "x"})
        mock_model.side_effect = ["EC:a", "EC:b"]

        result = ecc.EntertainmentConfigurationClient.fetch_all(self.ip, self.hak)

        self.assertEqual(result, ["EC:a", "EC:b"])
        mock_send.assert_called_once_with(
            ecc.HttpMethodEnum.GET,
            ecc.EndpointEnum.ENTERTAINMENT_CONFIGURATION,
            self.ip,
            ANY,
        )
        mock_header.assert_called_once_with(self.hak)

    @patch("hue_entertainment_pykit.lowl.clients.entertainment_configuration_client.EntertainmentConfigurationHue")
    @patch("hue_entertainment_pykit.lowl.clients.entertainment_configuration_client.RequestHeader")
    @patch.object(ecc.EntertainmentConfigurationClient, "_send_request")
    def test_fetch_by_id(self, mock_send, mock_header, mock_model):
        body = [{"id": "only-one"}]
        mock_send.return_value = (body, {"h": "x"})
        mock_model.return_value = "EC:only-one"

        result = ecc.EntertainmentConfigurationClient.fetch_by_id(self.ec_id, self.ip, self.hak)

        self.assertEqual(result, "EC:only-one")
        mock_send.assert_called_once_with(
            ecc.HttpMethodEnum.GET,
            ecc.EndpointEnum.ENTERTAINMENT_CONFIGURATION,
            self.ip,
            ANY,
            ANY,
        )
        called_args = mock_send.call_args.args
        req_body = called_args[4]
        self.assertIsInstance(req_body, ecc.RequestBody)
        mock_header.assert_called_once_with(self.hak)

    @patch("hue_entertainment_pykit.lowl.clients.entertainment_configuration_client.RequestBody",
           side_effect=lambda *a, **k: DummyRequestBody())
    @patch("hue_entertainment_pykit.lowl.clients.entertainment_configuration_client.RequestHeader")
    @patch.object(ecc.EntertainmentConfigurationClient, "_send_request")
    def test_put_stream_to_active(self, mock_send, mock_header, mock_body_ctor):
        ecc.EntertainmentConfigurationClient.put_stream_to_active(self.ip, self.username, self.ec_id)

        mock_send.assert_called_once()
        args = mock_send.call_args.args
        self.assertEqual(args[0], ecc.HttpMethodEnum.PUT)
        self.assertEqual(args[1], ecc.EndpointEnum.ENTERTAINMENT_CONFIGURATION)
        self.assertEqual(args[2], self.ip)
        mock_header.assert_called_once_with(self.username)
        payload = args[4]
        self.assertIsInstance(payload, DummyRequestBody)
        self.assertEqual(payload.data.get("query_id"), self.ec_id)
        self.assertEqual(payload.data.get("action"), "start")

    @patch("hue_entertainment_pykit.lowl.clients.entertainment_configuration_client.RequestBody",
           side_effect=lambda *a, **k: DummyRequestBody())
    @patch("hue_entertainment_pykit.lowl.clients.entertainment_configuration_client.RequestHeader")
    @patch.object(ecc.EntertainmentConfigurationClient, "_send_request")
    def test_put_stream_to_inactive(self, mock_send, mock_header, mock_body_ctor):
        ecc.EntertainmentConfigurationClient.put_stream_to_inactive(self.ip, self.hak, self.ec_id)

        mock_send.assert_called_once()
        args = mock_send.call_args.args
        self.assertEqual(args[0], ecc.HttpMethodEnum.PUT)
        self.assertEqual(args[1], ecc.EndpointEnum.ENTERTAINMENT_CONFIGURATION)
        self.assertEqual(args[2], self.ip)
        mock_header.assert_called_once_with(self.hak)
        payload = args[4]
        self.assertIsInstance(payload, DummyRequestBody)
        self.assertEqual(payload.data.get("query_id"), self.ec_id)
        self.assertEqual(payload.data.get("action"), "stop")


if __name__ == "__main__":
    unittest.main()
