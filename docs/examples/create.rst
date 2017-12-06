Creating a new record
---------------------

See the :meth:`pysnow.Request.insert` documentation for more details.

.. code-block:: python

   import pysnow

   # Create client object
   s = pysnow.Client(instance='myinstance', user='myusername', password='mypassword')

   # Create new record and catch possible server response exceptions
   try:
       res = s.insert(table='incident', payload={'field1': 'value1', 'field2': 'value2'})

       # print the result
       print(res)
   except pysnow.UnexpectedResponse as e:
       print("%s, details: %s" % (e.error_summary, e.error_details))

