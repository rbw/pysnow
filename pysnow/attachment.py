# -*- coding: utf-8 -*-

import os
from pysnow.exceptions import InvalidUsage


class Attachment(object):
    """API for managing attachments.

    :param resource: API resource to manage attachments for
    :param table_name: Name of the table to use in the attachment API
    """

    def __init__(self, resource, table_name):
        self.resource = resource
        self.table_name = table_name

    def get(self, sys_id=None, limit=100):
        """Returns a list of records,

        :param sys_id: record sys_id to list attachments for
        :param limit: override the default limit of 100
        :return: list of incident objects
        """

        if sys_id:
            return self.resource.get(query={'table_sys_id': sys_id, 'table_name': self.resource_name}).all()

        return self.resource.get(query={'table_name': self.resource_name}, limit=limit).all()

    def upload(self, sys_id, file_path, name=None, multipart=False):
        """Attaches a new file to the specified record

        :param sys_id: the sys_id of the record to attach the file to
        :param file_path: local absolute path of the file to upload
        :param name: custom name for the uploaded file (instead of basename)
        :param multipart: whether or not to use multipart
        :return: the inserted record
        """

        if not isinstance(multipart, bool):
            raise InvalidUsage('Multipart must be of type bool')

        resource = self.resource

        if name is None:
            name = os.path.basename(file_path)

        resource.parameters.add_custom({
            'table_name': self.resource_name,
            'table_sys_id': sys_id,
            'file_name': name
        })

        data = open(file_path, 'rb').read()
        headers = {}

        if multipart:
            headers["Content-Type"] = "multipart/form-data"
            path_append = '/upload'
        else:
            headers["Content-Type"] = "text/plain"
            path_append = '/file'

        return resource.request(method='POST', data=data, headers=headers, path_append=path_append).one()

    def delete(self, sys_id):
        """Deletes the specified record

        :param sys_id: attachment sys_id
        :return: delete result
        """

        self.resource.delete(query={'sys_id': sys_id})

