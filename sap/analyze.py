

import numpy as np
from scipy.optimize import curve_fit

import pyne

from . import display


class Analyze:
    def __init__(self, *args):
        self.loaded_runs = []
        self.loaded_numbers = []
        self.display = display.Display()
        self.experiment = pyne.Experiment(*args)
        self.experiment.find_all()

    def __call__(self, run_number):
        data = self.load_data(run_number)

        fig, _ = self.display.display_array(data)
        fig.savefig('{}_array.png'.format(run_number))

        # fit central detector
        det = data.adc[23]
        p0 = [det.counts.max(), 2750, 50]
        par, _ = curve_fit(gaussian, det.energies, det.counts, p0=p0)
        print(par)

    def load_data(self, run_number):
        if run_number in self.loaded_numbers:
            index = self.loaded_numbers.index(run_number)
            data = self.loaded_runs[index]
        else:
            self.loaded_numbers.append(run_number)
            data = self._load_data(run_number)
            self.loaded_runs.append(data)
        return data

    def _load_data(self, run_number):
        data = self.experiment[run_number]
        data.load_data()
        return data


def gaussian(x, A, mu, sig):
    return A * np.exp(-(x - mu)**2 / (2 * sig**2))
