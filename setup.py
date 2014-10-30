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


setup(name='Orbit Data Messages',
      version='0.1.0',
      description='Write valid ODM files.',
      long_description=open('README.md').read(),
      author='Frazer McLean',
      author_email='frazer@frazermclean.co.uk',
      url='https://github.com/RazerM/orbit-data-messages',
      packages=['orbitdatamessages'],
      cmdclass = {'test': PyTest})
