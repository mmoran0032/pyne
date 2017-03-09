

import os

import h5py


class File:
    def __init__(self, filename, out_directory='data_processed', access='r'):
        self.filename = filename
        self.out_directory = out_directory
        self.path = None
        self.access = access

    def __enter__(self):
        self.f = h5py.File(self._path, self.access)
        return self

    def __exit__(self, *args):
        self.f.close()

    def save_array(self, name, data):
        with h5py.File(self._path, 'w') as f:
            f.create_dataset(name, data=data)

    def read_array(self, name):
        with h5py.File(self._path, 'r') as f:
            data = f[name][:]
        return data

    def save_attribute(self, name, value):
        with h5py.File(self._path, 'w') as f:
            f.attrs[name] = value

    def read_attribute(self, name):
        with h5py.File(self._path, 'r') as f:
            value = f.attrs[name]
        return value

    @property
    def _path(self):
        if self.path is None:
            self.path = os.path.join(self.out_directory, self.filename)
        return self.path
