import unittest
from ipaddress import IPv4Address
from types import SimpleNamespace
from unittest.mock import patch
from uuid import UUID, uuid4

import hue_entertainment_pykit.lowl.utils.streaming_util as sut
from hue_entertainment_pykit.lowl.models.light.light_rgb import LightRGB
from hue_entertainment_pykit.lowl.models.light.light_xyb import LightXYB


class _DummyDtls:
    def __init__(self, ip, username, key):
        self.ip = ip
        self.username = username
        self.key = key
        self.created = False
        self.handshook = False
        self.closed = False
        self.sent = []

    def create_dtls_socket(self):
        self.created = True

    def do_handshake(self):
        self.handshook = True

    def close_socket(self):
        self.closed = True

    def send_message(self, msg: bytes):
        self.sent.append(msg)


class TestStreamingUtil(unittest.TestCase):
    def test_class_is_not_instantiable(self):
        with self.assertRaises(TypeError):
            sut.StreamingUtil()  # type: ignore[misc]

    def test_get_keep_alive_interval_constant(self):
        self.assertEqual(sut.StreamingUtil.get_keep_alive_interval(), 9.5)

    def test_start_stream_success(self):
        ip = IPv4Address("192.168.1.2")
        user = "u"
        key = "k"
        ecid = UUID("00000000-0000-0000-0000-000000000000")

        with patch.object(sut, "EntertainmentConfigurationClient") as ecc, \
             patch.object(sut, "DtlsConnection", _DummyDtls):
            dtls = sut.StreamingUtil.start_stream(ip, user, key, ecid)

        # Active called once, Inactive not called on success
        ecc.put_stream_to_active.assert_called_once_with(ip, user, ecid)
        ecc.put_stream_to_inactive.assert_not_called()
        self.assertIsInstance(dtls, _DummyDtls)
        self.assertTrue(dtls.created)
        self.assertTrue(dtls.handshook)

    def test_start_stream_create_socket_failure_raises_and_marks_inactive(self):
        ip = IPv4Address("10.0.0.1")
        user = "u"
        key = "k"
        ecid = UUID("11111111-1111-1111-1111-111111111111")

        class FailingCreate(_DummyDtls):
            def create_dtls_socket(self):
                raise sut.socket_error("boom")

        with patch.object(sut, "EntertainmentConfigurationClient") as ecc, \
             patch.object(sut, "DtlsConnection", FailingCreate):
            with self.assertRaises(sut.StreamStartError):
                sut.StreamingUtil.start_stream(ip, user, key, ecid)

        ecc.put_stream_to_active.assert_called_once_with(ip, user, ecid)
        ecc.put_stream_to_inactive.assert_called_once_with(ip, user, ecid)

    def test_start_stream_handshake_failure_raises_and_marks_inactive(self):
        ip = IPv4Address("10.0.0.2")
        user = "u"
        key = "k"
        ecid = UUID("22222222-2222-2222-2222-222222222222")

        class FailingHandshake(_DummyDtls):
            def do_handshake(self):
                raise sut.socket_error("nope")

        with patch.object(sut, "EntertainmentConfigurationClient") as ecc, \
             patch.object(sut, "DtlsConnection", FailingHandshake):
            with self.assertRaises(sut.StreamStartError):
                sut.StreamingUtil.start_stream(ip, user, key, ecid)

        ecc.put_stream_to_active.assert_called_once_with(ip, user, ecid)
        ecc.put_stream_to_inactive.assert_called_once_with(ip, user, ecid)

    def test_stop_stream_marks_inactive_and_closes_socket(self):
        ip = IPv4Address("10.1.1.1")
        app_key = "app"
        ecid = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
        dtls = _DummyDtls(ip, app_key, "k")

        with patch.object(sut, "EntertainmentConfigurationClient") as ecc:
            sut.StreamingUtil.stop_stream(ip, app_key, ecid, dtls)

        ecc.put_stream_to_inactive.assert_called_once_with(ip, app_key, ecid)
        self.assertTrue(dtls.closed)

    def test_send_input_rgb_builds_and_sends_message(self):
        ecid = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
        dtls = _DummyDtls("ip", "u", "k")
        lights = [LightRGB(uuid4(),
                           "s",
                           uuid4(),
                           0,
                           0,
                           0,
                           1,
                           uuid4())]

        with patch.object(sut, "LightRGB", LightRGB), \
             patch.object(sut, "LightXYB", LightXYB), \
             patch.object(sut.StreamingMessageBuilderUtil, "encode_light_data", return_value=b"CH7") as enc, \
             patch.object(sut.StreamingMessageBuilderUtil, "build", return_value=b"MSG") as build:
            sut.StreamingUtil.send_input(ecid, dtls, lights)

        enc.assert_called_once()
        build.assert_called_once()
        self.assertEqual(dtls.sent, [b"MSG"])

    def test_send_input_xyb_builds_and_sends_message(self):
        ecid = UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
        dtls = _DummyDtls("ip", "u", "k")

        lights = [LightXYB(uuid4(),
                           "s",
                           uuid4(),
                           float(0),
                           float(0),
                           float(0),
                           1,
                           uuid4())]

        with patch.object(sut, "LightRGB", LightRGB), \
             patch.object(sut, "LightXYB", LightXYB), \
             patch.object(sut.StreamingMessageBuilderUtil, "encode_light_data", return_value=b"CH3") as enc, \
             patch.object(sut.StreamingMessageBuilderUtil, "build", return_value=b"MSG2") as build:
            sut.StreamingUtil.send_input(ecid, dtls, lights)

        enc.assert_called_once()
        build.assert_called_once()
        self.assertEqual(dtls.sent, [b"MSG2"])

    def test_send_input_invalid_type_raises(self):
        ecid = UUID("dddddddd-dddd-dddd-dddd-dddddddddddd")
        dtls = _DummyDtls("ip", "u", "k")
        lights = [SimpleNamespace()]  # not RGB or XYB
        with self.assertRaises(Exception) as ctx:
            sut.StreamingUtil.send_input(ecid, dtls, lights)
        self.assertIn("Invalid lights type", str(ctx.exception))

    def test_send_input_encoding_error_wraps_in_custom_exception(self):
        ecid = UUID("eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee")
        dtls = _DummyDtls("ip", "u", "k")
        lights = [LightRGB(uuid4(),
                           "s",
                           uuid4(),
                           0,
                           0,
                           0,
                           1,
                           uuid4())]
        with patch.object(sut, "LightRGB", LightRGB), \
             patch.object(sut, "LightXYB", LightXYB), \
             patch.object(sut.StreamingMessageBuilderUtil, "encode_light_data", side_effect=RuntimeError("bad")):
            with self.assertRaises(sut.EncodingLightDataError):
                sut.StreamingUtil.send_input(ecid, dtls, lights)

    def test_send_input_socket_error_is_caught_and_not_raised(self):
        ecid = UUID("ffffffff-ffff-ffff-ffff-ffffffffffff")
        dtls = _DummyDtls("ip", "u", "k")
        lights = [LightRGB(uuid4(),
                           "s",
                           uuid4(),
                           0,
                           0,
                           0,
                           1,
                           uuid4())]
        with patch.object(sut, "LightRGB", LightRGB), \
             patch.object(sut, "LightXYB", LightXYB), \
             patch.object(sut.StreamingMessageBuilderUtil, "encode_light_data", return_value=b"X"), \
             patch.object(sut.StreamingMessageBuilderUtil, "build", return_value=b"MSG"):
            # Make DTLS raise socket error during send
            def boom(_):
                raise sut.socket_error("net down")
            dtls.send_message = boom  # type: ignore[method-assign]
            # Should not raise
            sut.StreamingUtil.send_input(ecid, dtls, lights)


if __name__ == "__main__":
    unittest.main()
