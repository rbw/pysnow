Using the QueryBuilder
----------------------

Example showing how the QueryBuilder can be used to construct a query using the Python `datetime` library.

.. code-block:: python

   import pysnow
   from datetime import datetime, timedelta

   # Create client object
   c = pysnow.Client(instance='myinstance', user='myusername', password='mypassword')

   today = datetime.today()
   sixty_days_ago = today - timedelta(days=60)

   # Query incident records with number starting with 'INC0123', created between 60 days ago and today.
   qb = (
       pysnow.QueryBuilder()
       .field('number').starts_with('INC0123')
       .AND()
       .field('sys_created_on').between(sixty_days_ago, today)
   )

   incident = c.resource(api_path='/table/incident')

   response = incident.get(query=qb)

   # Iterate over the matching records and print out number
   for record in response.all():
       print(record['number'])

