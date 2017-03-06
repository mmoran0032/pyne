

from collections.abc import Sequence

import numpy


class Detector(Sequence):
    def __init__(self, channels):
        self.channels = channels
        self.bins = numpy.arange(self.channels + 1)
        self.adc = []
        self.calibration = None

    def __getitem__(self, index):
        return self.adc[index]

    def __len__(self):
        return self.channels

    def add_event(self, value):
        self.adc.append(value)

    def convert_channels(self):
        self.counts, _ = numpy.histogram(self.adc, bins=self.bins)


class DetectorArray(Sequence):
    def __init__(self, num_detectors, channels):
        self.number = num_detectors
        self.detectors = [Detector(channels) for _ in range(self.number)]

    def __getitem__(self, index):
        return self.detectors[index]

    def __len__(self):
        return self.number

    def add_event(self, channel, value):
        self.detectors[channel].add_event(value)

    def convert_detectors(self):
        for detector in self.detectors:
            detector.convert_channels()
