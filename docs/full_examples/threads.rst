Using threaded queries
======================

This is an example of multiple threads doing simple fetches.


.. note::
    This example uses `concurrent.futures` and expects you to be familiar with :meth:`pysnow.Resource.get`.


.. code-block:: python

    import concurrent.futures
    import pysnow

    def just_print(client, query):
        # Run the query
        response = client.get(query=query)

        # Iterate over the result and print out `sys_id` and `state` of the matching records.
        for record in response.all():
            print(record['sys_id'], record['state'])

    # Create client object
    c = pysnow.Client(instance='myinstance', user='myusername', password='mypassword')

    # list of simple items to query
    queries = ({'api': '/table/incident', 'q': {'state': 1}}, {'api': '/table/incident', 'q': {'state': 3}})

    # build taskqueue
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as taskpool:
        for query in queries:
            connection = c.resource(api_path=query['api'])
            taskpool.submit(just_print, connection, query['q'])
