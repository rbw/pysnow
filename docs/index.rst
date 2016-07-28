.. title:: pysnow

pysnow
======

Python library for the ServiceNow REST API focused on ease of use and elegant syntax.

The REST API is active by default in all instances, starting with the Eureka release.



.. toctree::
   :maxdepth: 1

   examples
   client
   request


Installation
------------
pip install pysnow

Limitations
-----------
Currently `delete()` and `update()` operations only works for queries yielding a single result.
If there's a demand, delete_multiple() and update_multiple() will be implemented into the API to avoid accidents.

Compatibility
------------
pysnow is compatible with both Python 2 and 3. It's been tested in Python 2.7 and Python 3.4.

Quick links
-----------

* http://wiki.servicenow.com/index.php?title=REST_API
* http://wiki.servicenow.com/index.php?title=Table_API
* http://wiki.servicenow.com/index.php?title=Tables_and_Classes
* http://wiki.servicenow.com/index.php?title=Encoded_Query_Strings

