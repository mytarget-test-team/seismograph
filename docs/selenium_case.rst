Case
====

Selenium case give away browser for test method and started on setup and stopped on teardown him.
If you use selenium case or suite that you can not require extension.


.. code-block:: python

    import seismograph
    from seismograph.ext import selenium


    suite = selenium.Suite(__name__)


    @suite.register
    def function_example(case, browser):
        browser.go_to('http://google.com')


    @suite.register(static=True)
    def static_function_example(browser):
        browser.go_to('http://google.com')


    @suite.register
    class TestCaseExample(selenium.Case):

        def test(self, browser):
            browser.go_to('http://google.com')


    @suite.register
    class StepByStepExample(selenium.Case):

        @seismograph.step(1, 'Go to google')
        def go_to_google(self, browser):
            browser.go_to('http://google.com')

        @seismograph.step(2, 'Check text')
        def check_text(self, browser):
            self.assertion.greater(len(browser.text), 0)


    if __name__ == '__main__':
        seismograph.main()



if you want to get browser for other methods that you can use decorator for that.


.. code-block:: python

    import seismograph
    from seismograph.ext import selenium


    @suite.register
    class StepByStepExample(selenium.Case):

        @selenium.require_browser
        def begin(self, browser):
            # do something

        @seismograph.step(1, 'Go to google')
        def go_to_google(self, browser):
            browser.go_to('http://google.com')

        @seismograph.step(2, 'Check text')
        def check_text(self, browser):
            self.assertion.greater(len(browser.text), 0)


    if __name__ == '__main__':
        seismograph.main()


How to use flows
----------------

Browser will be injected like first argument after case instance always.
You can get context as second argument.


.. code-block:: python

    import seismograph
    from seismograph.ext import selenium


    suite = selenium.Suite(__name__)


    @seismograph.flows(
        seismograph.Context(
            path='/',
        ),
        seismograph.Context(
            path='/search',
        ),
    )
    @suite.register
    def function_example(case, browser, ctx):
        browser.go_to(
            'http://google.com{}'.format(ctx.path),
        )


    if __name__ == '__main__':
        seismograph.main()
