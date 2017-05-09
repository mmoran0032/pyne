

import json
from pathlib import Path

import h5py
import numpy as np


class File:
    def __init__(self, directory):
        self.directory = Path(directory)
        if not self.directory.exists():
            self.directory.mkdir()
        self.metadata_file = self.directory / 'meta.json'
        self.adc_file = self.directory / '{}.npz'

    def __bool__(self):
        return len(list(self.directory.iterdir())) > 0

    def read_adc(self, name):
        f = np.load(str(self.adc_file).format(name))
        return f['bins'], f['counts'], f['energies']

    def save_adc(self, name, bins, counts, energies):
        np.savez(str(self.adc_file).format(name),
                 bins=bins, counts=counts, energies=energies)

    def read_attributes(self):
        with self.metadata_file.open('r') as f:
            return json.load(f)

    def save_attributes(self, attributes):
        with self.metadata_file.open('w') as f:
            json.dump(attributes, f, indent=4)

    def add_attribute(self, **kwargs):
        '''Add and save additional attributes through keyword arguments.'''
        attrs = self.read_attributes()
        attrs.update(kwargs)
        self.save_attributes(attrs)

    def remove_attribute(self, key):
        attrs = self.read_attributes()
        try:
            del attrs[key]
            self.save_attributes(attrs)
        except KeyError:
            print('Attribute {} not present'.format(key))


class FileH5:
    def __init__(self, filename, access='r', *, open=False):
        self.filename = filename
        self.access = access
        if open:
            self.__enter__()

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
        counts = np.array(adc_group['counts'])
        energies = np.array(adc_group['energies'])
        return bins, counts, energies

    def close(self):
        self.f.close()
