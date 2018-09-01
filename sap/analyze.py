

import numpy as np
from scipy.optimize import curve_fit

from .functions import gaussian


class Analyzer:
    def __init__(self, data):
        self.data = data

    def determine_energy_window(self, sigma_window=(7, 7)):
        good_detectors = self.data.adc[16:]
        central_det, index = self._find_best_detector(good_detectors)
        fit_pars = self._fit_best_detector(central_det)
        energy_range = self._get_energy_range(fit_pars, sigma_window)
        return energy_range, fit_pars, index

    def _find_best_detector(self, detectors):
        counts_by_strip = [det.counts.max() for det in detectors]
        max_strip_index = np.argmax(counts_by_strip)
        return detectors[max_strip_index], max_strip_index

    def _fit_best_detector(self, detector):
        print(' using det {}...'.format(detector.name))
        fit_guess = [detector.counts.max(),
                     detector.energies[np.argmax(detector.counts)],
                     detector.counts.max() / 12]
        par, _ = curve_fit(gaussian, detector.energies, detector.counts,
                           p0=fit_guess, bounds=(0, np.inf))
        return par

    def _get_energy_range(self, fit_pars, sigma_window):
        return np.array([
            fit_pars[1] - sigma_window[0] * fit_pars[2],
            fit_pars[1] + sigma_window[0] * fit_pars[2]
        ])

    def get_peak_counts(self, energy_range, **pargs):
        good_detectors = self.data.adc[16:]
        counts = [self._sum_peak(d, energy_range) for d in good_detectors]
        counts = np.array(counts)
        for i, value in enumerate(counts):
            print('adc {:02d}: {:>5d} +/- {:>3d}'.format(
                i + 16, value, int(np.sqrt(value))))
        return counts

    def _sum_peak(self, detector, energy_range):
        bin_indices = np.searchsorted(detector.energies, energy_range)
        peak_range = detector.counts[slice(*bin_indices)]
        return peak_range.sum()
