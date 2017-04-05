

import pytest


@pytest.fixture
def detector():
    from . import detector
    return detector.Detector(name='test', channels=5)


def test_add_event(detector):
    detector.add_event(None, 1)
    assert 1 in detector.adc


def test_set_calibration(detector):
    energies = [3.5, 4.75, 6.0, 7.25]
    detector.set_calibration(energies)
    assert detector.energies == energies


def test_binning(detector):
    data = [1, 1, 1, 1, 2, 2, 2, 3, 3, 4]
    for value in data:
        detector.add_event(None, value)
    detector.convert_detector(mask=False)
    assert detector.counts[0] == 0
    assert detector.counts[1] == 4
    assert detector.counts[2] == 3
    assert detector.counts[3] == 2
    assert detector.counts[4] == 1
