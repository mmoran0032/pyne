

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit


class Analyze:
    def __init__(self, data, name):
        self.data = data
        self.name = name

    def determine_energy_window(self, sigma_window=(7, 7), **pargs):
        good_detectors = self.data.adc[16:]
        central_det = self._find_best_detector(good_detectors)
        fit_pars = self._fit_best_detector(central_det)
        energy_range = self._get_energy_range(fit_pars, sigma_window)
        fig, _ = self.single_plot(central_det, fit_pars, energy_range, **pargs)
        fig.savefig('{}_energy_window.png'.format(self.name))
        return energy_range

    def _find_best_detector(self, detectors):
        counts_by_strip = [det.counts.max() for det in detectors]
        max_strip_index = counts_by_strip.index(max(counts_by_strip))
        return detectors[max_strip_index]

    def _fit_best_detector(self, detector):
        fit_guess = [detector.counts.max(), 2750, detector.counts.max() / 12]
        par, _ = curve_fit(gaussian, detector.energies, detector.counts,
                           p0=fit_guess)
        return par

    def _get_energy_range(self, fit_pars, sigma_window):
        low_energy = fit_pars[1] - sigma_window[0] * fit_pars[2]
        high_energy = fit_pars[1] + sigma_window[0] * fit_pars[2]
        return np.array([low_energy, high_energy])

    def get_peak_counts(self, energy_range, **pargs):
        good_detectors = self.data.adc[16:]
        counts = [self._sum_peak(d, energy_range) for d in good_detectors]
        counts = np.array(counts)
        for i, value in enumerate(counts):
            print('adc {:02d}: {:>5d} +/- {:>3d}'.format(
                i + 16, value, int(np.sqrt(value))))
        fig, _ = self.display_detector(counts, **pargs)
        fig.savefig('{}_full_detector.png'.format(self.name))
        return counts

    def _sum_peak(self, detector, energy_range):
        bin_indices = np.searchsorted(detector.energies, energy_range)
        peak_range = detector.counts[bin_indices[0]:bin_indices[1]]
        return peak_range.sum()

    def single_plot(self, detector, fit_pars=None, energy_range=None, *,
                    figsize=(10, 7.5), xlim=(0, 4000), ylim=(1, 1000)):
        fig = plt.figure(figsize=figsize)
        ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
        # nonposy='clip' wasn't working for this single case, so do it yourself
        counts = np.where(detector.counts > 0, detector.counts, 1e-10)
        ax.semilogy(detector.energies, counts,
                    nonposy='clip', linestyle='steps-mid')
        ax = self._adjust_ax(ax, fit_pars, energy_range, xlim, ylim)
        ax.set_title(detector.name)
        return fig, ax

    def display_array(self, fit_pars=None, energy_range=None, *,
                      figsize=(10, 7.5), xlim=(0, 4000), ylim=(1, 1000)):
        fig, axes = plt.subplots(nrows=4, ncols=4, figsize=figsize)
        axis = axes.ravel()
        for ax, adc in zip(axis, self.data.adc[16:]):
            ax.semilogy(adc.energies, adc.counts,
                        nonposy='clip', linestyle='steps-mid')
            ax = self._adjust_ax(ax, fit_pars, energy_range, xlim, ylim)
            ax.set_title(adc.name)
        fig.tight_layout()
        return fig, axes

    def display_detector(self, counts, *, figsize=(10, 7.5), ylim=(0, 100000)):
        counts = [0, *counts, 0]
        fig = plt.figure(figsize=figsize)
        ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
        ax.plot(np.arange(18), counts, linestyle='steps-mid')
        ax.set_xticks(np.arange(16) + 1)
        ax.set_xlim((0.5, 16.5))
        ax.set_ylim(ylim)
        return fig, ax

    def _adjust_ax(self, ax, fit_pars, energy_range, xlim, ylim):
        if fit_pars is not None:
            x = np.linspace(2000, 4000, 1000)
            ax.semilogy(x, gaussian(x, *fit_pars), 'k-', lw=1)
        if energy_range is not None:
            ax.vlines(energy_range, 0.1, 1000, 'k', linestyles='dashed', lw=1)
        ax.set_ylim(ylim)
        ax.set_xlim(xlim)
        return ax


def gaussian(x, A, mu, sig):
    return A * np.exp(-(x - mu)**2 / (2 * sig**2))
