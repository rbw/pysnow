Sorting
=======

Sorting can be done over multiple fields in ascending or descending order.

Example showing how sorting can be dynamically created from a comma-separated string of fields. 


.. code-block:: python

  query = pysnow.QueryBuilder()
  fields = '-created_at,priority'.split(',')

  query.field('priority').equals(['3', '4']).AND()

  for (idx, field) in enumerate(fields):
      if field[:1] == '-':
          query.field(field[1:]).order_descending()
      else:
          query.field(field).order_ascending()

      if idx != len(fields) - 1:
          query.AND()

  print(str(query))  # priorityIN3,4^ORDERBYnumber^ORDERBYDESCdescription


