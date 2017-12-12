Request parameters
==================

Request parameters (known as sysparms in ServiceNow) can be set on both the :class:`pysnow.Client` object and on the :class:`pysnow.Resource` object using the :attr:`parameters` property.
Parameters set on **Client** are automatically inherited by **Resource**, but can be overridden.

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

    incident = client.resource(api_path='/table/incident')

    incident.parameters.display_value = True
    incident.parameters.limit = 5  # Limits the max number of records returned for this Resource
    incident.parameters.add_custom({'foo': 'bar'})


