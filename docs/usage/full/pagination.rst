Multiple records with limit and offset (pagination)
---------------------------------------------------

See the :meth:`pysnow.Request.get_multiple` documentation for more details.

.. code-block:: python

   import pysnow

   # Create client object
   s = pysnow.Client(instance='myinstance', user='myusername', password='mypassword')

   # Get all incidents
   r = s.query('incident', query={})

   # Order by 'created_on' desc, skip the first 60 records and limit the number of records returned to 20
   for record in r.get_multiple(offset=60, limit=20, order_by=['-created_on']):
       print(record['number'])

