# -*- coding: utf-8 -*-

from seismograph import Case, Suite
from seismograph.ext.mock_server import JsonMock


suite = Suite(__name__, require=['mock_server'])


@suite.register
class TestSimpleMocks(Case):
    """
    Usage with control on case.
    You can start server on program setup callback.
    """

    server = None

    __repeatable__ = False

    def setup(self):
        self.server = self.ext('mock_server')
        self.server.start()

    def teardown(self):
        self.server.stop()

    def test_01_hello_get(self):
        response = self.server.client.get('/hello')
        self.assertion.equal(response.status_code, 200)
        self.assertion.equal(response.headers['Server'], 'nginx/1.2.1')

        data = response.json()
        self.assertion.equal(data['hello'], 'hello world!')

    def test_02_add_mock_on_the_wing(self):
        mock = JsonMock(
            'my_mock_2',
            '/hello',
            {'result': 'created'},
            http_method='POST',
            status_code=201,
            headers={
                'Server': 'nginx/1.2.1',
            },
        )
        self.server.add_mock(mock)

        response = self.server.client.post('/hello')
        self.assertion.equal(response.status_code, 201)
        self.assertion.equal(response.headers['Server'], 'nginx/1.2.1')

        data = response.json()
        self.assertion.equal(data['result'], 'created')

    def test_03_rewrite_mock_on_the_wing(self):
        mock = JsonMock(
            'my_mock_3',
            '/hello',
            {'hello': 'just say hello'},
            http_method='GET',
            status_code=201,
            headers={
                'Server': 'nginx/1.2.2',
            },
        )

        with self.server.mock(mock):
            response = self.server.client.get('/hello')
            self.assertion.equal(response.status_code, 201)
            self.assertion.equal(response.headers['Server'], 'nginx/1.2.2')

            data = response.json()
            self.assertion.equal(data['hello'], 'just say hello')

        self.test_01_hello_get()

    def test_04_rewrite_mock_on_the_wing_where_not_exist(self):
        mock = JsonMock(
            'my_mock_4',
            '/hello/dolly',
            {'hello': 'just say hello'},
            http_method='GET',
            status_code=200,
            headers={
                'Server': 'nginx/1.2.1',
            },
        )

        with self.server.mock(mock):
            response = self.server.client.get('/hello/dolly')
            self.assertion.equal(response.status_code, 200)
            self.assertion.equal(response.headers['Server'], 'nginx/1.2.1')

            data = response.json()
            self.assertion.equal(data['hello'], 'just say hello')

        response = self.server.client.get('/hello/dolly')
        self.assertion.equal(response.status_code, 404)

    def test_05_rewrite_mock_on_the_wing_where_was_exist(self):
        mock = JsonMock(
            'my_mock_5',
            '/hello/dolly',
            {'hello': 'just say hello'},
            http_method='GET',
            status_code=200,
            headers={
                'Server': 'nginx/1.2.1',
            },
        )

        with self.server.mock(mock):
            response = self.server.client.get('/hello/dolly')
            self.assertion.equal(response.status_code, 200)
            self.assertion.equal(response.headers['Server'], 'nginx/1.2.1')

            data = response.json()
            self.assertion.equal(data['hello'], 'just say hello')

        response = self.server.client.get('/hello/dolly')
        self.assertion.equal(response.status_code, 404)


if __name__ == '__main__':
    import seismograph
    seismograph.main()
