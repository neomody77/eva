import logging
from rich.logging import RichHandler

# Create the logger
logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    handlers=[RichHandler(show_time=False, show_level=True)]  # Do not pass level_styles here
)

logger = logging.getLogger("rich")

