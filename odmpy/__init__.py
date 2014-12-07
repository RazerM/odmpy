#!/usr/bin/env python

__author__ = 'Frazer McLean <frazer@frazermclean.co.uk>'
__version__ = '0.2.5.dev0'
__license__ = 'MIT'
__description__ = 'Create valid ASCII OPM, OMM, and OEM files.'


def test():
    """Run tests from tests directory."""
    import os.path
    import pytest
    pytest.main(os.path.dirname(os.path.abspath(__file__)))
