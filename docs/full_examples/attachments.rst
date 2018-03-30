Attaching files
===============

Shows how to upload a file using `Resource.attachments`.

Check out the `Attachment` API documentation for more info!


.. code-block:: python

    import pysnow

    # Create client object
    c = pysnow.Client(instance='myinstance', user='myusername', password='mypassword')

    # Create a resource
    incidents = c.resource(api_path='/table/incident')

    # Uploads file '/tmp/attachment.txt' to the provided incident
    incidents.attachments.upload(sys_id='9b9dd196dbc91f005ab1f58dbf96192b',
                                 file_path='/tmp/attachment.txt')

