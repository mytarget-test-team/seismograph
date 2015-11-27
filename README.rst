Seismograph
===========


About
-----

This is framework for functional test development.
Who is needing to him?
The target audience is test developers.
You can use the framework for unit testing and how you wish but him made
for functional testing web servers and web applications.


Features
--------

* Built-in extensions
* Async launch at choice
* Real suite objects
* Test script by steps
* Test case as class, function or static function
* Context flow for test execution
* XUnit xml report
* Detailed reason of crash by any problem
* Logical layers for all runnable objects
* Time of execution measured separately for any of runnable objects
* Opportunity to repeat test with help generator object


Installation
------------

::

    pip install seismograph


Quick start
-----------

.. code-block:: python

    import seismograph


    suite = seismograph.Suite(__name__)


    @suite.register
    def my_first_test(case):
        case.assertion.equal(1, 1)


    if __name__ == '__main__':
        seismograph.main()


Run tests
---------

::

    seismograph /path/to/suites/

or like

::

    python -m seismograph /path/to/suites/


Async run
---------

* multiprocessing
* threading
* gevent (for python 2 only)
