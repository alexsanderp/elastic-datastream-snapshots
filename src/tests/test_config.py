from unittest.mock import patch

import pytest
from config import Config


@pytest.fixture
def mock_config():
    with patch('config.Config') as mock_config:
        mock_config.return_value.elasticsearch_host = "https://localhost:9200"
        mock_config.return_value.elasticsearch_username = "user"
        mock_config.return_value.elasticsearch_password = "pass"
        mock_config.return_value.repository_name = "repo"
        mock_config.return_value.data_stream_pattern = "pattern"
        mock_config.return_value.min_days_to_snapshot = 30
        mock_config.return_value.min_days_to_delete_snapshot = 90
        mock_config.return_value.delete_old_snapshots = True
        mock_config.return_value.max_workers = 4
        yield mock_config.return_value

def test_config_default_values(mock_config):
    assert mock_config.elasticsearch_host == "https://localhost:9200"
    assert mock_config.elasticsearch_username == "user"
    assert mock_config.elasticsearch_password == "pass"
    assert mock_config.repository_name == "repo"
    assert mock_config.data_stream_pattern == "pattern"
    assert mock_config.min_days_to_snapshot == 30
    assert mock_config.min_days_to_delete_snapshot == 90
    assert mock_config.delete_old_snapshots is True
    assert mock_config.max_workers == 4

def clear_env(monkeypatch):
    keys = [
        'ELASTIC_TARGET', 'ELASTIC_USER', 'ELASTIC_PASS',
        'ELASTIC_REPOSITORY_NAME', 'ELASTIC_DATA_STREAM_PATTERN',
        'ELASTIC_MIN_DAYS_TO_SNAPSHOT', 'ELASTIC_MIN_DAYS_TO_DELETE_SNAPSHOT',
        'ELASTIC_DELETE_OLD_SNAPSHOTS', 'MAX_WORKERS'
    ]
    for key in keys:
        monkeypatch.delenv(key, raising=False)

def test_config_init_with_valid_env(monkeypatch):
    clear_env(monkeypatch)
    monkeypatch.setenv('ELASTIC_TARGET', 'http://localhost:9200')
    monkeypatch.setenv('ELASTIC_USER', 'user')
    monkeypatch.setenv('ELASTIC_PASS', 'pass')
    monkeypatch.setenv('ELASTIC_REPOSITORY_NAME', 'repo')
    monkeypatch.setenv('ELASTIC_DATA_STREAM_PATTERN', 'pattern')
    monkeypatch.setenv('ELASTIC_MIN_DAYS_TO_SNAPSHOT', '7')
    monkeypatch.setenv('ELASTIC_MIN_DAYS_TO_DELETE_SNAPSHOT', '30')
    monkeypatch.setenv('ELASTIC_DELETE_OLD_SNAPSHOTS', 'true')
    monkeypatch.setenv('MAX_WORKERS', '8')
    config = Config()
    assert config.elasticsearch_host == 'http://localhost:9200'
    assert config.elasticsearch_username == 'user'
    assert config.elasticsearch_password == 'pass'
    assert config.repository_name == 'repo'
    assert config.data_stream_pattern == 'pattern'
    assert config.min_days_to_snapshot == 7
    assert config.min_days_to_delete_snapshot == 30
    assert config.delete_old_snapshots is True
    assert config.max_workers == 8

def test_config_init_with_invalid_env(monkeypatch):
    clear_env(monkeypatch)
    with pytest.raises(ValueError) as exc_info:
        Config()
    assert "Missing required environment variables" in str(exc_info.value)

