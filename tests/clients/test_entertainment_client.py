import unittest
from ipaddress import IPv4Address
from unittest.mock import patch, MagicMock
from uuid import uuid4

import hue_entertainment_pykit.lowl.clients.entertainment_client as ec


class TestEntertainmentClient(unittest.TestCase):
    @patch('hue_entertainment_pykit.lowl.clients.entertainment_client.EntertainmentClient._send_request')
    @patch('hue_entertainment_pykit.lowl.clients.entertainment_client.EntertainmentHue')
    def test_fetch_all_filters_by_renderer_reference(self, MockEntertainmentHue, mock_send_request):
        body = [
            {'id': '1', 'name': 'Nope'},
            {'id': '2', 'name': 'Yes', 'renderer_reference': 'rr-123'},
        ]
        mock_send_request.return_value = (body, {})

        created_instance = MagicMock(name='EntertainmentHueInstance')
        MockEntertainmentHue.side_effect = [created_instance]

        result = ec.EntertainmentClient.fetch_all(IPv4Address('192.168.1.10'), 'user')

        self.assertEqual(result, [created_instance])
        MockEntertainmentHue.assert_called_once_with(**body[1])
        mock_send_request.assert_called_once()

    @patch('hue_entertainment_pykit.lowl.clients.entertainment_client.EntertainmentClient._send_request')
    @patch('hue_entertainment_pykit.lowl.clients.entertainment_client.EntertainmentHue')
    def test_fetch_all_empty_when_no_valid_items(self, MockEntertainmentHue, mock_send_request):
        mock_send_request.return_value = ([{'id': '1'}, {'id': '3', 'name': 'x'}], {})

        result = ec.EntertainmentClient.fetch_all(IPv4Address('192.168.1.10'), 'user')

        self.assertEqual(result, [])
        MockEntertainmentHue.assert_not_called()
        mock_send_request.assert_called_once()

    @patch('hue_entertainment_pykit.lowl.clients.entertainment_client.EntertainmentClient._send_request')
    def test_fetch_by_id_builds_request_and_returns_model(self, mock_send_request):
        uid = uuid4()
        body = [{'id': '2', 'renderer_reference': 'rr-xyz'}]
        mock_model = MagicMock(name='EntertainmentHueModel')

        with patch('hue_entertainment_pykit.lowl.clients.entertainment_client.EntertainmentHue',
                   return_value=mock_model) as MockEntertainmentHue, \
                patch('hue_entertainment_pykit.lowl.clients.entertainment_client.RequestHeader') as MockHeader, \
                patch('hue_entertainment_pykit.lowl.clients.entertainment_client.RequestBody') as MockBody:
            mock_send_request.return_value = (body, {})

            result = ec.EntertainmentClient.fetch_by_id(IPv4Address('192.168.1.10'), 'user', uid)

            self.assertIs(result, mock_model)
            MockEntertainmentHue.assert_called_once_with(**body[0])

            self.assertEqual(mock_send_request.call_count, 1)
            args, kwargs = mock_send_request.call_args
            self.assertEqual(args[0], ec.HttpMethodEnum.GET)
            self.assertEqual(args[1], ec.EndpointEnum.ENTERTAINMENT)
            self.assertEqual(args[2], IPv4Address('192.168.1.10'))

            MockHeader.assert_called_once_with('user')
            MockBody.assert_called_once_with({'query_id': uid})


if __name__ == '__main__':
    unittest.main()
