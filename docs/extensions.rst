Extensions
==========


.. toctree::
    :maxdepth: 2

    selenium
    alchemy
    mock_server


Extensions is tools for test development. You can to require their.


.. code-block:: python

    import seismograph


    suite = seismograph.Suite(__name__, require=['selenium', 'mock_server'])


    selenium = suite.ext('selenium')
    mock_server = suite.ext('mock_server')


or for case only


.. code-block:: python


    @suite.register(require=['selenium', 'mock_server'])
    def function_test(case):
        selenium = case.ext('selenium')
        mock_server = case.ext('mock_server')
        # do something


Extensions is allow from program instance.


.. code-block:: python

    program = seismograph.Program()
    selenium = program.ext('selenium')
    mock_server = program.ext('mock_server')
