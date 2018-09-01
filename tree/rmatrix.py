

import numpy as np
import pandas as pd

energy_map = dict(
    eV=0.001,
    keV=1000,
    MeV=1,
)


def load_file(file_path, mass_p, mass_t, unit='keV'):
    try:
        energy_factor = energy_map[unit]
    except KeyError:
        print(f'conversion to {unit} not known, using keV')
        energy_factor = energy_map['keV']
    filename = str(file_path)
    energy, *_, dxs, _ = np.loadtxt(filename, unpack=True)
    rmatrix = pd.DataFrame()
    rmatrix[f'cm_energy_{unit}'] = energy * energy_factor
    rmatrix['dxs_0'] = dxs
    mass_factor = (mass_p + mass_t) / mass_t
    rmatrix[f'lab_energy_{unit}'] = rmatrix[f'cm_energy_{unit}'] * mass_factor
    return rmatrix
