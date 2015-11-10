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

        search = browser.input(name='q').first()
        search.set(ctx.text)

        button = browser.button(name='btnG').first()
        button.click()

        self.assertion.text_in_page(browser, ctx.text)


@suite.register
class TestStepsForSelenium(selenium.Case):

    __flows__ = (
        Context(text='python'),
    )

    @step(1, 'To open google')
    def open_google(self, driver, ctx):
        driver.router.go_to('/')

    @step(2, 'To fill search form')
    def fill_search_form(self, driver, ctx):
        search = driver.input(name='q').first()
        search.set(ctx.text)
        button = driver.button(name='btnG').first()
        button.click()

    @step(3, 'To check result')
    def check_result(self, driver, ctx):
        self.assertion.text_in_page(driver, ctx.text)
