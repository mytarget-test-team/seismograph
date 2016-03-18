Case
====

Case class is abstraction platform for your test script.
It can to be as function for usability only. So, example usage is below.


Simple usage
------------

Case can to be as:
    * class
    * function
    * static function


.. code-block:: python

    import seismograph


    suite = seismograph.Suite(__name__)


    @suite.register
    class TestCase(seismograph.Case):

        def test_something(self):
            # do something


    @suite.register
    class StepsTestCase(seismograph.Case):

        @seismograph.step(1, 'step one')
        def one(self):
            # do something

        @seismograph.step(2, 'step two')
        def two(self):
            # do something


    @suite.register
    def function_test(case):
        # do something


    @suite.register(static=True)
    def static_function_test():
        # do something


    if __name__ == '__main__':
        seismograph.main()


How to use assertion
--------------------

You can to check result of test script with help assertion object.
Look at example...


.. code-block:: python

    import seismograph


    suite = seismograph.Suite(__name__)


    @suite.register
    class ExampleCase(seismograph.Case):

        def test(self):
            self.assertion.true(1 == 1)


    @suite.register
    def function_test(case):
        case.assertion.equal(1, 1)


    @suite.register(static=True)
    def static_function_test():
        seismograph.assertion.false(1 == 2)


    if __name__ == '__main__':
        seismograph.main()


Assertion class. How to change it?
----------------------------------

.. autoclass:: seismograph.case.AssertionBase
    :members:
    :exclude-members: __dict__, __weakref__
    :private-members:
    :special-members:


If you use case as function then you want to change assertion class, maybe, you can do it so...


.. code-block:: python

    import seismograph


    suite = seismograph.Suite(__name__)


    class ExampleAssertion(seismograph.AssertionBase):

        def is_string(string, msg=None):
            self.is_instance(string, str, msg=msg)


    @suite.register
    class ExampleCase(seismograph.Case):

        __assertion_class__ = ExampleAssertion

        def test(self):
            self.assertion.is_string('hello')


    @suite.register(assertion_class=ExampleAssertion)
    def function_test(case):
        case.assertion.is_string('hello')


    if __name__ == '__main__':
        seismograph.main()


Case class. How to change it during registration?
-------------------------------------------------

Let you be writing test as simple function then you want to change case class maybe :)
This is doing so...


.. code-block:: python

    import seismograph


    suite = seismograph.Suite(__name__)


    class ExampleCase(seismograph.Case):

        def print_hello(self):
            print('Hello world!')


    @suite.register(case_class=ExampleCase)
    def function_test(case):
        case.print_hello()


    class ExampleCase2(seismograph.Case):

        def setup(self):
            print('Hello world!')

        def teardown(self):
            print('Good bye world!')


    @suite.register(static=True, case_class=ExampleCase2)
    def static_function_case():
        print('I am running!')


    if __name__ == '__main__':
        seismograph.main()


How to use setup and teardown callbacks
---------------------------------------

This is xunit ideology. We support it.


.. code-block:: python

    import seismograph


    suite = seismograph.Suite(__name__)


    class ExampleCase(seismograph.Case):

        @classmethod
        def setup_class(cls):
            # do something

        def setup(self):
            # do something

        def teardown(self):
            # do something

        @classmethod
        def teardown_class(cls):
            # do something


    @suite.register
    class MyTestCase(ExampleCase):

        def test_something(self):
            # do something


    if __name__ == '__main__':
        seismograph.main()


Ho to use case by steps
-----------------------

This can to be useful for case with complex logic.
Let look at this...


.. code-block:: python

    import seismograph


    suite = seismograph.Suite(__name__)


    class StepByStepCase(seismograph.Case):

        def setup(self):
            # do something

        def begin(self):
            # do something

        @seismograph.step(1, 'step one')
        def one(self):
            # do something

        @seismograph.step(2, 'step two')
        def two(self):
            # do something

        def finish(self):
            # do something

        def teardown(self):
            # do something


    if __name__ == '__main__':
        seismograph.main()


Begin method will be called after setup and finish before teardown.
Need to remember, finish method can't to be called if any exception was raised before.


Step performer
--------------

if you want to get control for execution step method then you should to use performer function.
It's easy, look at this... :)


.. code-block:: python

    import logging
    import seismograph

    logger = logging.getLogger(__name__)
    suite = seismograph.Suite(__name__)


    def step_log(case, method):
        result = method()
        if result:
            logger.info(result)


    class StepByStepCase(seismograph.Case):

        @seismograph.step(1, 'step one',  performer=step_log)
        def one(self):
            return 'hello'

        @seismograph.step(2, 'step two',  performer=step_log)
        def two(self):
            return 'world'


    if __name__ == '__main__':
        seismograph.main()


How to use flows. What is it?
-----------------------------

If you have only one test script and many context for it, so you can to use flows for execution.


