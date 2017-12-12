Fetching data
=============

The :meth:`pysnow.Resource.get` returns an instance of :class:`pysnow.Response`, which exposes a public API with
various convenience methods for getting the data you're after.

.. note::
The **Response API** uses an incremental stream parser when fetching results, which dramatically reduces memory usage,
    load on the ServiceNow instance and response times.

    Example: using **first()** on a query that would yield 50000 records
    when iterated on, would yield only records contained in the first **4096 bytes** (the default) of the response.


See the :class:`pysnow.Response` documentation for more details.

Multiple records
----------------

The :meth:`pysnow.Response.all` returns a generator that yields records as iterated on.


.. code-block:: python

    import pysnow

    # Create client object
    c = pysnow.Client(instance='myinstance', user='myusername', password='mypassword')

    # Define a resource, here we'll use the incident table API
    incident = c.resource(api_path='/table/incident')

    # Query for incidents with state 1
    response = incident.get(query={'state': 1})

    # Iterate over the result and print out `sys_id` of the matching records.
    for record in response.all():
        print(record['sys_id'])


First record
------------

The :meth:`pysnow.Response.first` returns the first record in a result containing one or more records.
If the result contain no records, an exception is thrown.


.. code-block:: python

    import pysnow

    # Create client object
    c = pysnow.Client(instance='myinstance', user='myusername', password='mypassword')

    # Define a resource, here we'll use the incident table API
    incident = c.resource(api_path='/table/incident')

    # Query for incidents with state 3
    response = incident.get(query={'state': 3})

    # Print out the first match
    print(response.first())

First or none
-------------

The :meth:`pysnow.Response.first_or_none` returns the first record in a result containing one or more records.
None is returned if the result doesn't contain any records.


.. code-block:: python

    import pysnow

    # Create client object
    c = pysnow.Client(instance='myinstance', user='myusername', password='mypassword')

    # Define a resource, here we'll use the incident table API
    incident = c.resource(api_path='/table/incident')

    # Query for incidents with state 3
    response = incident.get(query={'state': 3})

    # Print out the first match, or `None`
    print(response.first_or_none())




Exactly one
-----------

The :meth:`pysnow.Response.one` returns exactly one record.
If the result contains zero or multiple records, an exception is raised.


.. code-block:: python

    import pysnow

    # Create client object
    c = pysnow.Client(instance='myinstance', user='myusername', password='mypassword')

    # Define a resource, here we'll use the incident table API
    incident = c.resource(api_path='/table/incident')

    # Query for incident with number INC012345
    response = incident.get(query={'number': 'INC012345'})

    # Print out the matching record
    print(response.one())


One or none
-----------

The :meth:`pysnow.Response.one_or_none` returns one record, or None if no matching records were found.
An exception is raised if the result contains multiple records


.. code-block:: python

    import pysnow

    # Create client object
    c = pysnow.Client(instance='myinstance', user='myusername', password='mypassword')

    # Create a new resource for the incident table API
    incident = c.resource(api_path='/table/incident')

    # Query for incident with number INC012345
    response = incident.get(query={'number': 'INC012345'})

    # Print out the matching record, or `None` if no matches were found.
    print(response.one_or_none())



