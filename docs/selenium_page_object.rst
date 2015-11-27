Page object
===========

Page object is common pattern for UI tests development. We offer our implementation.


Simple example
--------------

This code for demonstration simple usage of page object


.. code-block:: python

    import seismograph
    from seismograph import selenium


    suite = selenium.Suite(__name__)


    class GoogleSearchPage(selenium.Page):

        search_input = selenium.PageObject(
            selenium.query('input', name='q'),
        )

        submit_button = selenium.PageObject(
            selnium.query('button', name='btnG'),
        )


    @suite.register
    def test_google_search(case, browser):
        browser.go_to('http://google.com')
        page = MyFirstPage(browser)

        page.search_input.set('python')
        page.submit_button.click()


    if __name__ == '__main__':
        seismograph.main()


Page object result
------------------

Page object do return first element of query.
If you want to do it otherwise then should use additional params.


.. code-block:: python

    from seismograph import selenium


    class GoogleSearchPage(selenium.Page):

        # get element of query by index
        some_element = selenium.PageObject(
            selenium.query('link', _class='some_class'),
            index=0,
        )

        # get list of query
        some_elements = selenium.PageObject(
            selenium.query('li', id='some_id'),
            is_list=True,
        )

        # set timeout for waiting for first element of query
        another_some_element = selenium.PageObject(
            selenium.query('link', _class='some_class'),
            wait_timeout=5,
        )


How to create action for result of query
----------------------------------------

If you want to do result as function, should to wrap him for that.


.. code-block:: python

    from seismograph import selenium


    class GoogleSearchPage(selenium.Page):

        search_input = selenium.PageObject(
            selenium.query('input', name='q'),
        )

        submit = selenium.PageObject(
            selenium.query('button', name='btnG'),
            action=lambda button: button.click(),
        )


It's working so


>>> page = GoogleSearchPage(browser)
>>> page.search_input.set('some text')
>>> page.submit()


How to create proxy for result
------------------------------

If you want to wrap result of query then use proxy for that.


.. code-block:: python

    from seismograph import selenium


    class SubmitButtonProxy(selenium.PageObjectProxy):

        def do_search(self):
            self._wrapped.click()


    class GoogleSearchPage(selenium.Page):

        search_input = selenium.PageObject(
            selenium.query('input', name='q'),
        )

        submit_button = selenium.PageObject(
            selenium.query('button', name='btnG'),
            proxy=SubmitButtonProxy,
        )


It's working so


>>> page = GoogleSearchPage(browser)
>>> page.search_input.set('some text')
>>> page.submit_button.do_search()


Routing
-------

Page can be related to URL ule. URL rule is regexp pattern.


.. code-block:: python

    selenium.add_url_rule('/hello', SomePageClass)

    page = browser.router.get('/hello')
