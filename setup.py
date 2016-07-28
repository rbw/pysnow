try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from pysnow import __version__

setup(
    name='pysnow',
    packages=['pysnow'],
    version=__version__,
    description='Python library for the ServiceNow REST API',
    install_requires=['requests'],
    author='Robert Wikman',
    author_email='rbw@vault13.org',
    maintainer='Robert Wikman',
    maintainer_email='rbw@vault13.org',
    url='https://github.com/rbw0/pysnow',
    download_url='https://github.com/rbw0/pysnow/tarball/%s' % __version__,
    keywords=['servicenow', 'rest', 'api', 'http'],
    classifiers=[],
    license='GPLv2',
)