

import os

import pyne


class Experiment:
    def __init__(self, raw_directory, h5_directory, *,
                 raw_file='run{:03d}-13328.evt', h5_file='run{:03d}.h5'):
        self.raw_directory = raw_directory
        self.raw_file = raw_file
        self.h5_directory = h5_directory
        self.h5_file = h5_file
        self.loaded_run_numbers = []
        self.loaded_runs = []

    def load_run(self, run_number):
        if run_number not in self.loaded_run_numbers:
            raw_filename = os.path.join(self.raw_directory,
                                        self.raw_file.format(run_number))
            h5_filename = os.path.join(self.h5_directory,
                                       self.h5_file.format(run_number))
            data = pyne.Data('evt', raw_filename, h5_filename)
            data.load_data()
            self.loaded_run_numbers.append(run_number)
            self.loaded_runs.append(data)
            return data
        index = self.loaded_run_numbers.index(run_number)
        return self.loaded_runs[index]
