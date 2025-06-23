import unittest
from unittest.mock import patch, MagicMock
from ipaddress import IPv4Address

from hue_entertainment_pykit.lowl.enums.status_code_enum import StatusCodeEnum
from hue_entertainment_pykit.lowl.exceptions.low_hepk_exceptions import BridgeApiError, BridgeDiscoveryError
from hue_entertainment_pykit.lowl.utils.discovery_util import DiscoveryUtil


class TestDiscoveryUtil(unittest.TestCase):
    def setUp(self):
        self.BridgeApiError = BridgeApiError
        self.BridgeDiscoveryError = BridgeDiscoveryError
        self.StatusCodeEnum = StatusCodeEnum

    @patch("hue_entertainment_pykit.lowl.utils.bridge_builder_util.BridgeBuilderUtil.build_with_app_registration")
    @patch("hue_entertainment_pykit.lowl.utils.bridge_builder_util.BridgeBuilderUtil.build_without_app_registration")
    def test_discover_uses_without_registration_when_available(self, mock_build_without, mock_build_with):
        bridge_mock = MagicMock()
        bridge_mock.does_support_streaming = True
        mock_build_without.return_value = bridge_mock

        result = DiscoveryUtil.discover(
            application_name="app",
            ip_addresses=[IPv4Address("192.168.1.10")]
        )

        self.assertEqual(result, [bridge_mock])
        mock_build_without.assert_called_once()
        mock_build_with.assert_not_called()

    @patch("hue_entertainment_pykit.lowl.utils.bridge_builder_util.BridgeBuilderUtil.build_with_app_registration")
    @patch("hue_entertainment_pykit.lowl.utils.bridge_builder_util.BridgeBuilderUtil.build_without_app_registration")
    def test_discover_falls_back_to_with_registration(self, mock_build_without, mock_build_with):
        mock_build_without.side_effect = self.BridgeApiError("no pre-registration")
        bridge_mock = MagicMock()
        bridge_mock.does_support_streaming = True
        mock_build_with.return_value = bridge_mock

        result = DiscoveryUtil.discover(
            application_name="app",
            ip_addresses=[IPv4Address("192.168.1.11")]
        )

        self.assertEqual(result, [bridge_mock])
        mock_build_without.assert_called_once()
        mock_build_with.assert_called_once()

    @patch("hue_entertainment_pykit.lowl.utils.bridge_builder_util.BridgeBuilderUtil.build_with_app_registration")
    @patch("hue_entertainment_pykit.lowl.utils.bridge_builder_util.BridgeBuilderUtil.build_without_app_registration")
    def test_discover_filters_out_non_streaming_and_raises(self, mock_build_without, mock_build_with):
        bridge_non_streaming_1 = MagicMock()
        bridge_non_streaming_1.does_support_streaming = False
        bridge_non_streaming_2 = MagicMock()
        bridge_non_streaming_2.does_support_streaming = False
        mock_build_without.return_value = bridge_non_streaming_1
        mock_build_with.return_value = bridge_non_streaming_2

        with self.assertRaises(self.BridgeDiscoveryError):
            DiscoveryUtil.discover(
                application_name="app",
                ip_addresses=[IPv4Address("192.168.1.12")]
            )

    @patch("hue_entertainment_pykit.lowl.utils.discovery_util.DiscoveryUtil.discover_ip_addresses_via_cloud")
    @patch("hue_entertainment_pykit.lowl.utils.discovery_util.DiscoveryUtil.discover_ip_addresses_via_mdns")
    def test__discover_ip_addresses_uses_mdns_first(self, mock_mdns, mock_cloud):
        mock_mdns.return_value = [IPv4Address("192.168.1.20")]

        result = DiscoveryUtil.discover_ip_addresses()

        self.assertEqual(result, [IPv4Address("192.168.1.20")])
        mock_mdns.assert_called_once()
        mock_cloud.assert_not_called()

    @patch("hue_entertainment_pykit.lowl.utils.discovery_util.DiscoveryUtil.discover_ip_addresses_via_cloud")
    @patch("hue_entertainment_pykit.lowl.utils.discovery_util.DiscoveryUtil.discover_ip_addresses_via_mdns")
    def test__discover_ip_addresses_falls_back_to_cloud(self, mock_mdns, mock_cloud):
        mock_mdns.side_effect = self.BridgeApiError("mdns failed")
        mock_cloud.return_value = [IPv4Address("10.0.0.55")]

        result = DiscoveryUtil.discover_ip_addresses()

        self.assertEqual(result, [IPv4Address("10.0.0.55")])
        mock_mdns.assert_called_once()
        mock_cloud.assert_called_once()

    @patch("hue_entertainment_pykit.lowl.utils.discovery_util.DiscoveryUtil.discover_ip_addresses_via_cloud")
    @patch("hue_entertainment_pykit.lowl.utils.discovery_util.DiscoveryUtil.discover_ip_addresses_via_mdns")
    def test__discover_ip_addresses_raises_when_none_found(self, mock_mdns, mock_cloud):
        mock_mdns.side_effect = self.BridgeApiError("mdns failed")
        mock_cloud.side_effect = self.BridgeApiError("cloud failed")
        with self.assertRaises(self.BridgeDiscoveryError):
            DiscoveryUtil.discover_ip_addresses()

    @patch("requests.get")
    def test__discover_ip_addresses_via_cloud_parses_response(self, mock_get):
        ok = self.StatusCodeEnum.OK.value
        mock_resp = MagicMock()
        mock_resp.status_code = ok
        mock_resp.reason = "OK"
        mock_resp.json.return_value = [
            {"id": "abc", "internalipaddress": "192.168.1.30"},
            {"id": "def", "internalipaddress": "192.168.1.31"},
        ]
        mock_get.return_value = mock_resp

        result = DiscoveryUtil.discover_ip_addresses_via_cloud()

        self.assertEqual(result, ["192.168.1.30", "192.168.1.31"])
        mock_get.assert_called_once_with(DiscoveryUtil.get_cloud_url(), timeout=10)

    @patch("requests.get")
    def test__discover_ip_addresses_via_cloud_raises_on_bad_status(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.reason = "Internal Server Error"
        mock_get.return_value = mock_resp

        with self.assertRaises(self.BridgeDiscoveryError):
            DiscoveryUtil.discover_ip_addresses_via_cloud()


if __name__ == "__main__":
    unittest.main()