Welcome to documentation
========================

.. toctree::
    :maxdepth: 2

    case
    suite
    program
    scripts
    config
    layers
    extensions
    scope


About
-----

This is framework for functional test development.
Who is needing to him?
The target audience is test developers.
You can use the framework for unit testing and how you wish but him made
for functional testing web servers and web applications.


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
