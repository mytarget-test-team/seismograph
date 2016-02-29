Mocker
======

.. toctree::
    :maxdepth: 2

   mocker_usage
   mocker_mock_file
   mocker_config


Mocker is extension based on flask lib. It can to work separately of test program as UWSGI server.


It's doing so


.. code-block:: shell

    seismograph.mocker -m /absolute/path/to/mocks/dir -i 127.0.0.1 -p 5000


or so


.. code-block:: shell

    python -m seismograph.ext.mocker -m /absolute/path/to/mocks/dir -i 127.0.0.1 -p 5000


We use mocker for mocking rest json api and we have made it for that.
But you can to use it how you wish with help base classes.
