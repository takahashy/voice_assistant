import pytest
from unittest.mock import MagicMock, patch
from services.deepgram import DeepgramService

@patch("services.deepgram.DeepgramClient")
def test_initialize_connection_success(mock_deepgram_client):
    mock_client_instance = MagicMock()
    mock_connection = MagicMock()
    mock_client_instance.listen.live.v.return_value = mock_connection
    mock_deepgram_client.return_value = mock_client_instance
    mock_connection.start.return_value = True

    service = DeepgramService()
    service.set_callback(lambda x: x)
    service.initialize_connection()

    mock_connection.start.assert_called_once()
    assert service.connection is not None

@patch("services.deepgram.DeepgramClient")
def test_initialize_connection_failure(mock_deepgram_client):
    mock_client_instance = MagicMock()
    mock_connection = MagicMock()
    mock_connection.start.return_value = False
    mock_client_instance.listen.live.v.return_value = mock_connection
    mock_deepgram_client.return_value = mock_client_instance

    service = DeepgramService()
    service.set_callback(lambda x: x)
    with pytest.raises(SystemExit):  # Because you call exit() in failure
        service.initialize_connection()

@patch("services.deepgram.DeepgramClient")
def test_send_without_connection(mock_deepgram_client):
    service = DeepgramService()
    service.connection = None

    with pytest.raises(Exception):
        service.send(b"test audio")


