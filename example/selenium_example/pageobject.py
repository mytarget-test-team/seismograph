# -*- coding: utf-8 -*-

from seismograph.ext import selenium


suite = selenium.Suite(__name__)


class SearchField(selenium.PageObjectProxy):

    def fill(self, value):
        self._wrapped.set(value)


class IndexPage(selenium.Page):

    search_field = selenium.PageObject(
        selenium.query('input', name='q'),
        proxy_class=SearchField,
    )

    search_button = selenium.PageObject(
        selenium.query('button', name='btnG'),
    )


selenium.add_route('/', IndexPage)


@suite.register
def test_google_search(case, browser):
    page = browser.router.get('/')
    page.search_field.fill('python')
    page.search_button.click()

    case.assertion.text_in_page(browser, 'python')
