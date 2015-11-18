# -*- coding: utf-8 -*-

from __future__ import absolute_import

from gevent.pool import Pool

from .. import runnable
from ..groups import get_pool_size_of_value
from ..exceptions import ALLOW_RAISED_EXCEPTIONS


def target(runnable_object, result):
    runnable_object(result)


class GeventSuiteGroup(runnable.RunnableGroup):

    def __run__(self, result):
        self._is_run = True

        pool = Pool(
            get_pool_size_of_value(
                self.config.ASYNC_SUITES,
            ),
        )

        try:
            for suite in self.objects:
                pool.spawn(target, suite, result)

            pool.join()
        except ALLOW_RAISED_EXCEPTIONS:
            pool.kill()
            raise


class GeventCaseGroup(runnable.RunnableGroup):

    def __run__(self, result):
        self._is_run = True

        pool = Pool(
            get_pool_size_of_value(
                self.config.ASYNC_TESTS, in_two=True,
            ),
        )

        try:
            for case in self.objects:
                pool.spawn(target, case, result)

            pool.join()
        except ALLOW_RAISED_EXCEPTIONS:
            pool.kill()
            raise
