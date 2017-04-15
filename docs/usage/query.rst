Creating a query
================

Although optional, querying a good way to specify what you're after.


Using key-value
^^^^^^^^^^^^^^^
Simple. And sufficient in many cases.

.. code-block:: python

	# Query incident records with 'number' that equals 'INC012345'
	r = s.query(table='incident', query={'number': 'INC012345'})

Using the query builder
^^^^^^^^^^^^^^^^^^^^^^^
Perhaps a bit verbose, but pretty simple and powerful.

See the :meth:`pysnow.QueryBuilder` documentation for more details.


.. code-block:: python

	from datetime import datetime as dt
	from datetime import timedelta as td

	# Set start and end range
	start = dt(1970, 1, 1)
	end = dt.now() - td(days=20)

	# Query incident records with number starting with 'INC0123', created between 1970-01-01 and 20 days back in time
	qb = pysnow.QueryBuilder()\
	     .field('number').starts_with('INC0123')\
	     .AND()\
	     .field('sys_created_on').between(start, end)

	r = s.query('incident', query=qb)

SN Pass-through
^^^^^^^^^^^^^^^
It's a one-liner. Quite obscure. But hey, it's a one-liner.

.. code-block:: python

	# Query incident records starting with 'INC012' or short_description containing 'test'
	r = s.query(table='incident', query='numberSTARTSWITHINC012^ORshort_descriptionLIKEtest')
