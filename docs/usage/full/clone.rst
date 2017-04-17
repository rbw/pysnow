Cloning
-------

See the :meth:`pysnow.Request.clone` documentation for more details.


.. code-block:: python

    import pysnow

    # Create client object
    s = pysnow.Client(instance='myinstance', user='myusername', password='mypassword')

    try:
        # Query for record with number 'INC012345'
        r = s.query('incident', query={'number': 'INC012345'})

        clones = []

        # Create 5 clones
        for _ in range(5):
            c = r.clone(reset_fields=['sys_id', 'number', 'opened_at'])
            clones.append(c)

        # Print out some info
        print("Created clones: %s" % [clone['number'] for clone in clones])
    except pysnow.UnexpectedResponse as e:
        print("%s, details: %s" % (e.error_summary, e.error_details))

