

from setuptools import setup, find_packages


with open('README.rst', 'r') as f:
    readme = f.read()

with open('LICENSE', 'r') as f:
    license = f.read()

with open('pyne/__init__.py', 'r') as f:
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
    packages=find_packages(exclude=('tests',))
)
