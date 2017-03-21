

import h5py
import numpy


class File:
    def __init__(self, filename, access='r'):
        self.filename = filename
        self.access = access
        self.f = h5py.File(self.filename, self.access)

    def __enter__(self):
        self.f = h5py.File(self.filename, self.access)
        return self

    def __exit__(self, *args):
        self.close()

    def save_attributes(self, attributes):
        for key, value in attributes.items():
            self.f.attrs[key] = value

    def save_adc(self, name, bins, counts, energies):
        adc = self.f.create_group(name)
        adc.attrs['bins'] = bins
        adc.create_dataset('counts', data=counts, shape=(bins,))
        adc.create_dataset('energies', data=energies, shape=(bins,))

    def read_attributes(self):
        return {key: value for key, value in self.f.attrs.items()}

    def read_adc(self, name):
        adc_group = self.f[name]
        bins = adc_group.attrs['bins']
        counts = numpy.array(adc_group['counts'])
        energies = numpy.array(adc_group['energies'])
        return bins, counts, energies

    def close(self):
        self.f.close()
