

import numpy as np
from scipy.optimize import curve_fit
from scipy.signal import find_peaks_cwt
import statsmodels.api as sm

from .functions import gaussian


class Calibrator:
    def __init__(self, cal_data):
        self.cal_data = cal_data

    def find_calibration(self):
        for adc in self.cal_data.adc[16:]:
            self._calibrate_single_detector(adc)

    def calibrate(self, data):
        for adc, cal_adc in zip(data.adc[16:], self.cal_data.adc[16:]):
            energies = cal_adc.energies
            adc.set_calibration(energies)
        data.save_data()

    def _calibrate_single_detector(self, adc):
        peaks = self._find_calibration_peaks(adc)
        peak_centers = self._fit_data(adc.bins[:-1], adc.counts, peaks)
        energies = self._find_calibration(peak_centers, adc.bins)
        adc.set_calibration(energies)

    def _find_calibration_peaks(self, adc, threshold=50):
        peaks = find_peaks_cwt(adc.counts, np.array([175, 200, 225, 250]))
        heights = adc.counts[peaks]
        new_peaks = np.take(peaks, np.where(heights > threshold)[0])
        assert new_peaks.shape[0] == 2, adc.name
        return new_peaks

    def _fit_data(self, bins, counts, peaks):
        center_0 = self._fit_single_gaus(bins, counts, peaks[0])
        center_1 = self._fit_single_gaus(bins, counts, peaks[1])
        return center_0, center_1

    def _fit_single_gaus(self, bins, counts, peak):
        p0 = [600, peak, 50]
        pars, _ = curve_fit(gaussian, bins, counts, p0=p0)
        return pars[1]

    def _find_calibration(self, centers, bins):
        calibration_energies = [3182.69, 5485.56]  # 148Gd/241Am mixed source
        centers = sm.add_constant(centers)
        bins = sm.add_constant(bins[:-1])
        result = sm.OLS(calibration_energies, centers).fit()
        return result.predict(bins)
