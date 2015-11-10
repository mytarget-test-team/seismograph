# -*- coding: utf-8 -*-

from seismograph import Suite
from seismograph.ext import selenium


suite = Suite(__name__, require=['selenium'])


@suite.register
def test_google_search(case):
    with case.ext('selenium') as browser:
        browser.router.go_to('/')
        search = browser.input(name='q').first()
        search.set('python')
        button = browser.button(name='btnG').first()
        button.click()

        selenium.assertion.text_in_page(browser, 'python')


@suite.register(case_class=selenium.Case, static=True)
def test_google_search_static(browser):
    browser.router.go_to('/')
    search = browser.input(name='q').first()
    search.set('python')
    button = browser.button(name='btnG').first()
    button.click()

    selenium.assertion.text_in_page(browser, 'python')
