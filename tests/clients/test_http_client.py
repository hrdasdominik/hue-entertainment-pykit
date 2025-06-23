import unittest
from ipaddress import IPv4Address
from unittest.mock import patch, MagicMock
from uuid import UUID

import hue_entertainment_pykit.lowl.clients.http_client as hc


class TestHttpClient(unittest.TestCase):
    def setUp(self):
        self.ip = IPv4Address("192.168.1.70")
        self.endpoint = hc.EndpointEnum.ENTERTAINMENT_CONFIGURATION

    @patch("hue_entertainment_pykit.lowl.clients.http_client.ResponseUtil.unwrap")
    @patch("hue_entertainment_pykit.lowl.clients.http_client.requests.request")
    def test_send_request_basic_no_header_no_body(self, mock_request, mock_unwrap):
        mock_response = MagicMock(name="Response")
        mock_request.return_value = mock_response
        mock_unwrap.return_value = ([], {})

        result = hc.HttpClient._send_request(
            hc.HttpMethodEnum.GET, self.endpoint, self.ip
        )

        expected_url = f"https://{self.ip}/{self.endpoint.value}"
        mock_request.assert_called_once_with(
            hc.HttpMethodEnum.GET.value,
            expected_url,
            headers=None,
            verify=False,
            timeout=5,
            json=None,
        )
        mock_unwrap.assert_called_once_with(mock_response)
        self.assertEqual(result, ([], {}))

    @patch("hue_entertainment_pykit.lowl.clients.http_client.ResponseUtil.unwrap")
    @patch("hue_entertainment_pykit.lowl.clients.http_client.requests.request")
    def test_send_request_with_header_and_body_no_query_parts(self, mock_request, mock_unwrap):
        mock_response = MagicMock(name="Response")
        mock_request.return_value = mock_response
        mock_unwrap.return_value = ({"ok": True}, {"h": "v"})

        header = MagicMock()
        header.get_data.return_value = {"Authorization": "Bearer token"}

        body = MagicMock()
        body.get_query_id.return_value = None
        body.get_query_rid.return_value = None
        body.get_data.return_value = {"foo": "bar"}

        result = hc.HttpClient._send_request(
            hc.HttpMethodEnum.POST, self.endpoint, self.ip, header, body
        )

        expected_url = f"https://{self.ip}/{self.endpoint.value}"
        mock_request.assert_called_once_with(
            hc.HttpMethodEnum.POST.value,
            expected_url,
            headers={"Authorization": "Bearer token"},
            verify=False,
            timeout=5,
            json={"foo": "bar"},
        )
        body.remove_key.assert_not_called()
        self.assertEqual(result, ({"ok": True}, {"h": "v"}))

    @patch("hue_entertainment_pykit.lowl.clients.http_client.ResponseUtil.unwrap")
    @patch("hue_entertainment_pykit.lowl.clients.http_client.requests.request")
    def test_send_request_with_query_id_and_query_rid(self, mock_request, mock_unwrap):
        mock_response = MagicMock(name="Response")
        mock_request.return_value = mock_response
        mock_unwrap.return_value = ([{"result": "ok"}], {"h": "x"})

        query_id = UUID("11111111-2222-3333-4444-555555555555")
        query_rid = UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")

        header = MagicMock()
        header.get_data.return_value = {"X-Test": "1"}

        body = MagicMock()
        body.get_query_id.return_value = query_id
        body.get_query_rid.return_value = query_rid
        body.get_data.return_value = {"payload": 123}

        result = hc.HttpClient._send_request(
            hc.HttpMethodEnum.PUT, self.endpoint, self.ip, header, body
        )

        expected_url = f"https://{self.ip}/{self.endpoint.value}/{query_id}/{query_rid}"
        mock_request.assert_called_once_with(
            hc.HttpMethodEnum.PUT.value,
            expected_url,
            headers={"X-Test": "1"},
            verify=False,
            timeout=5,
            json={"payload": 123},
        )
        body.remove_key.assert_any_call("query_id")
        body.remove_key.assert_any_call("query_rid")
        self.assertEqual(result, ([{"result": "ok"}], {"h": "x"}))


if __name__ == "__main__":
    unittest.main()
