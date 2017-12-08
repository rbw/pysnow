Resources
=========

The :class:`pysnow.Resource`, given an API path, offers an interface to all CRUD functionality available in the ServiceNow REST API.

The idea with Resources is to provide a logical, nameable and reusable container-like object.

Example of a resource using the **incident table API** with a doubled **chunk_size** of 8192 bytes and **sysparm_display_value** set to True.

.. code-block:: python

    incident = client.resource(api_path='/table/incident', chunk_size=8192)
    incident.parameters.display_value = True

