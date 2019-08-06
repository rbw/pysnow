# -*- coding: utf-8 -*-

import io
import ast

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_version():
    """ Parses the pysnow package __init__ file and fetches the version attribute from the syntax tree
    :return: pysnow version
    """
    with io.open('pysnow/__init__.py') as input_file:
        for line in input_file:
            if line.startswith('__version__'):
                return ast.parse(line).body[0].value.s


with io.open('README.rst') as readme:
    setup(
        name='pysnow',
        packages=['pysnow'],
        version=get_version(),
        description='ServiceNow HTTP client library',
        long_description=readme.read(),
        install_requires=[
            'requests',
            'oauthlib',
            'python-magic',
            'requests_oauthlib',
            'httpretty',
            'six',
            'ijson',
            'pytz'
        ],
        author='Robert Wikman',
        author_email='rbw@vault13.org',
        maintainer='Robert Wikman',
        maintainer_email='rbw@vault13.org',
        url='https://github.com/rbw0/pysnow',
        download_url='https://github.com/rbw0/pysnow/tarball/%s' % get_version(),
        keywords=['servicenow', 'rest', 'api', 'http', 'client'],
        platforms='any',
        classifiers=[
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
            'Topic :: Software Development :: Libraries :: Python Modules'
        ],
        license='MIT',
    )
