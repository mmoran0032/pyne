

import numbers

import matplotlib.pyplot as plt
import numpy as np

from .functions import gaussian


class Display:
    def __init__(self, data):
        self.data = data

    def single_plot(self, detector, fit_pars=None, energy_range=None, *,
                    figsize=(10, 7.5), xlim=(0, 4000), ylim=(1, 1000)):
        if isinstance(detector, numbers.Integral):
            detector = self.data[detector]
        fig = plt.figure(figsize=figsize)
        ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
        tiny = np.finfo(np.float64).tiny
        counts = np.where(detector.counts > 0, detector.counts, tiny)
        ax.plot(detector.energies, counts, linestyle='steps')
        ax = self._adjust_ax(ax, fit_pars, energy_range, xlim, ylim)
        ax.set_title(detector.name)
        return fig, ax

    def display_array(self, fit_pars=None, energy_range=None, *,
                      figsize=(10, 7.5), xlim=(0, 4000), ylim=(1, 1000)):
        fig, axes = plt.subplots(nrows=4, ncols=4, figsize=figsize)
        axis = axes.ravel()
        for ax, adc in zip(axis, self.data.adc[16:]):
            ax.plot(adc.energies, adc.counts, linestyle='steps')
            ax = self._adjust_ax(ax, fit_pars, energy_range, xlim, ylim)
            ax.set_title(adc.name)
        fig.tight_layout()
        return fig, axes

    def display_detector(self, counts, *, figsize=(10, 7.5), ylim=(0, 1e5)):
        counts = [0, *counts, 0]
        fig = plt.figure(figsize=figsize)
        ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])
        ax.plot(np.arange(18), counts, linestyle='steps-mid', lw=2)
        ax.set_xticks(np.arange(16) + 1)
        ax.set_xlim((0.5, 16.5))
        ax.set_ylim(ylim)
        return fig, ax

    def _adjust_ax(self, ax, fit_pars, energy_range, xlim, ylim):
        if fit_pars is not None:
            x = np.linspace(*xlim, 5000)
            ax.semilogy(x, gaussian(x, *fit_pars), 'k-', lw=1)
        if energy_range is not None:
            ax.vlines(energy_range, *ylim, 'k', linestyles='dashed', lw=1)
        ax.set_yscale('log', nonposy='clip')
        ax.set_ylim(ylim)
        ax.set_xlim(xlim)
        return ax

