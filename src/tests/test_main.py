import sys
from unittest.mock import patch, MagicMock

import pytest
from main import parse_args, process_data_stream, process_data_streams, main


@pytest.fixture
def mock_snapshot_operations():
    with patch('main.snapshot_ops') as mock:
        mock.config.max_workers = 4
        mock.config.delete_data_stream_after_snapshot = True
        mock.snapshot_exists.return_value = (False, None)
        mock.create_snapshot.return_value = True
        yield mock

def test_parse_args():
    with patch('sys.argv', ['script.py']):
        args = parse_args()
        assert not args.dry_run

def test_parse_args_with_dry_run():
    with patch('sys.argv', ['script.py', '--dry-run']):
        args = parse_args()
        assert args.dry_run

def test_process_data_stream_skip(mock_snapshot_operations):
    mock_snapshot_operations.snapshot_exists.return_value = (True, "Snapshot already exists")
    process_data_stream("test-stream")
    mock_snapshot_operations.create_snapshot.assert_not_called()
    mock_snapshot_operations.delete_data_stream.assert_not_called()

def test_process_data_stream_success(mock_snapshot_operations):
    mock_snapshot_operations.snapshot_exists.return_value = (False, None)
    mock_snapshot_operations.create_snapshot.return_value = True
    mock_snapshot_operations.config.delete_data_stream_after_snapshot = True
    process_data_stream("test-stream")
    mock_snapshot_operations.create_snapshot.assert_called_once_with("test-stream", False)
    mock_snapshot_operations.delete_data_stream.assert_called_once_with("test-stream", False)

def test_process_data_stream_success_preserve(mock_snapshot_operations):
    mock_snapshot_operations.snapshot_exists.return_value = (False, None)
    mock_snapshot_operations.create_snapshot.return_value = True
    mock_snapshot_operations.config.delete_data_stream_after_snapshot = False
    process_data_stream("test-stream")
    mock_snapshot_operations.create_snapshot.assert_called_once_with("test-stream", False)
    mock_snapshot_operations.delete_data_stream.assert_not_called()

def test_process_data_stream_failure(mock_snapshot_operations):
    mock_snapshot_operations.snapshot_exists.return_value = (False, None)
    mock_snapshot_operations.create_snapshot.return_value = False
    process_data_stream("test-stream")
    mock_snapshot_operations.create_snapshot.assert_called_once_with("test-stream", False)
    mock_snapshot_operations.delete_data_stream.assert_not_called()

def test_process_data_streams_empty(mock_snapshot_operations):
    process_data_streams([])
    mock_snapshot_operations.create_snapshot.assert_not_called()
    mock_snapshot_operations.delete_data_stream.assert_not_called()

def test_process_data_streams_success(mock_snapshot_operations):
    data_streams = ["stream1", "stream2"]
    process_data_streams(data_streams)
    assert mock_snapshot_operations.create_snapshot.call_count == 2
    assert mock_snapshot_operations.delete_data_stream.call_count == 2

def test_process_data_streams_with_error(mock_snapshot_operations):
    mock_snapshot_operations.create_snapshot.side_effect = Exception("Test error")
    data_streams = ["stream1", "stream2"]
    process_data_streams(data_streams)
    assert mock_snapshot_operations.create_snapshot.call_count == 2
    assert mock_snapshot_operations.delete_data_stream.call_count == 0

def test_main_success(mock_snapshot_operations):
    with patch('sys.argv', ['script.py']):
        main()
        mock_snapshot_operations.get_data_streams_older_than_days.assert_called_once()
        mock_snapshot_operations.delete_old_snapshots.assert_called_once_with(dry_run=False)

def test_main_dry_run(mock_snapshot_operations):
    with patch('sys.argv', ['script.py', '--dry-run']):
        main()
        mock_snapshot_operations.get_data_streams_older_than_days.assert_called_once()
        mock_snapshot_operations.delete_old_snapshots.assert_called_once_with(dry_run=True)

def test_main_with_error(mock_snapshot_operations):
    mock_snapshot_operations.get_data_streams_older_than_days.side_effect = Exception("Test error")
    with patch('sys.argv', ['script.py']):
        with pytest.raises(Exception) as exc_info:
            main()
        assert str(exc_info.value) == "Test error"
