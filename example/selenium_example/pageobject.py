# -*- coding: utf-8 -*-

from seismograph.ext import selenium


suite = selenium.Suite(__name__)


class IndexPage(selenium.Page):

    search_field = selenium.PageObject(
        selenium.query('input', name='q'),
    )

    search_button = selenium.PageObject(
        selenium.query('button', name='btnG'),
    )


selenium.add_route('/', IndexPage)


@suite.register
def test_google_search(case, browser):
    page = browser.router.get('/')
    page.search_field.set('python')
    page.search_button.click()

    case.assertion.text_in_page(browser, 'python')
