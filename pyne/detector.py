

from collections.abc import Sequence

import matplotlib.pyplot as plt
import numpy


class Detector:
    def __init__(self, name='', channels=4096):
        self.name = name
        self.channels = channels
        self.bins = numpy.arange(self.channels + 1)
        self.adc = []
        self.counts = None
        self.total_counts = None
        self.energies = None

    def add_event(self, value):
        self.adc.append(value)

    def convert_channels(self):
        self.counts, _ = numpy.histogram(self.adc, bins=self.bins)
        # ensure first and last bins don't contain under/overflow
        self.counts[:3] = 0
        self.counts[-4:] = 0
        self.total_counts = self.counts.sum()

    def set_calibration(self, values):
        self.energies = values

    def display(self, figsize=(8, 6), log=False, calibrated=True):
        fig = plt.figure(figsize=figsize)
        axis = fig.add_axes([0.1, 0.1, 0.8, 0.8])
        if self.counts is None:
            self.convert_channels()
        if calibrated and self.energies is not None:
            plot_x = self.energies
        else:
            plot_x = self.bins[:-1]
        if log:
            axis.semilogy(plot_x, self.counts)
        else:
            axis.plot(plot_x, self.counts)
        axis.set_title(self.name)
        return fig, axis


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
        self.detectors[channel].add_event(value)

    def convert_detectors(self):
        for detector in self.detectors:
            detector.convert_channels()
