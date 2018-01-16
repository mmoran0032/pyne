

from pathlib import Path

import numpy as np
import pandas as pd


def load_srim_data(directory_path):
    ''' assume files were saved as energy-{value}eV_depth-{value}A.txt'''
    directory_path = Path(directory_path)
    df = pd.DataFrame()
    for i, filename in enumerate(directory_path.iterdir()):
        energy_eV, depth_A = get_info_from_filename(filename)
        data = load_data(filename)
        df[str(i)] = [energy_eV, depth_A, *sorted(data)]
    return (df.T
            .rename(columns={0: 'energy_eV', 1: 'depth_A'})
            .sort_values(by=['energy_eV', 'depth_A'], ascending=True))


def get_info_from_filename(filename):
    energy, depth = filename.parts[-1].split('_')
    energy_eV = float(energy.split('-')[1][:-2])
    depth_A = float(depth.split('-')[1][:-1])
    return energy_eV, depth_A


def load_data(filename):
    # need to preprocess so that np.loadtxt works
    with filename.open('r') as f:
        data = f.read().replace('T', '')
    with filename.open('w') as f:
        f.write(data)
    _, _, data, *_ = np.loadtxt(filename, skiprows=12, unpack=True)
    return data
