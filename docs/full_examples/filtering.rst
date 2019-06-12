Filtering fields
================

The `fields` parameter can be used for selecting which fields to return in the response.


.. code-block:: python

    import pysnow

    # Create client object
    c = pysnow.Client(instance='myinstance', user='myusername', password='mypassword')

    # Define a resource, here we'll use the incident table API
    incident = c.resource(api_path='/table/incident')

    # Query for incidents with state 3
    response = incident.get(query={'state': 3}, fields=['sys_id', 'number', 'description'])

    # Print out the first match
    print(response.first())
