Getting request item count
--------------------------

The count property uses the ServiceNow stats API to obtain the number of items a query would yield.

See the :prop:`pysnow.Request.count` for more information.


.. code-block:: python

   import pysnow

   # Create client object
   s = pysnow.Client(instance='myinstance', user='myusername', password='mypassword')

   # Get all incidents
   r = s.query('incident', query={})

   print("This query would yield %d records." % r.count)


