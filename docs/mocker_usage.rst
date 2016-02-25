Usage as extension for runnable
===============================

Start and stop server
---------------------

You can start server from runnable object, but need to remember that extension has
**single instance** in program context. The best way is start and stop server on program object.


.. code-block:: python

    import seismograph


    program = seismograph.Program()


    @program.add_setup
    def start_mock_server():
        mock_server = program.ext('mock_server')
        mock_server.start()

    @program.add_teardown
    def stop_mock_server():
        mock_server = program.ext('mock_server')
        mock_server.stop()



Mock server instance has self client


.. code-block:: python

    resp = mock_server.client.get('/some/path/')
    # this is response object from requests lib


Create mock object
------------------

You can to create mock and add it to server. Mock can be added to running server.


.. code-block:: python

    from seismograph.ext.mock_server import JsonMock


     mock = JsonMock(
        'example_mock',
        '/hello',
        {'result': 'created'},
        http_method='POST',
        status_code=201,
        headers={
            'Server': 'nginx/1.2.1',
        },
    )

    mock_server.add_mock(mock)


Also, you can rewrite mock on the fly


.. code-block:: python

    with mock_server.mock(mock) as old_mock:
        # do something


Old mock will restored after exit from with block.
If url rules is equals and http methods is equals then mocks is equals.
If old mock is not found by the criterias then None be returned.
