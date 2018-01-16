

import numbers

import matplotlib.pyplot as plt
import numpy as np

from .functions import gaussian


def display_single_channel(data, detector, fit_pars=None, energy_range=None, *,
                           figsize=(10, 7.5), xlim=(0, 4000), ylim=(1, 1000),
                           **plotting_kwargs):
    if isinstance(detector, numbers.Integral):
        detector = data[detector]
    fig, ax = plt.subplots(figsize=figsize)
    ax = detector_plot(ax, detector, **plotting_kwargs)
    ax = _adjust_ax(fit_pars, energy_range, xlim, ylim)
    return fig, ax


def display_array(data, fit_pars=None, energy_range=None, *,
                  figsize=(10, 7.5), xlim=(0, 4000), ylim=(1, 1000),
                  **plotting_kwargs):
    fig, axes = plt.subplots(nrows=4, ncols=4, figsize=figsize)
    axis = axes.ravel()
    for ax, adc in zip(axis, data.adc[16:]):
        ax = detector_plot(ax, adc, **plotting_kwargs)
        ax = _adjust_ax(fit_pars, energy_range, xlim, ylim)
    fig.tight_layout()
    return fig, axes


def display_strip_detector(counts, *, figsize=(10, 7.5), ylim=(0, 1e5)):
    counts = [0, *counts, 0]
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(np.arange(18), counts, linestyle='steps-mid')
    ax.set_xticks(np.arange(16) + 1)
    ax.set_xlim((0.5, 16.5))
    ax.set_ylim(ylim)
    return fig, ax


def detector_plot(ax, adc, **kwargs):
    counts = _fix_nonposy(adc.counts)
    ax.semilogy(adc.energies, counts, linestyle='steps', **kwargs)
    ax.set_title(adc.name)
    return ax


def _fix_nonposy(in_array):
    tiny = np.finfo(np.float64).tiny
    return np.where(in_array > 0, in_array, tiny)


def _adjust_ax(ax, fit_pars, energy_range, xlim, ylim):
    if fit_pars is not None:
        x = np.linspace(*xlim, 5000)
        ax.semilogy(x, gaussian(x, *fit_pars), 'k-', lw=1)
    if energy_range is not None:
        ax.vlines(energy_range, *ylim, 'k', linestyles='dashed', lw=1)
    ax.set_ylim(ylim)
    ax.set_xlim(xlim)
    return ax
