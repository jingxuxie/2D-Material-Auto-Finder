

from distutils.core import setup
import py2exe

setup(console=['test.py'])



'''
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = ["numba", "pyqtgraph", "scipy"])

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('Sony_view20.py', base=base)
]

setup(name='test',
      version = '0.1',
      description = '',
      options = dict(build_exe = buildOptions),
      executables = executables)
'''