Getting multiple records
------------------------

See the :meth:`pysnow.Request.get_multiple` documentation for more details.

.. code-block:: python

   import pysnow

   # Create client object
   s = pysnow.Client(instance='myinstance', user='myusername', password='mypassword')

   # Get all incidents
   r = s.query('incident', query={})

   # Set the limit of records returned from server to 20, then iterate over the result and print out number
   for record in r.get_multiple(limit=20):
       print(record['number'])

