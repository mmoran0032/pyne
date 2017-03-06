

from collections.abc import Sequence


class Detector(Sequence):
    def __init__(self, channels):
        self.chanels = channels
        self.adc = [self._add_channel() for _ in range(self.channels)]

    def __getitem__(self, index):
        return self.adc[index]

    def __len__(self):
        return self.channels

    def _add_channel(self):
        return list()
