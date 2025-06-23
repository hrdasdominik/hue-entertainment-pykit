import unittest
from ipaddress import IPv4Address
from unittest.mock import patch, ANY

import hue_entertainment_pykit.lowl.clients.light_client as lc


class TestLightClient(unittest.TestCase):
    def setUp(self):
        self.ip = IPv4Address("192.168.1.88")
        self.username = "tester"

    @patch("hue_entertainment_pykit.lowl.clients.light_client.LightHue")
    @patch("hue_entertainment_pykit.lowl.clients.light_client.RequestHeader")
    @patch.object(lc.LightClient, "_send_request")
    def test_fetch_lights_from_bridge_happy_path(self, mock_send, mock_header, mock_model):
        body = [
            {"id": "1", "name": "Lamp A"},
            {"id": "2", "name": "Lamp B"},
        ]
        mock_send.return_value = (body, {"dummy": True})
        mock_model.side_effect = ["L:1", "L:2"]

        result = lc.LightClient.fetch_lights_from_bridge(self.ip, self.username)

        self.assertEqual(result, ["L:1", "L:2"])

        mock_send.assert_called_once_with(
            lc.HttpMethodEnum.GET,
            lc.EndpointEnum.LIGHT,
            self.ip,
            ANY,
        )

        mock_header.assert_called_once_with(self.username)

        mock_model.assert_any_call(**{"id": "1", "name": "Lamp A"})
        mock_model.assert_any_call(**{"id": "2", "name": "Lamp B"})

    @patch("hue_entertainment_pykit.lowl.clients.light_client.LightHue")
    @patch("hue_entertainment_pykit.lowl.clients.light_client.RequestHeader")
    @patch.object(lc.LightClient, "_send_request")
    def test_fetch_lights_from_bridge_empty_list(self, mock_send, mock_header, mock_model):
        mock_send.return_value = ([], {"h": "x"})

        result = lc.LightClient.fetch_lights_from_bridge(self.ip, self.username)

        self.assertEqual(result, [])
        mock_send.assert_called_once()
        mock_header.assert_called_once_with(self.username)
        mock_model.assert_not_called()

    @patch("hue_entertainment_pykit.lowl.clients.light_client.RequestHeader")
    @patch.object(lc.LightClient, "_send_request")
    def test_fetch_lights_from_bridge_propagates_error(self, mock_send, mock_header):
        mock_send.side_effect = RuntimeError("network poof")

        with self.assertRaises(RuntimeError):
            lc.LightClient.fetch_lights_from_bridge(self.ip, self.username)
        mock_header.assert_called_once_with(self.username)


if __name__ == "__main__":
    unittest.main()
