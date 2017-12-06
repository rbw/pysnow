Getting a single record with the OAuthClient
--------------------------------------------

See the :meth:`pysnow.OAuthClient` documentation for more details.


.. code-block:: python

    import pysnow
    import session

    def updater(new_token):
        print("OAuth token refreshed!")
        session['token'] = new_token

    s = pysnow.OAuthClient(client_id='<client_id_from_servicenow>', client_secret='<client_secret_from_servicenow>', token_updater=updater, instance='<instance_name>')

    if not session['token']:
        # No previous token exists. Generate new.
        session['token'] = s.generate_token('<username>', '<password>')

    s.set_token(session['token'])

    response = s.query(table='incident', query={'number': 'INC012345'}).get_one()

    print(response['number'])


