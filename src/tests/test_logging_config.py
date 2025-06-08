import os
from unittest.mock import patch

import pytest
from loguru import logger


def test_logger_configuration():
    assert len(logger._core.handlers) > 0
    try:
        logger.info("Test message for Loguru logger.")
    except Exception as e:
        pytest.fail(f"Logger failed to log message: {e}")

def test_logger_loguru():
    try:
        logger.info("Test message for Loguru logger.")
    except Exception as e:
        pytest.fail(f"Logger failed to log message: {e}")

def test_logger_with_slogger_enabled():
    with patch.dict(os.environ, {'SLOGGER_ENABLED': 'true'}):
        import importlib
        import logging_config
        importlib.reload(logging_config)
        
        assert len(logger._core.handlers) > 0
        try:
            logger.info("Test message with SLOGGER enabled")
        except Exception as e:
            pytest.fail(f"Logger failed to log message: {e}")

def test_logger_with_slogger_disabled():
    with patch.dict(os.environ, {'SLOGGER_ENABLED': 'false'}):
        import importlib
        import logging_config
        importlib.reload(logging_config)

        assert len(logger._core.handlers) > 0
        try:
            logger.info("Test message with SLOGGER disabled")
        except Exception as e:
            pytest.fail(f"Logger failed to log message: {e}")
