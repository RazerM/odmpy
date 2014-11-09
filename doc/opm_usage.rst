*************************
Orbital Parameter Message
*************************

Usage
=====

.. function:: dumps(obj, skipkeys=False, ensure_ascii=True, indent=None, \
    separators=None[, default=None[, sort_keys=False]])

   Serialize *obj* to a JSON formatted :class:`str` using this :ref:`conversion
   table <py-to-json-table>`.  The arguments have the same meaning as in
   :func:`dump`.

.. code:: python

    import odmpy.opm as opm

    header = opm.Header()
