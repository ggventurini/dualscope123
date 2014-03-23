#!/usr/bin/env python

import os
from setuptools import setup, find_packages, Extension
__version__ = "1.0rc1"

def read(fname):
    try:
        with open(os.path.join(os.path.dirname(__file__), fname)) as fp:
            return fp.read()
    except IOError:
        return ""

setup(
    name='dualscope123',
    version=__version__,
    packages=find_packages(),
    package_data={
      'dualscope123': []
    },
    install_requires=['numpy', 'pyaudio'],
    entry_points = { 'console_scripts': [ 'dualscope123 = dualscope123.main:main', ], },
    zip_safe=False,
    include_package_data=True,
    ext_modules=[Extension('dualscope123.probes.libethc', ['dualscope123/probes/ethc.c'])],
    author="Giuseppe Venturini and others",
    author_email="giuseppe.g.venturini@ieee.org",
    description="A versatile oscilloscope + spectrum analyzer in Python/QWT",
    long_description=''.join([read('pypi_description.rst'), '\n\n',
                              read('CHANGES.rst')]),
    license="GPLv3",
    keywords="oscilloscope scope spectrum data",
    url="http://github.com/ggventurini/dualscope123",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GPL v3 License",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7"]
)

