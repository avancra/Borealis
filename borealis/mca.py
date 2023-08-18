import datetime
import logging

import numpy as np


LOGGER = logging.getLogger(__name__)

class MCAMetadata:

    def __init__(self, runtime: float, livetime: float, det_info: dict, date: datetime = None):
        self.runtime = runtime
        self.livetime = livetime
        self.acq_date = datetime.datetime.now() if date is None else date
        self.det_sn = det_info["serial_number"]
        self.det_alias = det_info["alias"]
        self.det_type = det_info["type"]
        LOGGER.debug('New MCA created')

    def as_dict(self):
        det_info = {'serial_number': self.det_sn,
                    'alias': self.det_alias,
                    'type': self.det_type}

        return {'date': self.acq_date,
                'runtime': self.runtime,
                'livetime': self.livetime,
                'detector': det_info}

    @classmethod
    def from_dict(cls, md_dict):
        return cls(runtime=md_dict['runtime'],
                   livetime=md_dict['livetime'],
                   det_info=md_dict['detector'],
                   date=md_dict['date'])

class MCA:

    def __init__(self, counts_array: np.ndarray, metadata: MCAMetadata):
        self.counts = np.asarray(counts_array)
        self.metadata = metadata

    def as_dict(self):
        return_dict = {"mca_counts": self.counts.tolist(),
                       "metadata": self.metadata.as_dict()}
        return return_dict

    @classmethod
    def from_dict(cls, mca_dict):
        return cls(np.array(mca_dict["mca_counts"]),
                   MCAMetadata.from_dict(mca_dict["metadata"]))
