# -*- coding: utf-8 -*-

from seismograph import Context, step
from seismograph.ext import selenium


suite = selenium.Suite(__name__)


@suite.register
class TestGoogleSearch(selenium.Case):

    __flows__ = (
        Context(text='python'),
    )

    def test_search(self, browser, ctx):
        browser.router.go_to('/')
        browser.input(name='q').set(ctx.text)
        browser.button(name='btnG').click()

        self.assertion.text_exist(browser, ctx.text)


@suite.register
class TestStepsForSelenium(selenium.Case):

    __flows__ = (
        Context(text='python'),
    )

    @step(1, 'To open google')
    def open_google(self, browser, ctx):
        browser.router.go_to('/')

    @step(2, 'To fill search form')
    def fill_search_form(self, browser, ctx):
        browser.input(name='q').set(ctx.text)
        browser.button(name='btnG').click()

    @step(3, 'To check result')
    def check_result(self, browser, ctx):
        self.assertion.text_exist(browser, ctx.text)
