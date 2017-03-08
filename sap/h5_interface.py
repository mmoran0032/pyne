

import os

import h5py


class File:
    def __init__(self, filename, out_directory='data_processed'):
        self.filename = filename
        self.out_directory = out_directory

    def save_array(self, name, data):
        with h5py.File(self._path, 'w') as f:
            f.create_dataset(name, data=data)

    def read_array(self, name):
        with h5py.File(self._path, 'r') as f:
            data = f[name][:]
        return data

    @property
    def _path(self):
        return os.path.join(self.out_directory, self.filename)
