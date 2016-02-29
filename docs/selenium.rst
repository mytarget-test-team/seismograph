Selenium
========

.. toctree::
    :maxdepth: 2

    selenium_simple
    selenium_find_elements
    selenium_config
    selenium_case
    selenium_suite
    selenium_browser
    selenium_proxy
    selenium_page_object
    selenium_forms


Selenium extension is wrapper over *selenium* lib.
You can to use the extension but you should to configure it for that. See `config documentation <selenium_config.html>`_


Features
--------

* Auto start and stop browser on selenium case

Selenium case give usage browser's instance and not think about started and stopped.

* Auto save screenshot by any problem

If you make configure for screenshots that it will saved by any problem.

* Polling

Is know, selenium work unstable when we are testing ajax interfaces, it's exactly. We need to waiting for elements.
Polling give a chance to work with selenium objects (web element, web driver) and not think about this.
All methods will wait for correct execution while timeout doesn't exceeded.

* Easy query

.. code-block:: python

    element = browser.div(id='some_id').first()
    second_elements = element.li(_class='some_class').all()


* Page object

You can to do outline of page as python class and use it in your test scripts.


* Forms

Declarative approach to description UI forms. It can be related to page object.


* Routing

Pages can be related to url rule for auto creating from browser.router and can has url path for open.
