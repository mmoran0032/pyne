

from collections.abc import Sequence

import numpy as np


class Detector:
    def __init__(self, name='adc', channels=4096, binned=False):
        self.name = name
        self.channels = channels
        self.binned = binned
        self.bins = np.arange(self.channels + 1)
        self.adc = []
        self.counts = None
        self.energies = None

    def add_event(self, channel, value):
        self.adc.append(value)

    def convert_detector(self):
        if self.binned:
            self.counts = np.array(self.adc)
        else:
            self.counts, _ = np.histogram(self.adc, bins=self.bins)
        # ensure first and last bins don't contain under/overflow
        self.counts[:3] = 0
        self.counts[-4:] = 0

    def set_calibration(self, values):
        self.energies = values


class DetectorArray(Sequence):
    def __init__(self, num_detectors, channels):
        self.number = num_detectors
        self.detectors = [Detector('adc_{:02d}'.format(i), channels)
                          for i in range(self.number)]

    def __getitem__(self, index):
        return self.detectors[index]

    def __len__(self):
        return self.number

    def add_event(self, channel, value):
        self.detectors[channel].add_event(None, value)

    def convert_detector(self):
        for detector in self.detectors:
            detector.convert_detector()
