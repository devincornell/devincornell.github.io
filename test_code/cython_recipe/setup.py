from distutils.core import setup
from Cython.Build import cythonize
import glob


build_folder = 'cython_files'

setup(
    name='levenshtein', 
    ext_modules = cythonize([f"{build_folder}/*.pyx"], language_level = "3")
)
