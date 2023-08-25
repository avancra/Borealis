from datetime import datetime
import numpy as np
import pytest

from borealis.mca import MCA, MCAMetadata


@pytest.fixture()
def get_det_info():
    return {'serial_number': 'S/N 1234',
            'alias': 'det',
            'type': 'ketek AXAS-M'}

@pytest.fixture()
def get_metadata_dict(get_det_info):
    md_dict = {"runtime": 42.0,
               "livetime": 42.0,
               "detector": get_det_info}

    return md_dict


def test_metadata_constructor(get_det_info):
    MCAMetadata(42., 42., get_det_info)

    with pytest.raises(TypeError):
        MCAMetadata()


def test_metadata_from_dict(get_metadata_dict):
    md_dict = get_metadata_dict
    MCAMetadata.from_dict(md_dict)

    with pytest.raises(KeyError):
        MCAMetadata.from_dict({"runtime": 42.0})

    MCAMetadata.from_dict(md_dict)


def test_metadata_date(get_det_info):
    meta = MCAMetadata(12.34, 12.34, get_det_info)
    assert isinstance(meta.acq_date, datetime)


def test_mca_constructor(get_metadata_dict):
    metadata = MCAMetadata.from_dict(get_metadata_dict)

    MCA(np.empty(10), metadata)


def test_mca_from_dict(get_metadata_dict):
    mca_dict = {"mca_counts": [1, 1, 1, 1, 1],
                "metadata": get_metadata_dict}

    print(mca_dict)
    mca = MCA.from_dict(mca_dict)
    MCA.from_dict(mca.as_dict())
    assert isinstance(mca.counts, np.ndarray)
