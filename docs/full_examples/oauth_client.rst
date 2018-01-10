Using the OAuthClient
=====================

Example showing how tokens can be obtained, stored and refreshed using the OAuthClient.

In this example a basic dictionary is used as store, which offers no persistence, meaning that `OAuthClient.generate_token` will be called every time this code executes, which introduces an overhead.
The `store` here could be a database table, file, session or whatever you want.

.. code-block:: python

    import pysnow

    store = {'token': None}

    # Takes care of refreshing the token storage if needed
    def updater(new_token):
        print("OAuth token refreshed!")
        store['token'] = new_token

    # Create the OAuthClient with the ServiceNow provided `client_id` and `client_secret`, and a `token_updater`
    # function which takes care of refreshing local token storage.
    s = pysnow.OAuthClient(client_id='<client_id_from_servicenow>', client_secret='<client_secret_from_servicenow>',
                           token_updater=updater, instance='<instance_name>')

    if not store['token']:
        # No previous token exists. Generate new.
        store['token'] = s.generate_token('<username>', '<password>')

    # Set the access / refresh tokens
    s.set_token(store['token'])

    # We should now be good to go. Let's define a `Resource` for the incident API.
    incident_resource = s.resource(api_path='/table/incident')

    # Fetch the first record in the response
    record = incident_resource.get(query={}).first()

    # Print it
    print(record)

