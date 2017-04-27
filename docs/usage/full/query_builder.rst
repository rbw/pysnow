Using the query builder
-----------------------

See the :meth:`pysnow.Request.get_all` and :meth:`pysnow.QueryBuilder` documentation for more details.

.. code-block:: python

   import pysnow
   from datetime import datetime as dt
   from datetime import timedelta as td

   # Create client object
   s = pysnow.Client(instance='myinstance', user='myusername', password='mypassword')

   # Set start and end range
   start = dt(1970, 1, 1)
   end = dt.now() - td(days=20)

   # Query incident records with number starting with 'INC0123', created between 1970-01-01 and 20 days back in time
   qb = (
       pysnow.QueryBuilder()
       .field('number').starts_with('INC0123')
       .AND()
       .field('sys_created_on').between(start, end)
   )

   r = s.query('incident', query=qb)

   # Iterate over the result and print out number
   for record in r.get_all():
       print(record['number'])

