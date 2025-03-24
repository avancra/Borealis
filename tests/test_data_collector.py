from pathlib import Path

from borealis.data_collector import DataCollector
from borealis.orchestrator import Orchestrator

class TestDataCollector:

    @classmethod
    def setup_class(cls):
        orchestrator = Orchestrator()
        cls.dc = DataCollector(orchestrator)
        cls.h5_filename = Path(f'borealis_datafile_test.h5')

    def test_data_collector(self):
        self.dc.create_h5file(self.h5_filename)

        assert self.h5_filename.exists()

    @classmethod
    def teardown_class(cls):
        cls.dc.h5file.close()
        cls.h5_filename.unlink()

