Fetching data
=============

The :meth:`pysnow.Resource.get` returns an instance of :class:`pysnow.Response`, which exposes an interface to the
various methods available for getting the data you're after.

.. note::
    Fetching large amounts of data? Use the incremental stream parser by passing stream=True to get(),
    this will return a memory-friendly generator instead of a buffered result.


Multiple records
----------------

In this example, :meth:`pysnow.Response.all` returns a generator (stream=True), which is iterated on in chunks of 8192 bytes by default.


.. code-block:: python

    import pysnow

    # Create client object
    c = pysnow.Client(instance='myinstance', user='myusername', password='mypassword')

    # Define a resource, here we'll use the incident table API
    incident = c.resource(api_path='/table/incident')

    # Query for incidents with state 1
    response = incident.get(query={'state': 1}, stream=True)

    # Iterate over the result and print out `sys_id` of the matching records.
    for record in response.all():
        print(record['sys_id'])


First record
------------

The :meth:`pysnow.Response.first` returns the first record in a result containing one or more records.
An exception is raised if the result doesn't contain any records.


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
An exception is raised if the result is empty or contains multiple records.


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



