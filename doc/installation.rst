************
Installation
************

The odmpy package can be installed on any system running **Python 3**.

The recommended installation method is using ``pip``.

pip
===

.. code:: bash

    $ pip install odmpy

Git
===

.. code-block:: sh

	$ git clone https://github.com/RazerM/odmpy.git
	Cloning into 'odmpy'...

Check out a `release tag <https://github.com/RazerM/odmpy/releases>`_:

.. parsed-literal::

	$ cd odmpy
	$ git checkout |version|

Test and install:

.. code-block:: sh

	$ python setup.py test
	running test...
	$ python setup.py install
	running install...