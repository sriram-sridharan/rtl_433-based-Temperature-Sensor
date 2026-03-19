import sys
import os
from unittest.mock import patch, MagicMock
from urllib.error import URLError, HTTPError
from socket import timeout

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import temp_simplified


@patch('temp_simplified.urlopen')
def test_send_data_success(mock_urlopen):
    # A successful request should call urlopen exactly once with no retries
    mock_urlopen.return_value = MagicMock()
    temp_simplified.send_data(1, 72.5, 45.0)
    assert mock_urlopen.call_count == 1


@patch('temp_simplified.time.sleep')
@patch('temp_simplified.urlopen')
def test_send_data_http_error_no_retry(mock_urlopen, mock_sleep):
    # HTTP errors indicate a bad request, so retrying won't help and things should break immediately
    mock_urlopen.side_effect = HTTPError(url=None, code=404, msg='Not Found', hdrs=None, fp=None)
    temp_simplified.send_data(1, 72.5, 45.0)
    assert mock_urlopen.call_count == 1
    mock_sleep.assert_not_called()


@patch('temp_simplified.time.sleep')
@patch('temp_simplified.urlopen')
def test_send_data_timeout_retries(mock_urlopen, mock_sleep):
    # Timeouts (e.g. PRTG temporarily down) should retry up to 15 times before giving up
    mock_urlopen.side_effect = timeout()
    temp_simplified.send_data(1, 72.5, 45.0)
    assert mock_urlopen.call_count == 15
    assert mock_sleep.call_count == 15


@patch('temp_simplified.time.sleep')
@patch('temp_simplified.urlopen')
def test_send_data_succeeds_after_retry(mock_urlopen, mock_sleep):
    # If a timeout is followed by a success, it should stop retrying and return
    mock_urlopen.side_effect = [timeout(), timeout(), MagicMock()]
    temp_simplified.send_data(1, 72.5, 45.0)
    assert mock_urlopen.call_count == 3


@patch('temp_simplified.urlopen')
def test_send_data_url_contains_sensor_id(mock_urlopen):
    # The sensor ID must appear in the URL so PRTG attributes the data to the correct sensor
    mock_urlopen.return_value = MagicMock()
    temp_simplified.send_data(42, 70.0, 50.0)
    called_url = mock_urlopen.call_args[0][0]
    assert '/42?' in called_url
