Creating a new record
=====================

The :meth:`Client.resource.create` takes a dictionary payload with key-values of the record to be created.


.. note::
    This method calls :meth:`pysnow.Resource.one` if the record was created successfully, returning a dictionary of the created record.


.. code-block:: python

    import pysnow

    # Create client object
    c = pysnow.Client(instance='myinstance', user='myusername', password='mypassword')

    # Define a resource, here we'll use the incident table API
    incident = c.resource(api_path='/table/incident')

    # Set the payload
    new_record = {
        'short_description': 'Pysnow created incident',
        'description': 'This is awesome'
    }

    # Create a new incident record
    result = incident.create(payload=new_record)



