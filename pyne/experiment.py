

from collections.abc import Sequence
import os

from . import data


class Experiment(Sequence):
    def __init__(self, data_directory='data', out_directory='data_processed'):
        self.data_directory = data_directory
        self.out_directory = out_directory

    def __getitem__(self, run_number):
        index = self.run_numbers.index(run_number)
        return data.Data(self.data_runs[index], self.out_runs[index])

    def __len__(self):
        return len(self.runs)

    def __iter__(self):
        yield self.runs

    def find_all(self):
        self.find_runs()
        self.find_auxiliary()
        print('{} evt and {} aux found'.format(
            len(self.data_runs), len(self.aux_runs)))

    def find_runs(self):
        files = os.listdir(self.data_directory)
        files = sorted(f for f in files if f.endswith('.evt'))
        self.data_runs = [os.path.join(self.data_directory, f) for f in files]
        self.out_runs = self._create_processed_file_list(files, '-')
        self.run_numbers = self._extract_run_numbers(self.data_runs)

    def _create_processed_file_list(self, files, split_char):
        basenames = ['{}.h5'.format(f.split(split_char)[0]) for f in files]
        return [os.path.join(self.out_directory, f) for f in basenames]

    def _extract_run_numbers(self, names):
        return [self._extract_single_number(n) for n in names]

    def _extract_single_number(self, path):
        name = path.split('/')[1]
        number = name.split('-')[0].replace('run', '')
        return int(number)

    def find_auxiliary(self):
        files = os.listdir(self.data_directory)
        files = sorted(f for f in files if not f.endswith('evt'))
        self.aux_runs = [os.path.join(self.data_directory, f) for f in files]
        self.aux_out = self._create_processed_file_list(files, '.')
