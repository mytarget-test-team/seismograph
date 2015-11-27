Simple usage
============

You can create you test script in context selenium extension. Browser will be started and stopped automatically.


.. code-block:: python

    import seismograph


    suite = seismograph.Suite(__name__, require=['selenium'])


    @suite.register
    def selenium_example(case):
        with case.ext('selenium') as browser:
            browser.go_to('http://google.com')


    if __name__ == '__main__':
        seismograph.main()
