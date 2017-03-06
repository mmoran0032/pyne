

from collections.abc import Sequence

import numpy


class Detector(Sequence):
    def __init__(self, channels):
        self.channels = channels
        self.adc = [list() for _ in range(self.channels)]

    def __getitem__(self, index):
        return self.adc[index]

    def __len__(self):
        return self.channels

    def add_event(self, channel, value):
        self.adc[channel].append(value)

    def convert_channels(self):
        self.adc = list(map(numpy.array, self.adc))
