from unittest.mock import patch

import pytest
from elasticsearch import NotFoundError
from snapshot_operations import SnapshotOperations, SnapshotError


@pytest.fixture
def mock_snapshot_operations():
    with patch('config.Config') as mock_config, \
         patch('snapshot_operations.Elasticsearch') as mock_es:
        mock_config.return_value.elasticsearch_host = "https://localhost:9200"
        mock_config.return_value.elasticsearch_username = "user"
        mock_config.return_value.elasticsearch_password = "pass"
        mock_config.return_value.repository_name = "repo"
        mock_config.return_value.data_stream_pattern = "pattern"
        mock_config.return_value.min_days_to_snapshot = 30
        mock_config.return_value.min_days_to_delete_snapshot = 90
        mock_config.return_value.delete_old_snapshots = True
        mock_config.return_value.max_workers = 4
        mock_client = mock_es.return_value
        mock_client.indices.get_data_stream.return_value = {'data_streams': []}
        mock_client.snapshot.get.return_value = {'snapshots': []}
        
        yield SnapshotOperations(mock_config.return_value)

def test_get_data_streams_older_than_days_success(mock_snapshot_operations):
    mock_snapshot_operations.client.indices.get_data_stream.return_value = {
        'data_streams': [
            {'name': 'stream-2023.01.01'},
            {'name': 'stream-2023.01.02'},
            {'name': 'stream-2023.01.03'}
        ]
    }
    result = mock_snapshot_operations.get_data_streams_older_than_days()
    assert len(result) > 0
    assert all('stream-' in name for name in result)

def test_get_data_streams_older_than_days_error(mock_snapshot_operations):
    mock_snapshot_operations.client.indices.get_data_stream.side_effect = Exception("Test error")
    with pytest.raises(SnapshotError) as exc_info:
        mock_snapshot_operations.get_data_streams_older_than_days()
    assert "Error getting data streams" in str(exc_info.value)

def test_get_data_streams_with_invalid_date(mock_snapshot_operations):
    mock_snapshot_operations.client.indices.get_data_stream.return_value = {
        'data_streams': [
            {'name': 'stream-invalid-date'},
            {'name': 'stream-2023.01.01'}
        ]
    }
    result = mock_snapshot_operations.get_data_streams_older_than_days()
    assert len(result) > 0
    assert all('stream-' in name for name in result)

def test_snapshot_exists_found(mock_snapshot_operations):
    mock_snapshot_operations.client.snapshot.get.return_value = {'snapshots': []}
    should_skip, reason = mock_snapshot_operations.snapshot_exists("test-stream")
    assert should_skip is True
    assert reason == "snapshot already exists"

def test_snapshot_exists_not_found(mock_snapshot_operations):
    mock_snapshot_operations.client.snapshot.get.side_effect = NotFoundError('msg', {}, {})
    should_skip, reason = mock_snapshot_operations.snapshot_exists("test-stream")
    assert should_skip is False
    assert reason == ""

def test_snapshot_exists_error(mock_snapshot_operations):
    mock_snapshot_operations.client.snapshot.get.side_effect = Exception("Test error")
    should_skip, reason = mock_snapshot_operations.snapshot_exists("test-stream")
    assert should_skip is True
    assert reason == "could not verify snapshot existence"

def test_create_snapshot_success(mock_snapshot_operations):
    result = mock_snapshot_operations.create_snapshot("test-stream")
    assert result is True
    mock_snapshot_operations.client.snapshot.create.assert_called_once()

def test_create_snapshot_dry_run(mock_snapshot_operations):
    result = mock_snapshot_operations.create_snapshot("test-stream", dry_run=True)
    assert result is True

def test_create_snapshot_error(mock_snapshot_operations):
    mock_snapshot_operations.client.snapshot.create.side_effect = Exception("Test error")
    result = mock_snapshot_operations.create_snapshot("test-stream")
    assert result is False

def test_delete_data_stream_success(mock_snapshot_operations):
    result = mock_snapshot_operations.delete_data_stream("test-stream")
    assert result is True
    mock_snapshot_operations.client.indices.delete_data_stream.assert_called_once()

def test_delete_data_stream_dry_run(mock_snapshot_operations):
    result = mock_snapshot_operations.delete_data_stream("test-stream", dry_run=True)
    assert result is True

def test_delete_data_stream_error(mock_snapshot_operations):
    mock_snapshot_operations.client.indices.delete_data_stream.side_effect = Exception("Test error")
    result = mock_snapshot_operations.delete_data_stream("test-stream")
    assert result is False

def test_delete_old_snapshots_success(mock_snapshot_operations):
    mock_snapshot_operations.client.snapshot.get.return_value = {
        'snapshots': [
            {'snapshot': 'snapshot-2023.01.01'},
            {'snapshot': 'snapshot-2023.01.02'}
        ]
    }
    result = mock_snapshot_operations.delete_old_snapshots()
    assert result is True
    assert mock_snapshot_operations.client.snapshot.delete.call_count > 0

def test_delete_old_snapshots_dry_run(mock_snapshot_operations):
    mock_snapshot_operations.client.snapshot.get.return_value = {
        'snapshots': [
            {'snapshot': 'snapshot-2023.01.01'},
            {'snapshot': 'snapshot-2023.01.02'}
        ]
    }
    result = mock_snapshot_operations.delete_old_snapshots(dry_run=True)
    assert result is True
    mock_snapshot_operations.client.snapshot.delete.assert_not_called()

def test_delete_old_snapshots_error(mock_snapshot_operations):
    mock_snapshot_operations.client.snapshot.get.side_effect = Exception("Test error")
    result = mock_snapshot_operations.delete_old_snapshots()
    assert result is False

def test_delete_old_snapshots_with_invalid_date(mock_snapshot_operations):
    mock_snapshot_operations.client.snapshot.get.return_value = {
        'snapshots': [
            {'snapshot': 'snapshot-invalid-date'},
            {'snapshot': 'snapshot-2023.01.01'}
        ]
    }
    result = mock_snapshot_operations.delete_old_snapshots()
    assert result is True
    assert mock_snapshot_operations.client.snapshot.delete.call_count > 0

def test_delete_old_snapshots_no_snapshots(mock_snapshot_operations):
    mock_snapshot_operations.client.snapshot.get.return_value = {
        'snapshots': []
    }
    result = mock_snapshot_operations.delete_old_snapshots()
    assert result is True
    mock_snapshot_operations.client.snapshot.delete.assert_not_called() 