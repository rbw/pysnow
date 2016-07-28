.. title:: pysnow

pysnow
======

Python library for the ServiceNow REST API focused on ease of use, simple code and elegant syntax.

The REST API is active by default in all instances, starting with the Eureka release.

Documentation
-------------
Click `here <http://pysnow.readthedocs.org/>`_ to see the documentation

Installation
------------
# pip install pysnow


Basic usage
-----------

.. code-block:: python

   import pysnow

   # Create client object
   s = pysnow.Client(instance='myinstance',
		     user='myusername',
		     password='mypassword',
		     raise_on_empty=True)

   # Create a new record
   s.insert(table='incident', payload={'field1': 'value1', 'field2': 'value2'})

   # Create a `Request` object by querying for 'INC01234' on table 'incident'
   r = s.query(table='incident', query={'number': 'INC01234'})

   # Fetch one record and filter out everything but 'number' and 'sys_id' from the results
   r.get_one(fields=['number', 'sys_id'])

   # Update
   r.update({'this': 'that'})

   # Delete
   r.delete()
   
   # Iterate over all records with state == 2 and print out number
   for record in s.query(table='incident', query={'state': 2}).get_all():
       print(record['number'])


See the `documentation <http://pysnow.readthedocs.org/>`_ for more examples and other info

Compatibility
-------------
pysnow is compatible with both Python 2 and 3. It's been tested in Python 2.7 and Python 3.4.

Author
------
pysnow was created by Robert Wikman <rbw@vault13.org> in 2016

Quick links
-----------

* http://wiki.servicenow.com/index.php?title=REST_API
* http://wiki.servicenow.com/index.php?title=Table_API
* http://wiki.servicenow.com/index.php?title=Tables_and_Classes
* http://wiki.servicenow.com/index.php?title=Encoded_Query_Strings



