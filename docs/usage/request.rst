Creating a request
==================

See the :meth:`Request documentation <pysnow.Request>` for more info

Creating a new record
---------------------

See the :meth:`pysnow.Request.insert` documentation for more details.

.. code-block:: python

    # Create a new record
    result = s.insert(table='incident', payload={'field1': 'value1', 'field2': 'value2'})

    # Print out the number of the created record
    print(result['number'])


Getting a single record
------------------------

Here we'll utilize get_one(), a convenience function for getting a single record without having to use a generator.

See the :meth:`pysnow.Request.get_one` documentation for more details.

.. code-block:: python

    request = s.query(table='incident', query={'number': 'INC01234'})

    # Fetch one record and filter out everything but 'number' and 'sys_id' from the results
    result = request.get_one(fields=['number', 'sys_id'])
    print(result['number'])


Getting multiple sorted records
-------------------------------

get_all() returns a generator response (iterable) , also, this method chains linked responses.

See the :meth:`pysnow.Request.get_all` documentation for more details.

.. code-block:: python

    request = s.query(table='incident', query={'state': 2})

    # Fetch multiple records sorted by the category field in ascending order, with a secondary sort by created_on in descending order.
    # Finally, iterate over the results and print out sys_id for each record.
    while record in request.get_all(order_by=['category', '-created_on']):
        print(record['sys_id'])


Updating a record
-----------------

See the :meth:`pysnow.Request.update` documentation for more details.

.. code-block:: python

    request = s.query(table='incident', query={'number': 'INC01234'})

    # Update the record
    result = request.update({'description': 'test'})

    print("Record '%s' was successfully updated" % result)



Deleting a record
---------------------

See the :meth:`pysnow.Request.delete` documentation for more details.

.. code-block:: python

    # Query the incident table by number
    request = s.query(table='incident', query={'number': 'INC01234'})

    # Delete the record
    result = request.delete()

    if result['success'] == True:
        print("Record deleted")



Request error handling
----------------------

See the :meth:`pysnow.exceptions.UnexpectedResponse` documentation for more details.

`UnexpectedResponse` can be used with all CRUD methods and contains important information of what went wrong when interfacing with the API

.. code-block:: python

   # Create new record and catch possible server response exceptions
   try:
       s.insert(table='incident', payload={'field1': 'value1', 'field2': 'value2'})
   except pysnow.UnexpectedResponse as e:
       print("%s, details: %s" % (e.error_summary, e.error_details))


