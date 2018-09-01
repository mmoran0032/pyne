

import numpy as np
from scipy.integrate import quad


class Rebinner:
    def __init__(self, *, rebinnned_counts=None, rebinnned_energies=None):
        self.rb_counts = rebinnned_counts
        self.rb_energies = rebinnned_energies

    def create_arrays(self, low=0, high=7000, width=10):  # energies in keV
        bin_count = int((high - low) / width) + 1
        self.rb_energies = np.linspace(low, high, bin_count)
        self.rb_counts = np.zeros(bin_count)

    def rebin(self, adc, fresh_array=True):
        if fresh_array:
            self.rb_counts = np.zeros(self.rb_energies.shape)
        insertion, energy_stack = self._find_insertion_points(
            adc.energies, self.rb_energies)
        easy_counts, hard_counts = self._divide_counts(adc.counts, insertion)
        self._rebin_easy_counts(easy_counts, insertion)
        self._rebin_hard_counts(adc, hard_counts, insertion, energy_stack)
        return self.rb_counts, self.rb_energies

    def _find_insertion_points(self, old_energies, new_energies):
        temp = np.append(old_energies, 2 * old_energies[-1] - old_energies[-2])
        energy_stack = np.vstack((temp[:-1], temp[1:])).T
        return np.searchsorted(new_energies, energy_stack), energy_stack

    def _divide_counts(self, counts, insertion_points):
        mask = insertion_points[:, 0] == insertion_points[:, 1]
        easy_counts = np.where(mask, counts, 0)
        hard_counts = np.where(mask, 0, counts)
        return easy_counts, hard_counts

    def _rebin_easy_counts(self, counts, insertion_points):
        data = np.vstack((insertion_points[:, 0], counts)).T
        data = data[np.where(data[:, 1])]
        for index, value in data:
            self.rb_counts[index] += value

    def _rebin_hard_counts(self, adc, counts, insertion_points, energy_stack):
        data = np.vstack((*insertion_points.T, counts, *energy_stack.T)).T
        data = data[np.where(data[:, 2])]
        for index_0, index_1, value, energy_0, energy_1 in data:
            index_0, index_1, value = int(index_0), int(index_1), int(value)
            local_poly = self._create_local_polynomial(adc, index_0)
            energy_data = [energy_0, energy_1, self.rb_energies[index_0]]
            counts = self._redistribute_counts(value, local_poly, energy_data)
            self.rb_counts[index_0] += counts[0]
            self.rb_counts[index_1] += counts[1]

    def _create_local_polynomial(self, adc, index, degree=5):
        locations = [self.rb_energies[index] - 40,
                     self.rb_energies[index] + 40]
        energy_locs = np.searchsorted(adc.energies, locations)
        pars = np.polyfit(np.take(adc.energies, np.arange(*energy_locs)),
                          np.take(adc.counts, np.arange(*energy_locs)),
                          deg=degree)
        return np.poly1d(pars)

    def _redistribute_counts(self, counts, poly, energies):
        if counts < 10:
            # low statistics, so simple overlap
            p = (energies[2] - energies[0]) / (energies[1] - energies[0])
        else:
            integrals = (quad(poly, energies[0], energies[2])[0],
                         quad(poly, energies[0], energies[1])[0])
            p = abs(integrals[0] / integrals[1])
        counts_0 = np.random.binomial(1, p, size=counts).sum()
        return counts_0, counts - counts_0
