Proxy
=====

Web driver, web element and web element list is wrapped to proxy object.
It implemented for expand logic and get control over him.
You can get driver from any proxy object, he is available as **driver** property. It be driver proxy always.
Origin driver not available for public api but he available as **_wrapped** property.
Proxy objects is adapter for original also.


Web driver proxy
----------------

Where is him? Let get look...


.. code-block:: python

    import seismograph


    suite = seismograph.Suite(__name__, require=['selenium'])


    @suite.register
    def example(case):
        selenium = case.ext('selenium')
        browser = selenium.get_browser()
        # browser is WebDriverProxy object in reality


Web element proxy
-----------------

Where is him?


.. code-block:: python

    import seismograph
    from seismograph.ext import selenium


    suite = selenium.Suite(__name__)


    @suite.register
    def example(case, browser):
        browser.go_to('http://some.address')

        some_element = browser.div(id='some_id').first()
        # it's WebElementProxy in reality


You can get tag attribute like


.. code-block:: python

        print(some_element.attr.name)
        print(some_element.attr.class_)


You can set attribute and he will be set to html document


.. code-block:: python

        some_element.attr.id = 'some_id'


Also, you can working with css property


.. code-block:: python

        print(some_element.css.background_color)

        some_element.css.background_color = '#fff'


Web element list proxy
----------------------

Web element list like base list in python but he have additional methods.
Let look at examples...


.. code-block:: python

    from seismograph.ext import selenium


    suite = selenium.Suite(__name__)


    @suite.register
    def example(case, browser):
        browser.go_to('http://some.address')

        some_elements = browser.div(id='some_id').all()
        # it's WebElementListProxy in reality


Let get element by..


.. code-block:: python

        some_element = some_elements.get_by(_class='some_class')
        # by text also
        some_element = some_elements.get_by(text='some text')


If element will not found then **None** be returned


Let apply filter to list...


.. code-block:: python

        for element in some_elements.filter(_class='some_class'):
            # do something


Filter method will do return **generator object**
