

from collections.abc import Sequence
import os
import re


class Experiment(Sequence):
    def __init__(self, data_directory='data'):
        self.data_directory = data_directory
        self.runs = []

    def __getitem__(self, run_number):
        index = self.run_numbers.index(run_number)
        return self.runs[index]

    def __len__(self):
        return len(self.runs)

    def __iter__(self):
        yield self.runs

    def find_runs(self, *, extension='.evt', format=None):
        files = os.listdir(self.data_directory)
        if format is not None:
            files = self._filter_by_format(files, format)
        else:
            files = sorted(f for f in files if f.endswith(extension))
        self.runs = files
        self.run_numbers = self._extract_run_numbers(self.runs)

    def _filter_by_format(self, files, format):
        pattern = re.compile(format)
        return sorted(list(filter(pattern.match, files)))

    def _extract_run_numbers(self, names):
        return [self._extract_single_number(n) for n in names]

    def _extract_single_number(self, name):
        number = name.split('-')[0].replace('run', '')
        return int(number)
