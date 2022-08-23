Installation
------------

The fritzconnection package is available on `PyPi <https://pypi.org/project/fritzconnection/>`_ and installable by `pip <https://pypi.org/project/pip/>`_:  ::

    $ pip install fritzconnection

To enable the creation of :ref:`QR-codes for wifi login <get_wifi_qr_code_example>`, install fritzconnection with the `qr`-option: ::

    $ pip install fritzconnection[qr]

.. versionadded:: 1.9.0

This will install an additional dependency `segno <https://pypi.org/project/segno/>`_. In case you've missed this, segno can get installed any time later: ::

    $ pip install segno

It is good practice and highly recommended to do the installation in a virtual environment – either by means of `venv <https://docs.python.org/3.7/library/venv.html?highlight=venv#module-venv>`_ or `conda <https://docs.conda.io/en/latest/index.html>`_ (comes with `miniconda <https://docs.conda.io/en/latest/miniconda.html>`_ or `anaconda <https://www.anaconda.com/distribution/>`_).

fritzconnection requires Python >= 3.6
