from setuptools import setup, find_packages
from version import find_version

setup(
    name = 'annotate',
    author = 'Diego Morais',
    description = 'Annotate each query using the best alignment for which a mapping is known',
    license = 'GPL3',
    version = find_version('annotate', '__init__.py'),
    packages = find_packages()
)
