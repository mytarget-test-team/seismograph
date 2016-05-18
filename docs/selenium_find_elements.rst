Find elements
=============

You can to use origin api from selenium lib but we offer to do it easy.


Easy query by css selector
--------------------------

You can to use tag name as method name and tag attributes as keyword arguments.
If you want to use class attribute or id or another attributes which has conflict
with python's global names so you can to use "_" as prefix or suffix for that.


.. code-block:: python

    import seismograph
    from seismograph.ext import selenium


    suite = selenium.Suite(__name__)


    @suite.register
    def function_example(case, browser):
        browser.go_to('http://google.com')

        search = browser.input(name='q').first()
        search.set('python')
        button = browser.button(name='btnG').first()
        button.click()


    if __name__ == '__main__':
        seismograph.main()


Query object
------------

You can to create query separately of browser and to get result by request of.


.. code-block:: python

    import seismograph
    from seismograph.ext import selenium


    suite = selenium.Suite(__name__)


    def get_some_element(browser):
        query = selenium.query(selenium.query.DIV, _class='some-class')
        result = query(browser)
        result.wait()
        return result.first()


    @suite.register
    def example(case, browser):
        some_element = get_some_element(browser)
        # do something


Contains marker
---------------

When value of attribute contains value


.. code-block:: python

    import seismograph
    from seismograph.ext import selenium


    suite = selenium.Suite(__name__)


    @suite.register
    def example(case, browser):
        browser.go_to('http://some.address')

        some_element = browser.div(
            _class=selenium.query.contains('some-class'),
        ).first()


Not equal marker
----------------

When value of attribute not equal value


.. code-block:: python

    import seismograph
    from seismograph.ext import selenium


    suite = selenium.Suite(__name__)


    @suite.register
    def example(case, browser):
        browser.go_to('http://some.address')

        some_element = browser.div(
            _class=selenium.query.not_equal('some-class'),
        ).first()


Endswith marker
---------------

When value of attribute ends with value


.. code-block:: python

    import seismograph
    from seismograph.ext import selenium


    suite = selenium.Suite(__name__)


    @suite.register
    def example(case, browser):
        browser.go_to('http://some.address')

        some_element = browser.div(
            _class=selenium.query.endswith('some-class'),
        ).first()


Startswith marker
-----------------

When value of attribute starts with value


.. code-block:: python

    import seismograph
    from seismograph.ext import selenium


    suite = selenium.Suite(__name__)


    @suite.register
    def example(case, browser):
        browser.go_to('http://some.address')

        some_element = browser.div(
            _class=selenium.query.startswith('some-class'),
        ).first()


Not contains marker
-------------------

When value of attribute does not contains value


.. code-block:: python

    import seismograph
    from seismograph.ext import selenium


    suite = selenium.Suite(__name__)


    @suite.register
    def example(case, browser):
        browser.go_to('http://some.address')

        some_element = browser.div(
            _class=selenium.query.not_contains('some-class'),
        ).first()



Expression
----------

When require expression for value of attribute


.. code-block:: python

    import seismograph
    from seismograph.ext import selenium


    suite = selenium.Suite(__name__)


    @suite.register
    def example(case, browser):
        browser.go_to('http://some.address')

        some_element = browser.div(
            _class=selenium.query.expression(
                selenium.query.contains('some-class'),
                selenium.query.not_contains('hide'),
            )
        ).first()


Chain of query
--------------

If you want to follow into DOM tree then you can to do it like


.. code-block:: python

    import seismograph
    from seismograph.ext import selenium


    suite = selenium.Suite(__name__)


    @suite.register
    def function_example(case, browser):
        browser.go_to('http://some.address')

        element = browser.div(name='some_name').first()
        second_element = element.li(_class='some-class').first()


or like


.. code-block:: python

    @suite.register
    def function_example(case, browser):
        browser.go_to('http://some.address')

        second_element = browser.div(name='some_name').li(_class='some-class').first()


Css query result api
--------------------

.. autoclass:: seismograph.ext.selenium.query.QueryResult
    :members:
    :exclude-members: __dict__, __weakref__
    :private-members:
    :special-members:

