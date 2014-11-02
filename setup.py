#!/usr/bin/env python3
from distutils.core import setup, Command


class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import sys,subprocess
        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)


setup(
    name='orbit_data_messages',
    version='0.1.0',
    description='Create valid ASCII OPM, OMM, and OEM files.',
    long_description=open('README').read(),
    author='Frazer McLean',
    author_email='frazer@frazermclean.co.uk',
    url='https://github.com/RazerM/orbit-data-messages',
    packages=['orbitdatamessages'],
    cmdclass = {'test': PyTest},
    classifiers=[
        'License :: OSI Approved :: MIT License'
    ]
)
