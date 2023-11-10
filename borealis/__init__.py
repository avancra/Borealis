import logging
from logging.handlers import TimedRotatingFileHandler
import sys

from pathlib import Path
from platformdirs import user_data_dir

# default cross-platform directory for Borealis log and config files
# On windows, it should be something like C:\\Users\\username\\AppData\\Local\\C4XS\\Borealis
app_name = "Borealis"
app_author = "C4XS"
app_dir = Path(user_data_dir(app_name, app_author))
app_dir.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Stream handler to log to the console
stream_hdlr = logging.StreamHandler()
stream_hdlr.setLevel(logging.INFO)
stream_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_hdlr.setFormatter(stream_formatter)
logger.addHandler(stream_hdlr)

# Handler to file
file_hdlr = TimedRotatingFileHandler(app_dir / "borealis.log", when="midnight")
file_hdlr.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_hdlr.setFormatter(stream_formatter)
logger.addHandler(file_hdlr)


def handle_unhandled_exception(exc_type, exc_value, exc_traceback):

    # Do not log keyboard interrupt
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    # Create a ERROR level log message with info from the except hook.
    logger.error("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))


# Assign the excepthook to the handler
sys.excepthook = handle_unhandled_exception

logger.debug("\n\n  New Borealis session started \n")
