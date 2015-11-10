# -*- coding: utf-8 -*-

from seismograph.ext import selenium


suite = selenium.Suite(__name__)


class SearchForm(selenium.forms.UIForm):

    search_field = selenium.forms.fields.Input(
        'Search input',
        value='python',
        selector=selenium.forms.fields.selector(name='q'),
    )

    def submit(self):
        button = self.query.button(name='btnG').first()
        button.click()


@suite.register
def test_search_form(case, browser):
    browser.router.go_to('/')
    form = SearchForm(browser)
    form.fill()
    form.submit()

    case.assertion.text_in_page(browser, form.search_field.value)
