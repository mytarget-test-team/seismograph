Program
=======

This is only one entry point to test program.


Simple example
--------------


.. code-block:: python

    import seismograph


    suite = seismograph.Suite(__name__)


    @suite.register
    def function_test(case):
        case.assertion.equal(1, 1)


    if __name__ == '__main__':
        program = seismograph.Program(exit=False)
        program.register_suite(suite)

        program()



How to use setup and teardown callbacks
---------------------------------------

Program class have setup teardown callbacks also like suite and case.
You can use their so...

.. code-block:: python

    import seismograph


    class ExampleProgram(seismograph.Program):

        def setup(self):
            # do something

        def teardown(self):
            # do something


    suite = seismograph.Suite(__name__)


    @suite.register
    def function_test(case):
        # do something


    if __name__ == '__main__':
        program = ExampleProgram(exit=False)

        @program.add_setup
        def setup():
            # do something


        @program.teardown
        def teardown():
            # do something


        program.register_suite(suite)

        program()


How to use extensions
---------------------


.. code-block:: python

    import seismograph


    class ExampleProgram(seismograph.Program):

        def setup(self):
            self.ext('mock_server').start()

        def teardown(self):
            self.ext('mock_server').stop()


    suite = seismograph.Suite(__name__)


    @suite.register
    def function_test(case):
        # do something


    if __name__ == '__main__':
        program = ExampleProgram(exit=False)
        program.register_suite(suite)

        program()
