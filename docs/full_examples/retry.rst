Session with auto-retry
=======================

You might run into issues if you're creating too many requests against the ServiceNow API.
Fortunately, the `requests` library enables users to create their own transport adapter with a retry mechanism from the `urllib3` library.

You can read more about transport adapters and the retry mechanism here:
 - http://docs.python-requests.org/en/master/user/advanced/#transport-adapters
 - https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html#module-urllib3.util.retry


This example shows how to automatically retry on an error for about 2 seconds and then fall back to the default error handling.

.. code-block:: python

    import requests
    import pysnow

    from requests.adapters import HTTPAdapter
    from requests.packages.urllib3.util.retry import Retry

    s = requests.Session()
    s.auth = requests.auth.HTTPBasicAuth('<username>', '<password>')

    # set auto retry for about 2 seconds on some common errors
    adapter = HTTPAdapter(
        max_retries=Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=(401, 408, 429, 431, 500, 502, 503, 504, 511)
        )
    )

    s.mount('https://', adapter)

    sn = pysnow.Client(instance='<instance>', session=s)
