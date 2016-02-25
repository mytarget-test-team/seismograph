Mock server
===========

.. toctree::
    :maxdepth: 2

   mocker_usage
   mocker_mock_file
   mocker_config


Mock server extension based on flask lib. It can to work separately of test program as UWSGI server.


It's doing so


.. code-block:: shell

    seismograph.mock_server -m /absolute/path/to/mocks/dir -i 127.0.0.1 -p 5000


or so


.. code-block:: shell

    python -m seismograph.ext.mock_server -m /absolute/path/to/mocks/dir -i 127.0.0.1 -p 5000


We use mock server for mocking rest json api and we make extension for that.
But you can use him how you wish with help base classes.
