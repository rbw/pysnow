Getting a single record
-----------------------

Check out the :meth:`get_one() documentation <pysnow.Request.get_one>` for more info

.. code-block:: python

   import pysnow

   # Create client object
   s = pysnow.Client(instance='myinstance', user='myusername', password='mypassword')

   # Query for 'INC01234' on table 'incident'
   r = s.query(table='incident', query={'number': 'INC01234'})

   # Fetch one record and filter out everything but 'number' and 'sys_id'
   res = r.get_one(fields=['number', 'sys_id'])

   # Print out the result
   print(res)

