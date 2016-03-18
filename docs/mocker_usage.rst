Usage as extension for runnable
===============================

Start and stop server
---------------------

You can start server from runnable object, but need to remember what extension has
**single instance** in program context. The best way is start and stop server from program instance.


.. code-block:: python

    import seismograph


    program = seismograph.Program()


    @program.add_setup
    def start_mocker():
        mocker = program.ext('mocker')
        mocker.start()

    @program.add_teardown
    def stop_mocker():
        mocker = program.ext('mocker')
        mocker.stop()



Mocker instance has self client


.. code-block:: python

    resp = mocker.client.get('/some/path/')
    # this is response object from requests lib


Create mock object
------------------

You can to create mock and add it to server. Mock can be added to running server.


.. code-block:: python

    from seismograph.ext.mocker import JsonMock


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

    mocker.add_mock(mock)


Also, you can to rewrite mock on the fly


.. code-block:: python

    with mocker.mock(mock) as old_mock:
        # do something


Old mock will be restored after exit from with block.
If url rules is equals and http methods is equals then mocks is equals.
If old mock is not found by the criterias then None be returned.
