

from collections.abc import Sequence
from collections import defaultdict
import os


class Experiment(Sequence):
    def __init__(self, data_directory='data'):
        self.data_directory = data_directory
        self.runs = []
        self.runs_grouped = defaultdict(list)

    def __getitem__(self, run_number):
        index = self.run_numbers.index(run_number)
        return self.runs[index]

    def __len__(self):
        return len(self.runs)

    def __iter__(self):
        yield self.runs

    def find_runs(self, *, extension='.evt'):
        files = os.listdir(self.data_directory)
        files = sorted(f for f in files if f.endswith(extension))
        self.runs = ['{}/{}'.format(self.data_directory, f) for f in files]
        self.run_numbers = self._extract_run_numbers(self.runs)

    def _extract_run_numbers(self, names):
        return [self._extract_single_number(n) for n in names]

    def _extract_single_number(self, path):
        name = path.split('/')[1]
        number = name.split('-')[0].replace('run', '')
        return int(number)

    def group_runs(self, category, *group):
        self.runs_grouped[category].extend(group)
