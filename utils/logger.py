# import logging

# logging.basicConfig(
#     format="%(asctime)s [%(levelname)s] %(message)s",
#     level=logging.INFO
# )

# logger = logging.getLogger(__name__)


import logging
import sys

# Configure root logging
logging.basicConfig(
    # level=logging.DEBUG,  # default level
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)  # Print logs to console
    ]
)

# Shared logger instance for the whole project
logger = logging.getLogger("kampra-ai")
# Silence DEBUG logs from the websockets library
logging.getLogger("websockets.client").setLevel(logging.WARNING)
logging.getLogger("websockets.server").setLevel(logging.WARNING)
logging.getLogger("websockets").setLevel(logging.CRITICAL)
