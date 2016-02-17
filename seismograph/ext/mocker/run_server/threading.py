# -*- coding: utf-8 -*-

from __future__ import absolute_import

from threading import Thread


class RunServerInThread(Thread):

    def __init__(self, mock_server, server_class):
        self._httpd = None
        self._mock_server = mock_server
        self._server_class = server_class

        super(RunServerInThread, self).__init__()

    def run(self):
        self._httpd = self._server_class(
            self._mock_server.host,
            self._mock_server.port,
            self._mock_server,
        )
        self._httpd.serve_forever()

    def stop(self):
        if self._httpd:
            self._httpd.shutdown()
