Resources
=========

``pysnow.Resource`` provides an interface to easily and efficiently create, read, update and delete records in ServiceNow. Additionally, it's also equipped with helpers for common operations, such as attaching files.

Check out the `Resource` `API documentation <http://pysnow.readthedocs.io/en/latest/api/resource.html>`_ for more info.


.. code-block:: python

    incident = client.resource(api_path='/table/incident')
    incident.parameters.display_value = True

    record = incident.get(query={'number': 'INC012345'}).one()
    
    sys_id = record['sys_id']
    incident.attachments.upload(sys_id, file_path='/tmp/document.txt)
    
    updated = incident.update(query={'sys_id': sys_id},
                              payload={
                                  'short_description': 'Uh-uh',
                                  'description': 'I fear I might be getting deleted.'
                              })
   
    incident.delete(query={'sys_id': sys_id})

