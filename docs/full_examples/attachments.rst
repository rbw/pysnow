Attaching files
===============

Shows how to upload a file using `Resource.attachments`.

Check out the `Attachment` API documentation for more info.

**Using Response.upload() convenience method**

.. code-block:: python

    # Create a resource
    incidents = client.resource(api_path='/table/incident')
    
    # Fetch and attach
    incident = incidents.get(query={'number': 'INC01234'})
    incident.upload(file_path='/tmp/attachment.txt')

**Using Resource.attachments.upload()**

.. code-block:: python

    # Create a resource
    incidents = client.resource(api_path='/table/incident')

    # Uploads file '/tmp/attachment.txt' to the provided incident
    incidents.attachments.upload(sys_id='9b9dd196dbc91f005ab1f58dbf96192b',
                                 file_path='/tmp/attachment.txt')
