Creating a new record
=====================

The :meth:`Client.resource.create` takes a dictionary payload with key-values of the record to be created.

.. code-block:: python

    import pysnow

    # Create client object
    c = pysnow.Client(instance='myinstance', user='myusername', password='mypassword')

    # Define a resource, here we'll use the incident table API
    incident = c.resource(api_path='/table/incident')

    # Set the payload
    new_record = {
        'short_description': '<short_description>',
        'description': '<description>'
    }

    # Create a new incident record
    result = incident.create(payload=new_record)

    # Print the created record
    print(result.one())
