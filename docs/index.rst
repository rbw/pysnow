.. title:: pysnow

pysnow
======

Python library for the ServiceNow REST API



.. toctree::
   :maxdepth: 1

   request
   query
   client


Usage
-----
Go  `here <usage>`_ for usage examples.

Installation
------------
# pip install pysnow

Limitations
-----------
Currently `delete()` and `update()` operations only works for queries yielding a single result.
If there's a demand, this support will be implemented into the API along with `force_multiple` to avoid accidents.

Compatibility
-------------
Python 2 and 3.

