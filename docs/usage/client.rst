The Client
==========

The **Client** comes in two forms:
 - The regular :class:`pysnow.Client` - use if you're authenticating with password credentials or wish to pass an already created session object.
 - The :class:`pysnow.OAuthClient` - use if you wish to do OAuth with an OAuth2 enabled ServiceNow instance.

Using pysnow.Client
-------------------

This shows some examples of how to create the :class:`pysnow.Client` using username and password or a custom session object

See the :class:`pysnow.Client` documentation for details.


With username and password
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    s = pysnow.Client(instance='myinstance',
                      user='myusername',
                      password='mypassword')

With a custom session object
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can pass a custom session object to :class:`pysnow.Client`.
In this example password credentials are used, but with SSL verification disabled.

.. code-block:: python

    s = requests.Session()
    s.verify = False
    s.auth = requests.auth.HTTPBasicAuth('myusername', 'mypassword')

    sn = pysnow.Client(instance='myinstance', session=s)


Using pysnow.OAuthClient
------------------------

Pysnow provides the :class:`pysnow.OAuthClient` to simplify the process of obtaining initial tokens, refreshing tokens and keeping tokens in sync with your storage.

Should the :class:`pysnow.OAuthClient` not be sufficient for your requirements some reason, you can always create a custom `Requests` compatible OAuth session and pass along to :meth:`pysnow.Client`

Enabling OAuth in ServiceNow is fairly simple but beyond the scope of this
document. Details on how to do this can be found in the `official ServiceNow documentation <https://docs.servicenow.com/bundle/istanbul-servicenow-platform/page/integrate/inbound-rest/task/t_EnableOAuthWithREST.html>`_.


Getting initial tokens
^^^^^^^^^^^^^^^^^^^^^^

In order to use the :class:`pysnow.OAuthClient` you first need to obtain a new token from ServiceNow.
Creating a new token bound to a certain user is easy. Simply call :meth:`pysnow.OAuthClient.generate_token()` and keep it in your storage (e.g. in session or database)

.. code-block:: python

    s = pysnow.OAuthClient(client_id='<client_id_from_servicenow>', client_secret='<client_secret_from_servicenow>', instance='<instance_name>')

    if not session['token']:
        # No previous token exists. Generate new.
        session['token'] = s.generate_token('<username>', '<password>')



Using tokens
^^^^^^^^^^^^

Once an initial token has been obtained it will be refreshed automatically upon usage, provided its refresh_token hasn't expired.

After a token has been refreshed, the provided :meth:`token_updater` function will be called with the refreshed token as first argument.

.. code-block:: python

    def updater(new_token):
        print("OAuth token refreshed!")
        session['token'] = new_token

    s = pysnow.OAuthClient(client_id='<client_id_from_servicenow>', client_secret='<client_secret_from_servicenow>', token_updater=updater, instance='<instance_name>')
    s.set_token(session['token'])

