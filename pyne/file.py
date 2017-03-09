

import os

import h5py


class File:
    def __init__(self, filename, out_directory='data_processed', access='r'):
        self.filename = filename
        self.out_directory = out_directory
        self.access = access
        self.path = None

    def __enter__(self):
        self.f = h5py.File(self._path, self.access)
        return self

    def __exit__(self, *args):
        self.f.close()

    def save_attributes(self, **attributes):
        for key, value in attributes.items():
            self.f.create_dataset(key, data=value)

    def save_adc(self, name, bins, counts, energies):
        adc = self.f.create_group(name)
        adc.attrs['bins'] = bins
        adc.create_dataset('counts', data=counts)
        adc.create_dataset('energies', data=energies)

    def read_attributes(self):
        return {key: value for key, value in self.f.attrs.items()}

    def read_adc(self, name):
        bins = self.f['{}/bins'.format(name)]
        counts = self.f['{}/counts'.format(name)]
        energies = self.f['{}/energies'.format(name)]
        return bins, counts, energies

    @property
    def _path(self):
        if self.path is None:
            self.path = os.path.join(self.out_directory, self.filename)
        return self.path
