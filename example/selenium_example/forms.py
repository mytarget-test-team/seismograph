# -*- coding: utf-8 -*-

from seismograph.ext import selenium


suite = selenium.Suite(__name__)


class SearchForm(selenium.forms.UIForm):

    search_field = selenium.forms.fields.Input(
        'Search input',
        value='python',
        selector=selenium.forms.fields.selector(name='q'),
    )

    submit = selenium.PageElement(
        selenium.query(
            selenium.query.BUTTON,
            name='btnG',
        ),
        call=lambda we: we.click(),
    )


class SearchPage(selenium.Page):

    search = selenium.PageElement(SearchForm)


@suite.register
def test_search_form(case, browser):
    browser.router.go_to('/')
    page = SearchPage(browser)
    page.search.fill()
    page.search.submit()

    case.assertion.text_exist(browser, page.search.search_field.value)
