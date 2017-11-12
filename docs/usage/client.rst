Connecting
==========

This shows some examples of how to connect with pysnow using either username and password or a custom session object

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


Setting request parameters
--------------------------
The `request_params` dict argument can be used to set request parameters. This example returns names from fields with linked tables, instead of the standard URL for ServiceNow dot walking.
Check out the `Table API documentation <http://wiki.servicenow.com/index.php?title=Table_API#gsc.tab=0>`_ for more info.

.. code-block:: python
    
    import pysnow

    # Create new client with SN request parameters
    sn = pysnow.Client(instance=instance,
                       user=username,
                       password=password,
                       request_params={'sysparm_display_value': 'true'})

Using the OAuthClient
---------------------

Pysnow provides the :meth:`pysnow.OAuthClient` to simplify the process of obtaining initial tokens, refreshing tokens and keeping tokens in sync with your storage.

Should the :meth:`pysnow.OAuthClient` not be sufficient for your requirements some reason, you can always create a custom `Requests` compatible OAuth session and pass along to :meth:`pysnow.Client`

Enabling OAuth in ServiceNow is fairly simple but beyond the scope of this
document. Details on how to do this can be found in the `official ServiceNow documentation <https://docs.servicenow.com/bundle/istanbul-servicenow-platform/page/integrate/inbound-rest/task/t_EnableOAuthWithREST.html>`_.


Initial tokens
^^^^^^^^^^^^^^

In order to use the :meth:`pysnow.OAuthClient` you first need to obtain a new token from ServiceNow.
Creating a new token bound to a certain user is easy, simply call :meth:`pysnow.OAuthClient.generate_token()` and keep it in your storage (e.g. in session or database)

.. code-block:: python

    import pysnow
    import session

    s = pysnow.OAuthClient(client_id='<client_id_from_servicenow>', client_secret='<client_secret_from_servicenow>', instance='<instance_name>')

    if not session['token']:
        # No previous token exists. Generate new.
        session['token'] = s.generate_token('<username>', '<password>')



Using the tokens
^^^^^^^^^^^^^^^^

Once an initial token has been obtained it will be refreshed automatically upon usage, provided its refresh_token hasn't expired.

After a token has been refreshed, the provided :attr:`pysnow.OAuthClient.token_updater` function will be called with the refreshed token as first argument.

.. code-block:: python

    import pysnow
    import session

    def updater(new_token):
        print("OAuth token refreshed!")
        session['token'] = new_token

    s = pysnow.OAuthClient(client_id='<client_id_from_servicenow>', client_secret='<client_secret_from_servicenow>', token_updater=updater, instance='<instance_name>')
    s.set_token(session['token'])

    response = s.query(table='incident', query={'number': 'INC012345'}).get_one()

    print(response['number'])


