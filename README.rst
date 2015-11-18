About
-----

This is framework for test development


Simple example
--------------

.. code-block:: python

    import seismograph


    suite = seismograph.Suite(__name__)


    suite.register
    def my_first_test(case):
        case.assertion.equal(1, 1)


    if __name__ == '__main__':
        seismograph.main()
