Updating a record
-----------------

See the :meth:`pysnow.Request.update` documentation for more details.

.. code-block:: python

   import pysnow

   # Create client object
   s = pysnow.Client(instance='myinstance', user='myusername', password='mypassword')

   # Create a `Request` object by querying for 'INC01234' on table 'incident'
   r = s.query(table='incident', query={'number': 'INC01234'})

   # Update some properties
   res = r.update({'short_description': 'This is a test', 'description': 'Hello from pysnow!'})

   # Print the updated record
   print(res)

