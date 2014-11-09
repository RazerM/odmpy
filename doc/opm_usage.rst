*************************
Orbital Parameter Message
*************************

Simple example
==============

Here is an example with the minimum code required to create an OPM file.

.. code:: python

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

Contents of iss.opm:

::

    CCSDS_OPM_VERS = 2.0
    CREATION_DATE  = 2014-11-09T22:35:49.837875
    ORIGINATOR     = NASA

    COMMENT Metadata
    OBJECT_NAME     = International Space Station
    OBJECT_ID       = 1998-067A
    CENTER_NAME     = Earth
    REF_FRAME       = EME2000
    TIME_SYSTEM     = UTC

    COMMENT State Vector Components
    EPOCH   = 2014-11-07T15:30:23
    X       = 6794.0
    Y       =    0.0
    Z       =    0.0
    X_DOT   =    0.0
    Y_DOT   =    7.6
    Z_DOT   =    0.0