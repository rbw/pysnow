# -*- coding: utf-8 -*-

import os


class Attachment(object):
    def __init__(self, resource, api_name, resource_name):
        self.resource = resource
        self.api_name = api_name
        self.resource_name = resource_name

    def get(self, sys_id=None, limit=10):
        if sys_id:
            return self.resource.get(query={'sys_id': sys_id}).one()

        return self.resource.get(query={'table_name': self.resource_name}, limit=limit).all()

    def upload(self, sys_id, file_path, name=None, multipart=False):
        resource = self.resource

        if name is None:
            name = os.path.basename(file_path)

        resource.parameters.add_custom({
            'table_name': self.resource_name,
            'table_sys_id': sys_id,
            'file_name': name
        })

        # Set the payload
        data = open(file_path, 'rb').read()

        headers = {}

        if multipart:
            headers["Content-Type"] = "multipart/form-data"
            path_append = '/upload'
        else:
            headers["Content-Type"] = "text/plain"
            path_append = '/file'

        return resource.request(method='POST', data=data, headers=headers, path_append=path_append)

    def delete(self, sys_id):
        self.resource.delete(query={'sys_id': sys_id})

