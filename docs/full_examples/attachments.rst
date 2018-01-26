Attaching a file
================

Shows how to upload a binary file specified in the request body, providing information about the attachment using the `pysnow.ParamsBuilder` API exposed in `Resource.parameters`.

.. note::
    The attachment API (/api/now/attachment/file), as with all ServiceNow APIs that doesn't conform with the standard REST principles, requires you to use :meth:`Client.resource.request` and create a custom request.


.. code-block:: python

    import pysnow

    # Create client object
    c = pysnow.Client(instance='myinstance', user='myusername', password='mypassword')

    # Create a resource
    attachment = c.resource(api_path='/attachment/file')

    # Provide the required information about the attachment
    attachment.parameters.add_custom({
        'table_name': 'incident',
        'table_sys_id': '<incident_sys_id>',
        'file_name': 'attachment.txt'
    })

    # Set the payload
    data = open('/tmp/attachment.txt', 'rb').read()

    # Override the content-type header
    headers = { "Content-Type": "text/plain" }

    # Fire off the request
    attachment.request(method='POST', data=data, headers=headers)

