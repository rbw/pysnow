Deleting a record
-----------------

See the :meth:`pysnow.Request.delete` documentation for more details.

.. code-block:: python

   import pysnow

   # Create client object
   s = pysnow.Client(instance='myinstance', user='myusername', password='mypassword')

   # Delete record with number 'INC012345'
   res = s.query(table='incident', query={'number': 'INC012345'}).delete()

   # Print out the result
   print(res)