.. code-block:: python

    import seismograph


    suite = seismograph.Suite(__name__)


    @suite.register
    class ExampleCaseClass(seismograph.Case):

        __flows__ = (
            seismograph.Context(
                text='some text',
            ),
            seismograph.Context(
                text='some text',
            ),
        )

        def test(self, ctx):
            print(ctx.text)


    @suite.register
    class ExampleCaseClass2(seismograph.Case):

        @seismograph.flows(
            seismograph.Context(
                text='some text',
            ),
            seismograph.Context(
                text='some text',
            ),
        )
        def test(self, ctx):
            print(ctx.text)


    @suite.register
    class StepsCase(seismograph.Case):

        __flows__ = (
            seismograph.Context(
                text='some text',
            ),
            seismograph.Context(
                text='some text',
            ),
        )

        @seismograph.step(1, 'step one')
        def one(self, ctx):
            print(ctx.text)

        @seismograph.step(2, 'step two')
        def two(self, ctx):
            print(ctx.text)


    @seismograph.flows(
        seismograph.Context(
            text='some text',
        ),
        seismograph.Context(
            text='some text',
        ),
    )
    @suite.register
    def function_test(case, ctx):
        print(ctx.text)


    @seismograph.flows(
        seismograph.Context(
            text='some text',
        ),
        seismograph.Context(
            text='some text',
        ),
    )
    @suite.register(static=True)
    def static_function_test(ctx):
        print(ctx.text)


    if __name__ == '__main__':
        seismograph.main()


How to use skip
---------------

Skip test or case is doing like in unittest framework.
I think, it's no problem for you :)


.. code-block:: python

    import seismograph


    suite = seismograph.Suite(__name__)


    @suite.register
    class CaseExample(seismograph.Case):

        @seismograph.skip('TODO')
        def test(self):
            # do something


    @seismograph.skip_unless(False, 'TODO')
    @suite.register
    class CaseExample(seismograph.Case):

        def test_one(self):
            # do something

        def test_two(self):
            # do something


    @seismograph.skip_if(True, 'TODO')
    @suite.register
    def function_test(case):
        # do something


    if __name__ == '__main__':
        seismograph.main()


Also, you can to use simple skip on registration case. Should to use keyword argument "skip" for that.


How to require extensions
-------------------------

You can to use extensions for your tests script. Extensions should to configure in config.


.. code-block:: python

    import seismograph


    suite = seismograph.Suite(__name__)


    @suite.register(require=['selenium'])
    def test_google_search(case):
        with case.ext('selenium') as browser:
            browser.go_to('http://google.com')
            browser.input(name='q').set('python')
            browser.button(name='btnG').click()

            selenium.assertion.text_in(browser, 'python')


    if __name__ == '__main__':
        seismograph.main()


How to use case log. What is it?
--------------------------------

Log object does store output in buffer for a while test case is running.
Log will be flushed to stream after run.
This give a chance to get sorted output while program is async running.


.. code-block:: python

    import seismograph


    suite = seismograph.Suite(__name__)


    @suite.register
    def function_test(case):
        case.log('Hello world!')


    if __name__ == '__main__':
        seismograph.main()


How can i add info to error reason?
-----------------------------------

This is reason of crash by any problem.
It will save to xunit report and write to console.


.. code-block:: python

    import seismograph


    suite = seismograph.Suite(__name__)


    @suite.register
    def function_test(case):
        case.reason_storage['username'] = 'John Smith'
        case.assertion.true(False)


    if __name__ == '__main__':
        seismograph.main()


How can i to repeat test method?
--------------------------------

It happens when is necessity to call test method within different settings.
This is for example only...


.. code-block:: python

    import requests
    import seismograph


    suite = seismograph.Suite(__name__)


    class Client(object):

        def __init__(self, addr, protocol=None):
            self._addr = addr
            self._protocol = protocol or 'http'

        @property
        def url(self):
        return '{}://{}'.format(self._protocol, self._addr)

        def switch_protocol(self, protocol):
            self._protocol = protocol

        def get(self, path, **kw):
            requests.get(self.url, **kw)


    @suite.register
    class ExampleCase(seismograph.Case):

        protocols = (
            'http',
            'https',
        )
        client = Client('google.com')

        def __repeat__(self):
            for protocol in self.protocols:
                self.client.switch_protocol(protocol)
                yield

        def test(self):
            self.client.get('/')


    if __name__ == '__main__':
        seismograph.main()


How to prepare test method?
---------------------------

Sometimes we are needing to change test method and wrap it.
You can do it so...


.. code-block:: python

    import seismograph


    suite = seismograph.Suite(__name__)


    @suite.register
    class ExampleCase(seismograph.Case):

        def __prepare__(self, method):
            def wrapper():
                print('Start')
                method()
                print('Stop')
            return wrapper


        def test(self):
            print('Run')


    if __name__ == '__main__':
        seismograph.main()
