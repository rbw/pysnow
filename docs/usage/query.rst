Querying
========

There are three different ways to create queries using the pysnow library.


Key-value
---------------
Simple. And sufficient in many cases.

.. code-block:: python

	content = incident.get(query={'NUMBER': 'INC012345'}).one()

Using the query builder
-----------------------

The recommended way to create advanced queries.

See the :meth:`pysnow.QueryBuilder` documentation for details.


.. code-block:: python

	# Set start and end range
	start = datetime(1970, 1, 1)
	end = datetime.now() - timedelta(days=20)

	# Query incident records with number starting with 'INC0123', created between 1970-01-01 and 20 days back in time
        qb = (
            pysnow.QueryBuilder()
            .field('number').starts_with('INC0123')
            .AND()
            .field('sys_created_on').between(start, end)
            .AND()
            .field('sys_updated_on').order_descending()
        )

	iterable_content = incident.get(query=qb).all()

SN Pass-through
---------------

It's recommended to use the query builder for complex queries, as it offers error handling and a cleaner way of creating queries.

However, you can still use SN pass-through queries should the query builder not satisfy your needs for some reason.

Below is the pass-through equivalent of the QB in the previous example. You decide ;)


.. code-block:: python

	# Set start and end range
	start = datetime(1970, 1, 1)
	end = datetime.now() - timedelta(days=20)

	# Query incident records with number starting with 'INC0123', created between 1970-01-01 and 20 days back in time
	iterable_content = incident.get(query='numberSTARTSWITHINC0150^sys_created_onBETWEENjavascript:gs.dateGenerate("%s")@javascript:gs.dateGenerate("%s")' % (start, end)).all()
