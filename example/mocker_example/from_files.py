# -*- coding: utf-8 -*-

from seismograph import Case, Suite
from seismograph.ext.mocker import client


suite = Suite(__name__, require=['mocker'])


@suite.register
class TestMocksFromFiles(Case):

    mocker = None

    def setup(self):
        self.mocker = self.ext('mocker')
        self.mocker.start()

    def teardown(self):
        self.mocker.stop()

    def test_hello_get(self):
        response = client.instance.get('/hello')
        self.assertion.equal(response.status_code, 200)
        self.assertion.equal(response.headers['Server'], 'nginx/1.2.1')

        data = response.json()
        self.assertion.is_instance(data['data'], list)
        self.assertion.equal(data['test']['test'], 3.5)
        self.assertion.equal(data['hello'], 'hello world!')

    def test_hello_put(self):
        response = client.instance.put('/hello')
        self.assertion.equal(response.status_code, 200)
        self.assertion.equal(response.headers['Server'], 'nginx/1.2.1')

        data = response.json()
        self.assertion.equal(data['result'], 'changed')

    def test_hello_post(self):
        response = client.instance.post('/hello')
        self.assertion.equal(response.status_code, 201)
        self.assertion.equal(response.headers['Server'], 'nginx/1.2.1')

        data = response.json()
        self.assertion.equal(data['result'], 'created')
