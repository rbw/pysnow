Connecting
==========

This shows some examples of how to connect with pysnow using either username and password or OAuth.

See the :meth:`pysnow.Client` documentation for details.

Using username and password
---------------------------

.. code-block:: python

    import pysnow

    # Create client object
    s = pysnow.Client(instance='myinstance',
                      user='myusername',
                      password='mypassword')


Using a custom session object
-----------------------------

You can pass a custom session object to `Client`.
In this example regular user / pass authentication is used, but with SSL verification disabled.

.. code-block:: python

    import pysnow
    import requests

    s = requests.Session()
    s.verify = False
    s.auth = requests.auth.HTTPBasicAuth('myusername', 'mypassword')

    # Create client object
    sn = pysnow.Client(instance='myinstance', session=s)


Setting Query Request Parameters
------------------------
You can use a default_payload dictionary to set query parameters. This example returns names from fields with linked tables, instead of the standard URL for ServiceNow dot walking. 

.. code-block:: python
    
    import pysnow

    # create your client object with sn request parameters
    sn_client = pysnow.Client(instance=instance,
                                       user=username,
                                       password=password,
                                       default_payload={"sysparm_display_value": "true"})
   
or with a custom session object

.. code-block:: python

    import psynow
    import requests
    s = requests.Session()
    s.verify = False
    s.auth = requests.auth.HTTPBasicAuth('myusername', 'mypassword')

    sn = pysnow.Client(instance='myinstance', 
                       session=s,
                       default_payload={'sysparm_display_value': True})
                       

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

   s = pysnow.client(instance=instance, session=oauth_session)
