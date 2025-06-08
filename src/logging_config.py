import logging
import os
import sys

from ecs_logging import StdlibFormatter
from loguru import logger

if os.getenv("SLOGGER_ENABLED", "").lower() == "true":
    logger.remove()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StdlibFormatter())
    logger.add(handler)
