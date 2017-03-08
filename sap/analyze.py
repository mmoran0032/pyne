

import numpy
from scipy.optimize import curve_fit
from scipy.signal import find_peaks_cwt
import statsmodels.api as sm

import pyne
from . import h5_interface


class Analysis:
    def __init__(self, data_directory, out_directory):
        self.data_directory = data_directory
        self.out_directory = out_directory
        self.e = pyne.Experiment(self.data_directory)
        self.e.find_runs()

    def calibrate(self, run_number):
        print('Loading run {}...'.format(run_number))
        self.calibration_run = pyne.Data(self.e[run_number])
        self.calibration_run.read_buffer()
        self.calibration_run.adc.convert_detectors()
        self.calibration_run.adc = self.calibration_run.adc[16:]
        print('Applying calibration...')
        for adc in self.calibration_run.adc:
            self.calibrate_single_detector(adc)
        print('Saving file...')
        self.save_h5_file('calibration.h5', self.calibration_run)

    def calibrate_single_detector(self, adc):
        peaks = self._find_calibration_peaks(adc.counts)
        peak_centers = self._fit_data(adc.bins[:-1], adc.counts, peaks)
        calibrated = self._find_calibration(peak_centers, adc.bins)
        adc.set_calibration(calibrated)

    def _find_calibration_peaks(self, counts, threshold=100):
        peaks = find_peaks_cwt(counts, numpy.array([200, 225, 250]))
        heights = counts[peaks]
        indices = numpy.where(heights > threshold)[0]
        new_peaks = numpy.take(peaks, indices)
        assert new_peaks.shape[0] == 2
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
            bins = sm.add_constant(bins)
        result = sm.OLS(calibration_energies, centers).fit()
        return result.predict(bins)

    def save_h5_file(self, filename, run):
        hdf = h5_interface.File(filename)
        for adc in run.adc:
            hdf.save_array('{}/bins'.format(adc.name), adc.bins)
            hdf.save_array('{}/energy'.format(adc.name), adc.calibrated)
            hdf.save_array('{}/counts'.format(adc.name), adc.counts)
        for key, value in run.run_information.iteritems():
            hdf.save_attribute(key, value)
        for key, value in run.events.iteritems():
            hdf.save_attribute('events/{}'.format(key), value)
