.. title:: pysnow

pysnow
======

Python library for the ServiceNow REST API focused on ease of use and elegant syntax.

The REST API is active by default in all instances, starting with the Eureka release.



.. toctree::
   :maxdepth: 1

   client
   query
   request
   usage/index


Installation
------------
# pip install pysnow

Limitations
-----------
Currently `delete()` and `update()` operations only works for queries yielding a single result.
If there's a demand, delete_multiple() and update_multiple() will be implemented into the API to avoid accidents.

Compatibility
-------------
Python 2 and 3.

