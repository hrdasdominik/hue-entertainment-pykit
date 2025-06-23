import unittest
from ipaddress import IPv4Address
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

from hue_entertainment_pykit.lowl.exceptions.low_hepk_exceptions import LoadingDataError, BridgeApiError
from hue_entertainment_pykit.lowl.utils.bridge_builder_util import BridgeBuilderUtil


class TestBridgeBuilderUtil(unittest.TestCase):
    def setUp(self):
        self.ip = IPv4Address("192.168.1.2")

    @patch("hue_entertainment_pykit.lowl.utils.bridge_builder_util.BridgeCombinationHue")
    @patch("hue_entertainment_pykit.lowl.utils.bridge_builder_util.FileHandlerUtil.save_bridge_api")
    @patch("hue_entertainment_pykit.lowl.utils.bridge_builder_util.BridgeClient.fetch_device")
    @patch("hue_entertainment_pykit.lowl.utils.bridge_builder_util.BridgeClient.fetch_bridge")
    @patch("hue_entertainment_pykit.lowl.utils.bridge_builder_util.BridgeClient.fetch_config")
    @patch("hue_entertainment_pykit.lowl.utils.bridge_builder_util.BridgeClient.generate_api_keys")
    def test_build_with_registration_success(self, mock_gen_keys, mock_fetch_config,
                                             mock_fetch_bridge, mock_fetch_device,
                                             mock_save_api, mock_combination):
        mock_api = MagicMock()
        mock_api.username = "user123"
        mock_gen_keys.return_value = mock_api

        mock_config = MagicMock()
        mock_config.swversion = str(BridgeBuilderUtil.get_min_swversion() + 1)
        mock_fetch_config.return_value = mock_config

        mock_bridge = MagicMock()
        mock_bridge.owner = SimpleNamespace(rid="RID-1")
        mock_fetch_bridge.return_value = mock_bridge

        mock_device = MagicMock()
        mock_fetch_device.return_value = mock_device

        combo_sentinel = object()
        mock_combination.return_value = combo_sentinel

        result = BridgeBuilderUtil.build_with_app_registration(self.ip, application_name="app")

        self.assertIs(result, combo_sentinel)
        mock_save_api.assert_called_once_with(self.ip, mock_api)
        mock_fetch_config.assert_called_once_with(self.ip, mock_api.username)
        mock_fetch_bridge.assert_called_once_with(self.ip, mock_api.username)
        mock_fetch_device.assert_called_once_with(self.ip, mock_api.username, "RID-1")

        called_kwargs = mock_combination.call_args.kwargs
        self.assertTrue(called_kwargs.get("does_support_streaming"))
        self.assertEqual(called_kwargs.get("ip_address"), self.ip)
        self.assertEqual(called_kwargs.get("bridge"), mock_bridge)
        self.assertEqual(called_kwargs.get("device"), mock_device)
        self.assertEqual(called_kwargs.get("config"), mock_config)
        self.assertEqual(called_kwargs.get("api"), mock_api)

    @patch("hue_entertainment_pykit.lowl.utils.bridge_builder_util.BridgeClient.generate_api_keys",
           side_effect=BridgeApiError("kaboom"))
    def test_build_with_registration_failure_raises(self, _):
        with self.assertRaises(BridgeApiError) as ctx:
            BridgeBuilderUtil.build_with_app_registration(self.ip, application_name="app")
        self.assertIn(str(self.ip), str(ctx.exception))

    @patch("hue_entertainment_pykit.lowl.utils.bridge_builder_util.BridgeCombinationHue")
    @patch("hue_entertainment_pykit.lowl.utils.bridge_builder_util.BridgeClient.fetch_device")
    @patch("hue_entertainment_pykit.lowl.utils.bridge_builder_util.BridgeClient.fetch_bridge")
    @patch("hue_entertainment_pykit.lowl.utils.bridge_builder_util.BridgeClient.fetch_config")
    @patch("hue_entertainment_pykit.lowl.utils.bridge_builder_util.FileHandlerUtil.load_bridge_api")
    def test_build_without_registration_success(self, mock_load_api, mock_fetch_config,
                                                mock_fetch_bridge, mock_fetch_device, mock_combination):
        mock_api = MagicMock()
        mock_api.username = "userXYZ"
        mock_load_api.return_value = mock_api

        mock_config = MagicMock()
        mock_config.swversion = str(BridgeBuilderUtil.get_min_swversion())
        mock_fetch_config.return_value = mock_config

        mock_bridge = MagicMock()
        mock_bridge.owner = SimpleNamespace(rid="RID-2")
        mock_fetch_bridge.return_value = mock_bridge

        mock_device = MagicMock()
        mock_fetch_device.return_value = mock_device

        combo_sentinel = object()
        mock_combination.return_value = combo_sentinel

        result = BridgeBuilderUtil.build_without_app_registration(self.ip)

        self.assertIs(result, combo_sentinel)
        mock_fetch_device.assert_called_once_with(self.ip, mock_api.username, "RID-2")
        called_kwargs = mock_combination.call_args.kwargs
        self.assertTrue(called_kwargs.get("does_support_streaming"))

    @patch("hue_entertainment_pykit.lowl.utils.bridge_builder_util.FileHandlerUtil.load_bridge_api",
           side_effect=FileNotFoundError("nope"))
    def test_build_without_registration_no_file(self, _):
        with self.assertRaises(LoadingDataError) as ctx:
            BridgeBuilderUtil.build_without_app_registration(self.ip)
        self.assertIn("No existing bridge API data found.", str(ctx.exception))

    @patch("hue_entertainment_pykit.lowl.utils.bridge_builder_util.FileHandlerUtil.load_bridge_api",
           side_effect=Exception("read fail"))
    def test_build_without_registration_read_fail(self, _):
        with self.assertRaises(LoadingDataError) as ctx:
            BridgeBuilderUtil.build_without_app_registration(self.ip)
        self.assertIn("Failed to read bridge API.", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
