Deleting a record
=================

Deletes the record returned from the query.
Successfully deleting a record returns a dictionary containing the result.

.. note::
    Deletion of multiple records is **not supported**.

.. code-block:: python

    import pysnow

    # Create client object
    c = pysnow.Client(instance='myinstance', user='myusername', password='mypassword')

    # Define a resource, here we'll use the incident table API
    incident = c.resource(api_path='/table/incident')

    # Delete incident with number 'INC012345'
    result = incident.delete(query={'number': 'INC012345'})



