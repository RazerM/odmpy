Orbit Data Messages
-------------------

| |Build Status|
| Python 3.4+

This package is for creating valid ASCII OPM, OMM, and OEM files using
Python.

Currently, only the orbital parameter message (OPM) module has been
implemented.

Installation
~~~~~~~~~~~~

.. code:: bash

    $ python3 setup.py install

Testing
~~~~~~~

.. code:: bash

    $ python3 setup.py test

Usage
~~~~~

.. code:: python

    import orbitdatamessages.orbital_parameter_message as opm

.. |Build Status| image:: https://travis-ci.org/RazerM/orbit-data-messages.svg?branch=master
   :target: https://travis-ci.org/RazerM/orbit-data-messages
