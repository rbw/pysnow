Request parameters
==================

Request parameters (sysparms in ServiceNow) are key-values passed in the query string for GET requests.
Default parameters can be set on both the :class:`pysnow.Client` and the :class:`pysnow.Resource` using the :attr:`parameters` property.
Parameters set on **Client** are automatically inherited by **Resource**, but can of course be overridden.

Please see the API documentation for more info on this.


Client object parameters
------------------------

.. code-block:: python

    client = pysnow.Client(instance=instance,
                           user=username,
                           password=password)

    client.parameters.display_value = False
    client.parameters.exclude_reference_link  = True
    client.parameters.add_custom({'foo': 'bar'})


Resource object parameters
--------------------------

.. code-block:: python

    incident = client.resource(api_path='/custom/api')
    incident.parameters.add_custom({'foo': 'bar'})

