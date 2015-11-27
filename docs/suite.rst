Suite
=====

Suite is test case collection with own context for run.


Simple usage
------------

Suite can be called by namespaces, however, how you wish...


.. code-block:: python

    import seismograph


    suite = seismograph.Suite(__name__)


How to register test case
-------------------------

Case should be related to suite if you want to run him.
This is doing so...


.. code-block:: python

    import seismograph


    suite = seismograph.Suite(__name__)


    @suite.register
    def function_test(case):
        case.log('Hello')


    if __name__ == '__main__':
        seismograph.main()


How to use setup and teardown callbacks
---------------------------------------

Suite can have many setup and teardown callbacks.
Let look at realization...


.. code-block:: python

    import seismograph


    class ExampleSuite(seismograph.Suite):

        def setup(self):
            print('Setup suite')

        def teardown(self):
            print('Teardown suite')


    suite = ExampleSuite(__name__)


    @suite.add_setup
    def setup():
        print('Setup 2 suite')


    @suite.add_teardown
    def teardown():
        print('Teardown 2 suite')


    @suite.register
    def function_test(case):
        case.log('Hello')


    if __name__ == '__main__':
        seismograph.main()


How to require extensions
-------------------------

Seismograph have extensions for test development. It's our feature, we are differ of other by that.


.. code-block:: python

    import seismograph


    suite = seismograph.Suite(__name__, require=['selenium'])


    @suite.register
    def test_google_search(case):
        with case.ext('selenium') as browser:
            browser.go_to('http://google.com')
            search = browser.input(name='q').first()
            search.set('python')
            button = browser.button(name='btnG').first()
            button.click()

            selenium.assertion.text_in(browser, 'python')


    if __name__ == '__main__':
        seismograph.main()


How to use extensions
---------------------

You can use extensions from suite object. Sometimes this can be helpful.


.. code-block:: python

    import seismograph


    class ExampleSuite(seismograph.Suite):

        __require__ = (
            'mock_server',
        )

        def setup(self):
            self.ext('mock_server').start()

        def teardown(self):
            self.ext('mock-server').stop()


    suite = ExampleSuite(__name__)


    @suite.register
    def function_test(case):
        # do something


    if __name__ == '__main__':
        seismograph.main()


How can i add info to reason storage?
-------------------------------------

This is reason of crash by any problem.
She will be save to xunit report and write to console.


.. code-block:: python

    import seismograph


    suite = seismograph.Suite(__name__)


    @suite.add_setup
    def setup():
        suite.reason_storage['username'] = 'John Smith'
        raise Exception('Ooops!')


    @suite.register
    def function_test(case):
        # do something


    if __name__ == '__main__':
        seismograph.main()
