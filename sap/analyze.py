

import numpy
from scipy.optimize import curve_fit
from scipy.signal import find_peaks_cwt
import statsmodels.api as sm

import pyne


class Analysis:
    def __init__(self, data_directory, out_directory):
        self.data_directory = data_directory
        self.out_directory = out_directory
        self.e = pyne.Experiment(self.data_directory, self.out_directory)
        self.e.find_runs()

    def calibrate(self, run_number):
        print('Loading run {}...'.format(run_number))
        self.calibration_run = self.e[run_number]
        self.calibration_run.load_data()
        self.calibration_run.adc = self.calibration_run.adc
        print('Applying calibration...')
        for adc in self.calibration_run.adc[16:]:
            self.calibrate_single_detector(adc)
        print('Saving file...')
        self.calibration_run.save_data()

    def calibrate_single_detector(self, adc):
        peaks = self._find_calibration_peaks(adc)
        peak_centers = self._fit_data(adc.bins[:-1], adc.counts, peaks)
        calibrated = self._find_calibration(peak_centers, adc.bins)
        adc.set_calibration(calibrated)

    def _find_calibration_peaks(self, adc, threshold=50):
        peaks = find_peaks_cwt(adc.counts, numpy.array([175, 200, 225, 250]))
        heights = adc.counts[peaks]
        indices = numpy.where(heights > threshold)[0]
        new_peaks = numpy.take(peaks, indices)
        assert new_peaks.shape[0] == 2, adc.name
        return new_peaks

    def _fit_data(self, bins, counts, peaks):
        center_0 = self._fit_single_gaus(bins, counts, peaks[0])
        center_1 = self._fit_single_gaus(bins, counts, peaks[1])
        return center_0, center_1

    def _fit_single_gaus(self, bins, counts, peak):
        def _single_gaus(x, A, mu, sig):
            return A * numpy.exp(-(x - mu)**2 / (2 * sig**2))

        p0 = [600, peak, 50]
        pars, _ = curve_fit(_single_gaus, bins, counts, p0=p0)
        return pars[1]

    def _find_calibration(self, centers, bins, zero_intercept=False):
        calibration_energies = [3182.69, 5485.56]  # 148Gd/241Am mixed source
        if not zero_intercept:
            centers = sm.add_constant(centers)
            bins = sm.add_constant(bins[:-1])
        result = sm.OLS(calibration_energies, centers).fit()
        return result.predict(bins)
