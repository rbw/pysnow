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

Version 0.6 has been released :tada:

This release comes with changes to some fundamental parts of the library. The old code has been kept, and should work seamlessly but raises a deprecation warning upon usage.

In short, the new version introduces the concept of **resources**, which enables a natural interaction with any ServiceNow API and changes how requests are performed, while
providing an improved response interface.

Also, the documentation has been reworked and covers only version 0.6 and later. If you're not interested in switching, that's OK, `The old documentation <http://pysnow.readthedocs.io/en/0.5.2>`_ is still available.



Documentation
-------------

The `documentation <http://pysnow.readthedocs.org/>`_ is divided into four sections:

 - `General <http://pysnow.readthedocs.io/en/latest/#general>`_ (install, compatibility etc)
 - `Library API <http://pysnow.readthedocs.io/en/latest/#api>`_
 - `Usage <http://pysnow.readthedocs.io/en/latest/#usage>`_
 - `Full examples <http://pysnow.readthedocs.io/en/latest/#examples>`_

Other projects using pysnow
---------------------------
- `pysnow-flask <https://github.com/rbw0/pysnow-flask>`_ - Makes interfacing with ServiceNow in Flask an amazing experience
- `pysnow-shovel <https://github.com/zetup/pysnow-shovel>`_ - Script for easy peasy pushing data into ServiceNow

Author
------
Robert Wikman <rbw@vault13.org>

Contributors
------------
lingfish, jcpunk, AMMullan, amontalban, ryancurrah, jdugan1024, punkrokk


JetBrains
---------
Thank you Jetbrains (www.jetbrains.com) for supporting with IDE licenses!
