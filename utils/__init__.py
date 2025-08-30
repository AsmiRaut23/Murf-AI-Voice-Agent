# # utils/__init__.py

# from .logger import logger

# __all__ = ["logger"]


# from .logger import logger  # makes `from utils import logger` possible
from .logger import logger  # import the logger instance
logger.info("✅ Logger initialized successfully")
logger.debug("Debug message")
