import datetime
import logging
from logging.handlers import TimedRotatingFileHandler

from pathlib import Path
from platformdirs import user_data_dir

from borealis.orchestrator import Orchestrator
from borealis.data_collector import DataCollector

# default cross-platform directory for Borealis log and config files
# On windows, it should be something like C:\\Users\\username\\AppData\\Local\\C4XS\\Borealis
# On linux, it should be something like /home/username/.local/share/Borealis
app_name = "Borealis"
app_author = "C4XS"
app_dir = Path(user_data_dir(app_name, app_author))
app_dir.mkdir(parents=True, exist_ok=True)

#####  LOGGING settings  #####
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Stream handler to log to the console
stream_hdlr = logging.StreamHandler()
stream_hdlr.setLevel(logging.INFO)
# stream_formatter = logging.Formatter('%(asctime)s - %(message)s')
# stream_hdlr.setFormatter(stream_formatter)
logger.addHandler(stream_hdlr)

# Handler to file
log_dir = app_dir / 'logs'
log_dir.mkdir(parents=False, exist_ok=True)
file_hdlr = TimedRotatingFileHandler(log_dir / "borealis.log", when="midnight")
file_hdlr.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(module)s - line %(lineno)d - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
file_hdlr.setFormatter(file_formatter)
logger.addHandler(file_hdlr)

logger.debug("\n\n %s - New Borealis session started \n",
             datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# SESSION OBJECTS
session_orchestrator = Orchestrator()
data_collector = DataCollector(session_orchestrator)

# Exposing main functions at package level as users shouldn't care about DataCollector
def new_file(exp_id: str = ''):
    data_collector.create_h5file(experiment_id=exp_id)

def new_sample(sample: str):
    data_collector.current_sample = sample