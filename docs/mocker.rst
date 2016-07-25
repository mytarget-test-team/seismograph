Mocker
======


Extension for mocking http external resources.


Usage
-----

.. code-block:: python

    from seismograph.ext import mocker


    with mocker.path('/users/<int:id>', json={'name': 'Username'}):
        pass

    @mocker.mock('/user/<int:id>', json={'name': 'Username'})
    def do_something():
        pass


    some_api = mocker.declare_external_resource('/it/can/be/base/path')


    with some_api.path('/users/<int:id>', json={'name': 'Username'}):
        pass

    @some_api.mock('/user/<int:id>', json={'name': 'Username'})
    def do_something(case):
        pass

    # or

    @some_api('/user/<int:id>', json={'name': 'Username'})
    def do_something(case):
        pass


    # You can to run server from program instance

    import seismograph


    class Program(seismograph.Program):

        def setup(self):
            self.ext('mocker').start()

        def teardown(self):
            self.ext('mocker').stop()


    # or from command line interface


!! Need to require mocker where it using


How to run mock server
----------------------

It's doing so


.. code-block:: shell

    seismograph.mocker -m /absolute/path/to/mocks/dir -i 127.0.0.1 -p 5000


or so


.. code-block:: shell

    python -m seismograph.ext.mocker -m /absolute/path/to/mocks/dir -i 127.0.0.1 -p 5000


Mock file
---------

File extension to content type:

* filename.html.mock - text/html
* filename.json.mock - application/json

Mock file example

::

    # This is comment line
    #
    # Order of lines is not important in reality
    # but body has to be in the end of file
    #
    # Meta data for response
    # URL is url rule from flask lib
    #
    GET 200 /hello
    #
    # Headers
    #
    Server: nginx/1.2.1
    #
    # Remind, body has to be in the end
    #

    {
        "hello": "hello world!",
        "data": [
            1,
            2,
            3,
            4,
            5
        ],
        "test": {
            "test": 3.5
        }
    }


Config
------

You should to use **MOCKER_EX** option in config for configure extension.
Config is python dictionary.

+-------------------+----------------------------------------------------------+
| **PATH_TO_MOCKS** | Absolute path to directory where contains mock files     |
+-------------------+----------------------------------------------------------+
| **PORT**          | Port which listen mock server                            |
+-------------------+----------------------------------------------------------+
| **DEBUG**         | Debug mode                                               |
+-------------------+----------------------------------------------------------+
| **HOST**          | Host for start server. Should set ip address.            |
+-------------------+----------------------------------------------------------+
| **SERVER_TYPE**   | Server type cen be in ("json_api", "simple")             |
+-------------------+----------------------------------------------------------+
| **BLOCK_TIMEOUT** | Timeout for release mocked url                           |
+-------------------+----------------------------------------------------------+
