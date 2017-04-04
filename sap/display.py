

import matplotlib.pyplot as plt


class Display:
    def __init__(self, pyne_Data):
        self.data = pyne_Data

    def display_array(self):
        fig, axes = plt.subplots(nrows=4, ncols=4, figsize=(10, 10))
        axis = axes.ravel()

        for ax, adc in zip(axis, self.data.adc[16:]):
            ax.semilogy(adc.energies, adc.counts, nonposy='clip')
            ax.set_ylim((0.1, 1000))
            ax.set_xlim((0, 4000))
            ax.set_title(adc.name)
        fig.tight_layout()
        return fig, axes
