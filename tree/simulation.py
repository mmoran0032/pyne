

import numpy as np

from .rmatrix import load_file
from .srim_data import load_srim_data


class Simulator:
    def __init__(self, rmatrix_args, projectile_srim, target_srim):
        self.rmatrix = load_file(*rmatrix_args)
        self.srim_proj_data = load_srim_data(projectile_srim)
        self.srim_target_data = load_srim_data(target_srim)
        self.thickness = None

    def get_cross_section(self, in_energy, thickness=None):
        _thickness = self._get_thickness(thickness)
        lower_bound = in_energy - _thickness
        return self.rmatrix[(self.rmatrix.iloc[:, -1] < in_energy)
                            & (self.rmatrix.iloc[:, -1] > lower_bound)]

    def _get_thickness(self, thickness):
        if thickness is None and self.thickness is None:
            print('target thickness not provided')
            raise ValueError
        elif thickness is None and self.thickness:
            return self.thickness
        else:
            return thickness


def generate_proton_deviations(d_energy=300, size=10000):
    ''' get energy deviations in eV'''
    return np.random.normal(loc=0, scale=d_energy, size=size)


def generate_random_depths(norm_cross_section, size=10000):
    ''' get depths into target between 1 and 99 percent'''
    depth = np.linspace(1, 99, norm_cross_section.shape[0])
    return np.random.choice(depth, size=size, p=norm_cross_section)
