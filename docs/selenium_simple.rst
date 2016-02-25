Simple usage
============

You can to create you test script in context selenium extension. Browser will started and stopped by automatically.


.. code-block:: python

    import seismograph


    suite = seismograph.Suite(__name__, require=['selenium'])


    @suite.register
    def selenium_example(case):
        with case.ext('selenium') as browser:
            browser.go_to('http://google.com')


    if __name__ == '__main__':
        seismograph.main()
