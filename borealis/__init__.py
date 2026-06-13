import datetime
import logging
from logging.handlers import TimedRotatingFileHandler

from pathlib import Path
from typing import Union, Iterable

from platformdirs import user_data_dir

__all__ = [
    "pseudo_motor",
    "orchestrator",
    "controller",
    "detector",
    "motor",
    "mca",
    "exceptions",
    "component",
    "spellman",
    "data_collector",
]

# default cross-platform directory for Borealis log and config files
# On windows, it should be something like C:\\Users\\username\\AppData\\Local\\C4XS\\Borealis
# On linux, it should be something like /home/username/.local/share/Borealis
app_name = "Borealis"
app_author = "C4XS"
app_dir = Path(user_data_dir(app_name, app_author))
app_dir.mkdir(parents=True, exist_ok=True)

###################
#  LOGGING SETUP  #
###################

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Stream handler to log to the console
stream_hdlr = logging.StreamHandler()
stream_hdlr.setLevel(logging.INFO)
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

#####################
#  SESSION OBJECTS  #
#####################

from borealis.orchestrator import Orchestrator
session_orchestrator = Orchestrator()

from borealis.data_collector import DataCollector
session_data_collector = DataCollector()

####################
#   PUBLIC API     #
####################

# Exposing main functions at package level as users shouldn't care about internals
def new_file(exp_id: str = ''):
    """New file."""
    session_data_collector.create_h5file(experiment_id=exp_id)


def new_sample(sample: str):
    """New sample.

    Parameters
    ----------
    sample : str
    """
    session_data_collector.current_sample = sample


def scan(scan_motor: Union['Motor', 'PseudoMotor'], data_point: Iterable[float], acq_time: float):
    """Master scan function.

    Parameters
    ----------
    scan_motor : Union[Motor, PseudoMotor]
        Instance of Motor or Pseudo-motor to scan
    data_point : Iterable[float]
    acq_time : float

    """
    session_orchestrator.scan(scan_motor, data_point, acq_time)