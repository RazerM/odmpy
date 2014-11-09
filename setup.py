#!/usr/bin/env python3
from setuptools import setup, Command, find_packages

import re

INIT_FILE = 'odmpy/__init__.py'
init_data = open(INIT_FILE).read()

metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", init_data))

AUTHOR_EMAIL = metadata['author']
VERSION = metadata['version']
LICENSE = metadata['license']

AUTHOR, EMAIL = re.match(r'(.*) <(.*)>', AUTHOR_EMAIL).groups()


class PyTest(Command):
    """Allow 'python setup.py test' to run without first installing pytest"""
    user_options = []
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys, subprocess
        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)

setup(
    name='odmpy',
    version=VERSION,
    description='Create valid ASCII OPM, OMM, and OEM files.',
    long_description=open('README').read(),
    author=AUTHOR,
    author_email=EMAIL,
    url='https://github.com/RazerM/odmpy',
    packages=find_packages(),
    cmdclass={'test': PyTest},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Astronomy',
        'License :: OSI Approved :: MIT License'
    ],
    license=LICENSE,
    extras_require={
        'test': ['pytest']
    }
)
