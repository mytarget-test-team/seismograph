# -*- coding: utf-8 -*-

from seismograph import Case, Suite
from seismograph.ext import mocker
from seismograph.ext.mocker import client


suite = Suite(__name__, require=['mocker'])


@suite.register
class TestSimpleMocks(Case):
    """
    Usage with control on case.
    You can start server on program setup callback.
    """

    __repeatable__ = False

    def setup(self):
        self.mocker = self.ext('mocker')
        self.mocker.start()

    def teardown(self):
        self.mocker.stop()

    def test_01_add_mock_on_the_wing(self):
        self.mocker.add_mock(
            '/hello/world',
            status=201,
            method='POST',
            json={'result': 'created'},
            headers={
                'Server': 'nginx/1.2.1',
            },
        )

        response = client.instance.post('/hello/world')
        self.assertion.equal(response.status_code, 201)
        self.assertion.equal(response.headers['Server'], 'nginx/1.2.1')

        data = response.json()
        self.assertion.equal(data['result'], 'created')

    @mocker.mock('/test-url', html='<html><body></body></html>', status=200)
    def test_02_decorator(self):
        response = client.instance.get('/test-url')

        self.assertion.equal(response.text, '<html><body></body></html>')
        self.assertion.equal(response.headers['Content-Type'], 'text/html')
