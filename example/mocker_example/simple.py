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

    def test_01_hello_get(self):
        response = client.instance.get('/hello')
        self.assertion.equal(response.status_code, 200)
        self.assertion.equal(response.headers['Server'], 'nginx/1.2.1')
        self.assertion.equal(response.headers['Content-Type'], 'application/json')

        data = response.json()
        self.assertion.equal(data['hello'], 'hello world!')

    def test_02_add_mock_on_the_wing(self):
        response = self.mocker.add_mock(
            '/hello',
            status=201,
            method='POST',
            json={'result': 'created'},
            headers={
                'Server': 'nginx/1.2.1',
            },
        )

        data = response.json()
        self.assertion.equal(data['status'], 'blocked')

        self.mocker.unblock_mock('/hello')

        response = self.mocker.add_mock(
            '/hello',
            status=201,
            method='POST',
            json={'result': 'created'},
            headers={
                'Server': 'nginx/1.2.1',
            },
        )

        data = response.json()
        self.assertion.equal(data['status'], 'added')

        response = client.instance.post('/hello')
        self.assertion.equal(response.status_code, 201)
        self.assertion.equal(response.headers['Server'], 'nginx/1.2.1')

        data = response.json()
        self.assertion.equal(data['result'], 'created')

    @mocker.mock('/test-url', html='<html><body></body></html>', status=200)
    def test_03_decorator(self):
        response = client.instance.get('/test-url')

        self.assertion.equal(response.content, '<html><body></body></html>')
        self.assertion.equal(response.headers['Content-Type'], 'text/html')

    def test_o4_html(self):
        response = client.instance.get('/world')

        self.assertion.equal(response.content, '<html><body></body></html>')
        self.assertion.equal(response.headers['Content-Type'], 'text/html')
