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

The recommended way to create complex queries.

See the :meth:`pysnow.QueryBuilder` documentation for more details.


.. code-block:: python

	from datetime import datetime as dt
	from datetime import timedelta as td

	# Set start and end range
	start = dt(1970, 1, 1)
	end = dt.now() - td(days=20)

	# Query incident records with number starting with 'INC0123', created between 1970-01-01 and 20 days back in time
    qb = (
        pysnow.QueryBuilder()
        .field('number').starts_with('INC0123')
        .AND()
        .field('sys_created_on').between(start, end)
    )

	r = s.query('incident', query=qb)

SN Pass-through
^^^^^^^^^^^^^^^

It's recommended to use the query builder for complex queries, as it offers a cleaner way to create queries.

However, you can still use SN pass-through queries should the query builder not satisfy your needs for some reason.

This is a pass-through equivalent of the QB example above.

.. code-block:: python

	from datetime import datetime as dt
	from datetime import timedelta as td

	# Set start and end range
	start = dt(1970, 1, 1)
	end = dt.now() - td(days=20)

	# Query incident records with number starting with 'INC0123', created between 1970-01-01 and 20 days back in time
	r = s.query(table='incident', query='numberSTARTSWITHINC0150^sys_created_onBETWEENjavascript:gs.dateGenerate("%s")@javascript:gs.dateGenerate("%s")' % (start, end))
