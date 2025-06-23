import json
import os
import tempfile
import unittest
from ipaddress import IPv4Address
from unittest.mock import patch

from hue_entertainment_pykit.lowl.models.bridge.hue.bridge_api_hue import BridgeApiHue
from hue_entertainment_pykit.lowl.utils.file_handler_util import FileHandlerUtil

class TestFileHandlerUtil(unittest.TestCase):
    def test_read_json_file_not_found_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing_path = os.path.join(tmp, "nope.json")
            with self.assertRaises(FileNotFoundError):
                FileHandlerUtil.read_json(missing_path)

    def test_read_json_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "data.json")
            payload = {"a": 1, "b": [1, 2, 3]}
            with open(path, "w", encoding="utf-8") as f:
                json.dump(payload, f)
            out = FileHandlerUtil.read_json(path)
            self.assertEqual(out, payload)

    def test_write_json_writes_dict(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "sub", "data.json")
            payload = {"x": 42, "y": "z"}

            FileHandlerUtil.write_json(path, payload)
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertEqual(data, payload)

    def test_save_and_load_bridge_api_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            bridge_file = os.path.join(tmp, "bridge_api.json")
            ip = IPv4Address("192.168.1.5")
            model_in = BridgeApiHue(username="test-bridge", clientkey="7")

            with patch.object(FileHandlerUtil, "BRIDGE_API_PATH", bridge_file):
                with patch("hue_entertainment_pykit.lowl.models.bridge.hue.bridge_api_hue.BridgeApiHue", BridgeApiHue):
                    FileHandlerUtil.save_bridge_api(ip, model_in)
                    loaded = FileHandlerUtil.load_bridge_api(ip)

            self.assertIsInstance(loaded, BridgeApiHue)
            self.assertEqual(loaded.model_dump(), model_in.model_dump())

    def test_load_bridge_api_missing_ip_raises_keyerror(self):
        with tempfile.TemporaryDirectory() as tmp:
            bridge_file = os.path.join(tmp, "bridge_api.json")
            present_ip = IPv4Address("10.0.0.10")
            absent_ip = IPv4Address("10.0.0.11")
            model_in = BridgeApiHue(username="only-one", clientkey="1")

            with patch.object(FileHandlerUtil, "BRIDGE_API_PATH", bridge_file):
                with patch("hue_entertainment_pykit.lowl.models.bridge.hue.bridge_api_hue.BridgeApiHue", BridgeApiHue):
                    FileHandlerUtil.save_bridge_api(present_ip, model_in)

                    with self.assertRaises(KeyError):
                        FileHandlerUtil.load_bridge_api(absent_ip)


if __name__ == "__main__":
    unittest.main()