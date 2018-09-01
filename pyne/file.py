

import json
from pathlib import Path

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
            print(f'Attribute {key} not present')
