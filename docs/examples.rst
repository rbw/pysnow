Usage examples
==============

Import and instantiation
------------------------

.. code-block:: python

    import pysnow

    # Create client object
    s = pysnow.Client(instance='myinstance',
                      user='myusername',
                      password='mypassword',
                      raise_on_empty=True)


Getting a single record
------------------------

Here we'll utilize `get_one()`, a convenience function for getting a single record without having to use a generator.

.. code-block:: python

    request = s.query(table='incident', query={'number': 'INC01234'})

    # Fetch one record and filter out everything but 'number' and 'sys_id' from the results
    result = request.get_one(fields=['number', 'sys_id'])
    print(result['number'])


Getting all records
-------------------

`get_all()` returns a generator response (iterable) , also, this method chains linked responses

.. code-block:: python

    request = s.query(table='incident', query={'state': 2})

    # Fetch all records without using a field filter,
    # then iterate over the results and print out sys_ids
    while record in request.get_all():
        print(record['sys_id'])


Updating a record
-----------------

.. code-block:: python

    request = s.query(table='incident', query={'number': 'INC01234'})

    # Update the record
    result = request.update({'description': 'test'})

    print("Record '%s' was successfully updated" % result)


Creating a new record
---------------------

.. code-block:: python

    # Create a new record
    result = s.insert(table='incident', payload={'field1': 'value1', 'field2': 'value2'})

    # Print out the number of the created record
    print(result['number'])


Deleting a record
---------------------

.. code-block:: python

    # Query the incident table by number
    request = s.query(table='incident', query={'number': 'INC01234'})

    # Delete the record
    result = request.delete()

    if result['success'] == True:
        print("Record deleted")



Catching server response errors
-------------------------------

`UnexpectedResponse` can be used with all CRUD methods and contains important information of what went wrong when interfacing with the API

.. code-block:: python

   # Create new record and catch possible server response exceptions
   try:
       s.insert(table='incident', payload={'field1': 'value1', 'field2': 'value2'})
   except pysnow.UnexpectedResponse as e:
       print("%s, details: %s" % (e.error_summary, e.error_details))


Using OAuth
-----------

You will need to enable OAuth inside ServiceNow which is beyond the scope of this
document. You can find the details in the `ServiceNow documentation <https://docs.servicenow.com/bundle/istanbul-servicenow-platform/page/integrate/inbound-rest/task/t_EnableOAuthWithREST.html>`_.

You will need to install
`Requests-OAuthlib <https://requests-oauthlib.readthedocs.io/en/latest/>`_ in order to
follow this example.

Initial tokens
^^^^^^^^^^^^^^

You will need an access_token and a refresh_token. The ServiceNow OAuth documentation
provides one way to get the initial tokens but here is a simple example of obtaining
them using Python.

You will need a username and password to obtain the initial access and refresh tokens.
Once you have these you will not need the username and password again until the
refresh token expires. This expiration is controlled in your ServiceNow setup.

.. code-block:: python


   import json
   from oauthlib.oauth2 import LegacyApplicationClient
   from requests_oauthlib import OAuth2Session

   client_id = 'CLIENT_ID'         # from the ServiceNow setup
   client_secret = 'CLIENT_SECRET' # also from ServiceNow setup
   username = 'USER_NAME'          # a valid ServiceNow user
   password = 'USER_PASSWORD'      # a valid ServiceNow password
   instance = 'SNOW_INSTANCE'      # the name of your ServiceNow instance

   oauth_url = 'https://{}.service-now.com/oauth_token.do'.format(instance)

   oauth = OAuth2Session(client=LegacyApplicationClient(client_id=client_id))
   token = oauth.fetch_token(token_url=oauth_url,
                             username=username,
                             password=password,
                             client_id=client_id,
                             client_secret=client_secret)

   print json.dumps(token, indent=4)

Save the contents of the ``token`` dictionary you get back. You'll need that that in
the following steps.

Using the tokens
^^^^^^^^^^^^^^^^

You will need the token dictionary created in the above step. This example sets up
autorefresh of the tokens. This will work for as long as the refresh_token is valid.

.. code-block:: python

   import pysnow
   from oauthlib.oauth2 import LegacyApplicationClient
   from requests_oauthlib import OAuth2Session

   client_id = 'CLIENT_ID'         # from the ServiceNow setup
   client_secret = 'CLIENT_SECRET' # also from ServiceNow setup
   username = 'USER_NAME'          # a valid ServiceNow user

   oauth_url = 'https://{}.service-now.com/oauth_token.do'.format(instance)

   token = ... # token dict from the previous step

   refresh_kwargs = { "client_id": client_id, "client_secret": client_secret }

   def token_updater(new_token):
       # callback to update/store the new tokens
       pass

   oauth_session = OAuth2Session(client=LegacyApplicationClient(client_id=client_id),
                                 token=token,
                                 auto_refresh_url=oauth_url,
                                 auto_refresh_kwargs=refresh_kwargs,
                                 token_updater=token_updater)

   s = pysnow.client(instance=instance, session=oauth_session, raise_on_empty=True)
