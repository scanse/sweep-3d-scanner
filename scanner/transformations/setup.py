# Usage: ``python setup.py build_ext --inplace``
from distutils.core import setup, Extension
import numpy
setup(name='_transformations', ext_modules=[Extension('_transformations', [
      'transformations.c'], include_dirs=[numpy.get_include()])])
