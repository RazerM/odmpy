## Orbit Data Messages
[![Build Status][bsi]][bsl] [![Test Coverage][tci]][tcl] [![PyPI Version][ppi]][ppl] [![Python Version][pvi]][pvl] [![MIT License][mli]][mll]

  [bsi]: http://img.shields.io/travis/RazerM/odmpy.svg?style=flat-square
  [bsl]: https://travis-ci.org/RazerM/odmpy
  [tci]: http://img.shields.io/codecov/c/github/RazerM/odmpy.svg?style=flat-square
  [tcl]: https://codecov.io/github/RazerM/odmpy
  [ppi]: http://img.shields.io/pypi/v/odmpy.svg?style=flat-square
  [ppl]: https://pypi.python.org/pypi/odmpy/
  [pvi]: http://img.shields.io/badge/python-3.0%2B-brightgreen.svg?style=flat-square
  [pvl]: https://www.python.org/downloads/
  [mli]: http://img.shields.io/badge/license-MIT-blue.svg?style=flat-square
  [mll]: https://raw.githubusercontent.com/RazerM/odmpy/master/LICENSE



odmpy is a python package for creating valid ASCII OPM, OMM, and OEM files.

Currently, only the orbital parameter message (OPM) module has been implemented.

### Installation

```bash
$ pip install odmpy
```

### Example

```python
import odmpy.opm as opm
from datetime import datetime

header = opm.Header(originator='NASA')

metadata = opm.Metadata(
    object_name='International Space Station',
    object_id='1998-067A',
    center_name='Earth',
    ref_frame=opm.RefFrame.EME2000,
    time_system=opm.TimeSystem.UTC)

sv = opm.DataBlockStateVector(
    epoch=datetime(2014, 11, 7, 15, 30, 23),
    x=6794,
    y=0,
    z=0,
    x_dot=0,
    y_dot=7.6,
    z_dot=0)

data = opm.Data(state_vector=sv)

iss = opm.Opm(header, metadata, data)

with open('iss.opm', 'w') as f:
    iss.write(f)
```

### [Go to Package Documentation](http://pythonhosted.org/odmpy/)