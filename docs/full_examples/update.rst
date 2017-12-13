Updating a record
=================

The :meth:`Client.resource.update` takes a **payload** and **query** to perform an update.

.. note::
    This method returns the updated record (dict) if the operation was successful.
    Refer to :meth:`Client.resource.custom` if you want a **Response** object back.

.. note::
    Updating multiple records is **not supported**.


.. code-block:: python

    import pysnow

    # Create client object
    c = pysnow.Client(instance='myinstance', user='myusername', password='mypassword')

    # Define a resource, here we'll use the incident table API
    incident = c.resource(api_path='/table/incident')

    update = {'short_description': 'New short description', 'state': 5}

    # Update 'short_description' and 'state' for 'INC012345'
    updated_record = incident.update(query={'number': 'INC012345'}, payload=update)

    # Print out the updated record
    print(updated_record)

