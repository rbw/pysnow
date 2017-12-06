Resources
=========

The :class:`pysnow.Resource`, given an API path, offers an interface to all CRUD functionality available in the ServiceNow REST API.

The idea with Resources is to provide a logical, nameable and reusable container-like object.

Example of a resource using the **incident table API**, with **sysparm_display_value** set to True and **raise_on_empty** False.

.. code-block:: python

    incident = client.resource(api_path='/table/incident')
    incident.parameters.display_value = True
    incident.raise_on_empty = False

