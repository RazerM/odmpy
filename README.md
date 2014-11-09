## Orbit Data Messages
[![Build Status](http://img.shields.io/travis/RazerM/odmpy.svg?style=flat-square)](https://travis-ci.org/RazerM/odmpy) [![Test Coverage](http://img.shields.io/codecov/c/github/RazerM/odmpy.svg?style=flat-square)](https://codecov.io/github/RazerM/odmpy) [![PyPI Version](http://img.shields.io/pypi/v/odmpy.svg?style=flat-square)](https://pypi.python.org/pypi/odmpy/) [![Python Version](http://img.shields.io/badge/python-3.4%2B-brightgreen.svg?style=flat-square)](https://www.python.org/download/releases/3.4.0/) [![MIT License](http://img.shields.io/badge/license-MIT-blue.svg?style=flat-square)](https://raw.githubusercontent.com/RazerM/odmpy/master/LICENSE)



odmpy is a python package for creating valid ASCII OPM, OMM, and OEM files.

Currently, only the orbital parameter message (OPM) module has been implemented.

### Installation

```bash
$ pip install odmpy
```

### Testing

```bash
$ python setup.py test
```

### Usage

```python
import odmpy.opm as opm
```