from pathlib import Path

from borealis.data_collector import DataCollector
from borealis.orchestrator import Orchestrator

class TestDataCollector:

    @classmethod
    def setup_class(cls):
        orchestrator = Orchestrator()
        cls.dc = DataCollector(orchestrator)
        cls.dc.filename_base = Path(f'datafile_test_dc')

    def test_data_collector(self):
        self.dc.create_h5file(add_date=False)

        assert Path('./data/datafile_test_dc.h5').exists()

    @classmethod
    def teardown_class(cls):
        cls.dc.h5file.close()
        # Path('./data/borealis_datafile_test.h5').unlink()

