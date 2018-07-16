

from pathlib import Path
from setuptools import setup, find_packages


with Path('README.rst').open() as f:
    readme = f.read()

with Path('LICENSE').open() as f:
    license = f.read()

with Path('src/pyne/__init__.py').open() as f:
    data = f.read().split('\n')
    for line in data:
        if line.startswith('__version__'):
            version = line.split()[-1].replace('\'', '')
        elif line.startswith('__author__'):
            author = ' '.join(line.split()[-2:]).replace('\'', '')

setup(
    name='pyne',
    version=version,
    description='Python for Nuclear Experiments',
    long_description=readme,
    author=author,
    author_email='mmoran0032@gmail.com',
    url=r'https://github.com/mmoran0032/pyne',
    license=license,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True
)
