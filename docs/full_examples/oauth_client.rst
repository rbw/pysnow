Using the OAuthClient
=====================

Example showing how tokens can be obtained, stored and refreshed using the OAuthClient.


.. code-block:: python

    import pysnow
    import session

    # Takes care of refreshing the token storage
    def updater(new_token):
        print("OAuth token refreshed!")
        session['token'] = new_token

    # Create the OAuthClient with the ServiceNow provided `client_id` and `client_secret`, and a `token_updater`
    # function which takes care of refreshing local token storage.
    s = pysnow.OAuthClient(client_id='<client_id_from_servicenow>', client_secret='<client_secret_from_servicenow>',
                           token_updater=updater, instance='<instance_name>')

    if not session['token']:
        # No previous token exists. Generate new.
        session['token'] = s.generate_token('<username>', '<password>')

    # Set the access / refresh tokens
    s.set_token(session['token'])

    # We should now be good to go. Let's define a `Resource` for the incident API.
    incident_resource = resource(api_path='/table/incident')

    # Fetch incident with number INC012345, or None
    record = incident_resource.get(query={'number': 'INC012345'}).one_or_none()

    if not record:
        print("No such incident")
    else:
        print(record)


