Updating a record
-----------------

Check out the :meth:`update() documentation <pysnow.Request.update>` for more info

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

