.. code-block:: bash
  
	 ______   __  __    ______    __   __    ______    __     __    
	/\  == \ /\ \_\ \  /\  ___\  /\ "-.\ \  /\  __ \  /\ \  _ \ \   
	\ \  _-/ \ \____ \ \ \___  \ \ \ \-.  \ \ \ \/\ \ \ \ \/ ".\ \  
	 \ \_\    \/\_____\ \/\_____\ \ \_\\"\_\ \ \_____\ \ \__/".~\_\ 
	  \/_/     \/_____/  \/_____/  \/_/ \/_/  \/_____/  \/_/   \/_/ 



.. image:: https://travis-ci.org/rbw0/pysnow.svg?branch=master
    :target: https://travis-ci.org/rbw0/pysnow
.. image:: https://coveralls.io/repos/github/rbw0/pysnow/badge.svg?branch=master
	:target: https://coveralls.io/github/rbw0/pysnow?branch=master

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


Creating the `Client` object
----------------------------

.. code-block:: python

   import pysnow

   # Create client object
   s = pysnow.Client(instance='myinstance',
		     user='myusername',
		     password='mypassword',
		     raise_on_empty=True)

Querying
--------

 | Although optional, queries is a simple and powerful way to specify what you're after.
 \ Pysnow offers 3 ways to query the SN REST API.
- Using the `QueryBuilder` (For complex queries)
- Dict type queries (For simple queries, i.e. `equals`)
- SN Pass-through type queries (...)

**Query builder example**

.. code-block:: python

	import pysnow
	from datetime import datetime as dt
	from datetime import timedelta as td
	
	s = pysnow.Client(...)
	
	# Set start and end range
	start = dt(1970, 1, 1)
	end = dt.now() - td(days=20)
	
	# Query incident records with number starting with 'INC0123', created between 1970-01-01 and 20 days back in time
	qb = pysnow.QueryBuilder()\
	     .field('number').starts_with('INC0123')\
	     .AND()\
	     .field('sys_created_on').between(start, end)
	
	r = s.query('incident', query=qb)
	
	# Execute query and iterate over the results, returning only 'number', 'sys_created_on' and 'short_description'
	for row in r.get_all(['number', 'sys_created_on', 'short_description']):
	    print(row)
::



More in the `QueryBuilder documentation <http://pysnow.readthedocs.io/en/latest/query.html>`_



**Dict query example**

.. code-block:: python

	import pysnow
	
	s = pysnow.Client(...)
	
	# Query incident records with 'short_description' that equals 'Happy days'
	r = s.query(table='incident', query={'short_description': 'Happy days'})
	
	# Execute query and iterate over the results returning all fields
	for row in r.get_all():
	    print(row)	

**SN Pass-through example**

.. code-block:: python	

	import pysnow
	
	s = pysnow.Client(...)
	
	# Query incident records starting with 'INC012' or short_description containing 'test'
	r = s.query(table='incident', query='numberSTARTSWITHINC012^ORshort_descriptionLIKEtest')
	
	# Execute query and iterate over the results returning all fields
	for row in r.get_all():
	    print(row)    

Misc usage
----------

.. code-block:: python

   import pysnow

   # Create client object
   s = pysnow.Client(instance='myinstance',
		     user='myusername',
		     password='mypassword',
		     raise_on_empty=True)

   # Create new record and catch possible server response exceptions
   try:
       s.insert(table='incident', payload={'field1': 'value1', 'field2': 'value2'})
   except pysnow.UnexpectedResponse as e:
       print("%s, details: %s" % (e.error_summary, e.error_details))

   # Create a `Request` object by querying for 'INC01234' on table 'incident'
   r = s.query(table='incident', query={'number': 'INC01234'})

   # Fetch one record and filter out everything but 'number' and 'sys_id' from the results
   r.get_one(fields=['number', 'sys_id'])

   # Update
   r.update({'this': 'that'})

   # Attach
   r.attach('path/to/somefile.txt')

   # Delete
   r.delete()

   # Iterate over all records with state == 2 and print out number
   for record in s.query(table='incident', query={'state': 2}).get_all():
       print(record['number'])
       


See the `documentation <http://pysnow.readthedocs.org/>`_ for more examples and other info

Compatibility
-------------
pysnow is compatible with both Python 2 and 3.
Automatically tested: 2.6, 2.7, 3.3, 3.4 and 3.5

Contributors
------
* lingfish
* jcpunk
* AMMullan
* amontalban
* ryancurrah

Author
------
pysnow was created by Robert Wikman <rbw@vault13.org> in 2016

Thank you JetBrains
-------------------
Thank you Jetbrains (www.jetbrains.com) for supporting with IDE licenses!

Quick links
-----------

* http://wiki.servicenow.com/index.php?title=REST_API
* http://wiki.servicenow.com/index.php?title=Table_API
* http://wiki.servicenow.com/index.php?title=Tables_and_Classes
* http://wiki.servicenow.com/index.php?title=Encoded_Query_Strings



