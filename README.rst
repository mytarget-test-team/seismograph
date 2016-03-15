Seismograph
===========


About
-----

This is framework for test development.
It makes life so easy because has flexible structure.
If you are needing for extension which is not, that you can to create
issue on github or implemented it and send merge request.


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

Full installation::

    pip install seismograph


Simple install(for unit testing, without extensions)::

    SIMPLE_SEISMOGRAPH=true pip install seismograph


With choice extensions::

    SEISMOGRAPH_EXTENSIONS='selenium, mocker' pip install seismograph


Documentation
-------------

http://pythonhosted.org/seismograph/


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
