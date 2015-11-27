Suite
=====

If you get between program and case with selenium suite that you can not require selenium extension for.
Selenium suite is connected with selenium case, so if you use test functions and selenium suite that you
not need to change case class on registration.


.. code-block:: python

    import seismograph
    from seismograph.ext import selenium


    suite = selenium.Suite(__name__)


    @suite.register
    def example(case, browser):
        # do something


    if __name__ == '__main__':
        seismograph.main()
