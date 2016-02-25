Case
====

Selenium case give away browser for test method and started on setup and stopped on teardown it.
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



if you want to get browser for other methods that you can to use "require_browser" decorator for that.


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


That perhaps shut off


.. code-block:: python

    import seismograph
    from seismograph.ext import selenium


    @suite.register
    class CaseExample(selenium.Case):

        __require_browser__ = False

        def test(self):
            pass


How to use flows
----------------

Browser will injected like first argument after case instance always.
You can to get context as second argument.


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


How to set page class to case
-----------------------------

Page class can be related to case.


.. code-block:: python

    from seismograph.ext import selenium


    class ExamplePage(selenium.Page):
        pass


    class ExampleCase(selenium.Case):

        __page_class__ = ExamplePage

        def test(self):
            self.page


How to checkout page
--------------------

You can to switch page on test script. Case class implemented "checkout_page" method for that.


.. code-block:: python

    from seismograph.ext import selenium


    class ExamplePage(selenium.Page):
        pass


    class ExamplePage2(selenium.Page):
        pass


    class ExampleCase(selenium.Case):

        __page_class__ = ExamplePage

        def test(self):
            self.page

            self.checkout_page(ExamplePage2)

            self.page
