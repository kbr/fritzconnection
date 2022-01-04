Installation
------------

The fritzconnection package is available on `PyPi <https://pypi.org/>`_ and installable by `pip <https://pypi.org/project/pip/>`_  ::

    $ pip install fritzconnection

This installation will also install the required package `requests <http://docs.python-requests.org/>`_ and the corresponding sub-dependencies.

As an optional feature fritzconnection can create QR-codes for wifi login data (:ref:`get_wifi_qr_code_example`). This requires the `segno <https://pypi.org/project/segno/>`_ package as an extra dependency. To add this package right at the beginning, install fritzconnection as ::

    $ pip install fritzconnection[qr]

.. versionadded:: 1.9.0

If you missed this, `segno` can get installed any time later with ::

    $ pip install segno

It is recommended and good practice, to do the installation in a virtual environment – either by means of `venv <https://docs.python.org/3.7/library/venv.html?highlight=venv#module-venv>`_ or `conda <https://docs.conda.io/en/latest/index.html>`_ (comes with `miniconda <https://docs.conda.io/en/latest/miniconda.html>`_ or `anaconda <https://www.anaconda.com/distribution/>`_).

fritzconnection runs with recent Python 3 versions, that are not EOL (end of life). (Older Python versions may work but are neither tested nor supported.)
