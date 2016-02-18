# -*- coding: utf-8 -*-

from seismograph import Suite
from seismograph.ext import selenium


suite = Suite(__name__, require=['selenium'])


@suite.register
def test_google_search(case):
    with case.ext('selenium') as browser:
        browser.router.go_to('/')
        browser.input(name='q').set('python')
        browser.button(name='btnG').click()

        selenium.assertion.text_exist(browser, 'python')


@suite.register(case_class=selenium.Case, static=True)
def test_google_search_static(browser):
    browser.router.go_to('/')
    browser.input(name='q').set('python')
    browser.button(name='btnG').click()

    selenium.assertion.text_exist(browser, 'python')
