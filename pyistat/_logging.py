import os
import logging

log_level = os.getenv("PYISTAT_LOG_LEVEL", "WARNING").upper()
logging.basicConfig(
    level=log_level,
    format='%(levelname)s - %(message)s'
)

logger = logging.getLogger("pyistat")