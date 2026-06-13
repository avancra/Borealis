from pathlib import Path

import borealis
from borealis.data_collector import DataCollector

class TestDataCollector:

    @classmethod
    def setup_class(cls):
        cls.dc = DataCollector()
        cls.dc.filename_base = Path(f'datafile_test_dc')

    def test_data_collector(self):
        self.dc.create_h5file(add_date=False)

        assert Path('./data/datafile_test_dc.h5').exists()

    @classmethod
    def teardown_class(cls):
        cls.dc.h5file.close()
        borealis.session_orchestrator.data_managers.remove(cls.dc)
        # Path('./data/borealis_datafile_test.h5').unlink()

