Getting multiple records
------------------------

See the :meth:`pysnow.Request.get_multiple` documentation for more details.

.. code-block:: python

   import pysnow

   # Create client object
   s = pysnow.Client(instance='myinstance', user='myusername', password='mypassword')

   # Get all incidents
   r = s.query('incident', query={})

   # order by 'created_on' descending, then iterate over the result and print out number
   for record in r.get_multiple(order_by=['-created_on']):
       print(record['number'])

