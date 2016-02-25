Page object
===========

Page object is common pattern for UI tests development. We offer our implementation.


Simple example
--------------

This code for demonstration of simple usage


.. code-block:: python

    import seismograph
    from seismograph import selenium


    suite = selenium.Suite(__name__)


    class GoogleSearchPage(selenium.Page):

        search_input = selenium.PageElement(
            selenium.query(
                selenium.query.INPUT,
                name='q',
            ),
        )

        submit_button = selenium.PageElement(
            selenium.query(
                selenium.query.INPUT,
                name='btnG',
            ),
        )


    @suite.register
    def test_google_search(case, browser):
        browser.go_to('http://google.com')
        page = MyFirstPage(browser)

        page.search_input.set('python')
        page.submit_button.click()


    if __name__ == '__main__':
        seismograph.main()


Page element result
-------------------

Page element does return first element of query.
If you want to do it otherwise then should to use additional params.


.. code-block:: python

    from seismograph import selenium


    class GoogleSearchPage(selenium.Page):

        # get element of query by index
        some_element = selenium.PageElement(
            selenium.query(
                selenium.query.A,
                _class='some_class',
            ),
            index=0,
        )

        # get list all elements of query
        some_elements = selenium.PageElement(
            selenium.query(
                selenium.query.LI,
                id='some_id',
            ),
            is_list=True,
        )

        # set timeout to wait for first element of query
        another_some_element = selenium.PageElement(
            selenium.query(
                selenium.query.A,
                _class='some_class',
            ),
            wait_timeout=5,
        )


How to make element of result as callable
-----------------------------------------

If you want to create call method for result, should to use "call" keyword argument for that.


.. code-block:: python

    from seismograph import selenium


    class GoogleSearchPage(selenium.Page):

        search_input = selenium.PageElement(
            selenium.query(
                selenium.query.INPUT,
                name='q',
            ),
        )

        submit = selenium.PageElement(
            selenium.query(
                selenium.query.BUTTON,
                name='btnG',
            ),
            call=lambda we: we.click(),
        )


It's working so


>>> page = GoogleSearchPage(browser)
>>> page.search_input.set('some text')
>>> page.submit()


How to create web element class
-------------------------------

If you want to wrap result then use decorator class for that.


.. code-block:: python

    from seismograph import selenium


    class SubmitButton(selenium.PageItem):

        def do_search(self):
            self.we.click()


    class GoogleSearchPage(selenium.Page):

        search_input = selenium.PageElement(
            selenium.query(
                selenium.query.INPUT,
                name='q',
            ),
        )

        submit_button = selenium.PageElement(
            selenium.query(
                selenium.query.BUTTON,
                name='btnG',
            ),
            we_class=SubmitButton,
        )


It's working so


>>> page = GoogleSearchPage(browser)
>>> page.search_input.set('some text')
>>> page.submit_button.do_search()


How to restrict area of DOM tree for query
------------------------------------------

You can to restrict area of DOM tree for search elements on page.


.. code-block:: python

    from seismograph import selenium


    class MyPage(selenium.Page):

        __area__ = selenium.query(
            selenium.query.DIV,
            _class='some-class',
        )


Routing
-------

Page class can has url path for open page.


.. code-block:: python

    from seismograph import selenium


    class MyPage(selenium.Page):

        __url_path__ = '/path/to/page'


Url path can has params for format string


.. code-block:: python

    from seismograph import selenium


    class MyPage(selenium.Page):

        __url_path__ = '/path/to/page/{id}'


    page = MyPage(browser)
    page.open(id=1)


Page class can to be related to URL ule. URL rule is regexp pattern.


.. code-block:: python

    selenium.add_url_rule('/hello', SomePageClass)

    page = browser.router.get('/hello')
