# -*- coding: utf-8 -*-

from __future__ import absolute_import

from gevent import Greenlet
from gevent.wsgi import WSGIServer


class RunServerInGreenlet(Greenlet):

    def __init__(self, mock_server):
        self._httpd = None
        self._mock_server = mock_server

        super(RunServerInGreenlet, self).__init__()

    def run(self):
        self._httpd = WSGIServer(
            (self._mock_server.config.HOST, self._mock_server.config.PORT),
            self._mock_server,
            log='default' if self._mock_server.config.DEBUG else None,
        )
        self._httpd.start()

    def stop(self):
        if self._httpd:
            self._httpd.stop()
