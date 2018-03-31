.. code-block::

	 ______   __  __    ______    __   __    ______    __     __
	/\  == \ /\ \_\ \  /\  ___\  /\ "-.\ \  /\  __ \  /\ \  _ \ \
	\ \  _-/ \ \____ \ \ \___  \ \ \ \-.  \ \ \ \/\ \ \ \ \/ ".\ \
	 \ \_\    \/\_____\ \/\_____\ \ \_\\"\_\ \ \_____\ \ \__/".~\_\
	  \/_/     \/_____/  \/_____/  \/_/ \/_/  \/_____/  \/_/   \/_/
			- a Python library for the ServiceNow REST API
			
.. image:: https://travis-ci.org/rbw0/pysnow.svg?branch=master
    :target: https://travis-ci.org/rbw0/pysnow
.. image:: https://coveralls.io/repos/github/rbw0/pysnow/badge.svg?branch=master
    :target: https://coveralls.io/github/rbw0/pysnow?branch=master
.. image:: https://badge.fury.io/py/pysnow.svg
    :target: https://pypi.python.org/pypi/pysnow
.. image:: https://img.shields.io/badge/License-MIT-green.svg
    :target: https://opensource.org/licenses/MIT


News
----

**Version 0.7 released**

This release comes with a new attachment helper, available in *table-type* `Resources`.
Go `here <http://pysnow.readthedocs.io/en/latest/api/attachment.html>`_ for its API documentation, or check out an `example <http://pysnow.readthedocs.io/en/latest/full_examples/attachments.html>`_.

Also, the ``Response`` interface has been further improved and now allows chaining. Example:

.. code-block:: python
    
    incidents = c.resource(api_path='/table/incident')
    incident = incidents.get(query={'number': 'INC01234'})
    print('uploading last words to incident: {0}'.format(incident['sys_id']))
    incident.upload(file_path='/tmp/last_words.txt')
    incident.update({'description': 'Bye bye'})
    incident.delete()

Additionally, generator / streamed responses are now default off, but can be easily enabled by passing stream=True to ``Resource.get`` for those memory-intensive queries.


Documentation
-------------

The `documentation <http://pysnow.readthedocs.org/>`_ is divided into four sections:

- `General <http://pysnow.readthedocs.io/en/latest/#general>`_ (install, compatibility etc)
- `Library API <http://pysnow.readthedocs.io/en/latest/#api>`_
- `Usage <http://pysnow.readthedocs.io/en/latest/#usage>`_
- `Full examples <http://pysnow.readthedocs.io/en/latest/#examples>`_

Other projects using pysnow
---------------------------
- `flask-snow <https://github.com/rbw0/flask-snow>`_ - Adds ServiceNow support to Flask
- `django-snow <https://github.com/godaddy/django-snow>`_ - ServiceNow Ticket Management App for Django based projects
- `pysnow-shovel <https://github.com/zetup/pysnow-shovel>`_ - Script for easy peasy pushing data into ServiceNow

Author
------
Robert Wikman <rbw@vault13.org>

Contributors
------------
lingfish, jcpunk, AMMullan, amontalban, ryancurrah, jdugan1024, punkrokk


JetBrains
---------
Thank you `Jetbrains <http://www.jetbrains.com>`_ for creating pycharm and providing me with free licenses