def test_config_init_with_invalid_min_days_to_snapshot(monkeypatch):
    clear_env(monkeypatch)
    monkeypatch.setenv('ELASTIC_TARGET', 'http://localhost:9200')
    monkeypatch.setenv('ELASTIC_USER', 'user')
    monkeypatch.setenv('ELASTIC_PASS', 'pass')
    monkeypatch.setenv('ELASTIC_REPOSITORY_NAME', 'repo')
    monkeypatch.setenv('ELASTIC_DATA_STREAM_PATTERN', 'pattern')
    monkeypatch.setenv('ELASTIC_MIN_DAYS_TO_SNAPSHOT', 'invalid')
    monkeypatch.setenv('ELASTIC_MIN_DAYS_TO_DELETE_SNAPSHOT', '30')
    monkeypatch.setenv('ELASTIC_DELETE_OLD_SNAPSHOTS', 'true')
    with pytest.raises(ValueError) as exc_info:
        Config()
    assert "ELASTIC_MIN_DAYS_TO_SNAPSHOT must be an integer" in str(exc_info.value)

def test_config_init_with_invalid_min_days_to_delete_snapshot(monkeypatch):
    clear_env(monkeypatch)
    monkeypatch.setenv('ELASTIC_TARGET', 'http://localhost:9200')
    monkeypatch.setenv('ELASTIC_USER', 'user')
    monkeypatch.setenv('ELASTIC_PASS', 'pass')
    monkeypatch.setenv('ELASTIC_REPOSITORY_NAME', 'repo')
    monkeypatch.setenv('ELASTIC_DATA_STREAM_PATTERN', 'pattern')
    monkeypatch.setenv('ELASTIC_MIN_DAYS_TO_SNAPSHOT', '7')
    monkeypatch.setenv('ELASTIC_MIN_DAYS_TO_DELETE_SNAPSHOT', 'invalid')
    monkeypatch.setenv('ELASTIC_DELETE_OLD_SNAPSHOTS', 'true')
    with pytest.raises(ValueError) as exc_info:
        Config()
    assert "ELASTIC_MIN_DAYS_TO_DELETE_SNAPSHOT must be an integer" in str(exc_info.value)

def test_config_init_with_invalid_max_workers(monkeypatch):
    clear_env(monkeypatch)
    monkeypatch.setenv('ELASTIC_TARGET', 'http://localhost:9200')
    monkeypatch.setenv('ELASTIC_USER', 'user')
    monkeypatch.setenv('ELASTIC_PASS', 'pass')
    monkeypatch.setenv('ELASTIC_REPOSITORY_NAME', 'repo')
    monkeypatch.setenv('ELASTIC_DATA_STREAM_PATTERN', 'pattern')
    monkeypatch.setenv('ELASTIC_MIN_DAYS_TO_SNAPSHOT', '7')
    monkeypatch.setenv('ELASTIC_MIN_DAYS_TO_DELETE_SNAPSHOT', '30')
    monkeypatch.setenv('ELASTIC_DELETE_OLD_SNAPSHOTS', 'true')
    monkeypatch.setenv('MAX_WORKERS', 'invalid')
    with pytest.raises(ValueError) as exc_info:
        Config()
    assert "MAX_WORKERS must be an integer" in str(exc_info.value)

def test_config_delete_old_snapshots_non_bool(monkeypatch):
    clear_env(monkeypatch)
    monkeypatch.setenv('ELASTIC_TARGET', 'http://localhost:9200')
    monkeypatch.setenv('ELASTIC_USER', 'user')
    monkeypatch.setenv('ELASTIC_PASS', 'pass')
    monkeypatch.setenv('ELASTIC_REPOSITORY_NAME', 'repo')
    monkeypatch.setenv('ELASTIC_DATA_STREAM_PATTERN', 'pattern')
    monkeypatch.setenv('ELASTIC_MIN_DAYS_TO_SNAPSHOT', '7')
    monkeypatch.setenv('ELASTIC_MIN_DAYS_TO_DELETE_SNAPSHOT', '30')
    monkeypatch.setenv('ELASTIC_DELETE_OLD_SNAPSHOTS', 'not_bool')
    config = Config()
    assert config.delete_old_snapshots is False
