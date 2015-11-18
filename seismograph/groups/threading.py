# -*- coding: utf-8 -*-

from __future__ import absolute_import

from multiprocessing.pool import ThreadPool

from .. import runnable
from ..groups import get_pool_size_of_value
from ..exceptions import ALLOW_RAISED_EXCEPTIONS


def target(runnable_object, result):
    runnable_object(result)


class ThreadingSuiteGroup(runnable.RunnableGroup):

    def __run__(self, result):
        self._is_run = True

        pool = ThreadPool(
            get_pool_size_of_value(self.config.ASYNC_SUITES),
        )

        try:
            for suite in self.objects:
                pool.apply_async(target, args=(suite, result))

            pool.close()
            pool.join()
        except ALLOW_RAISED_EXCEPTIONS:
            pool.terminate()
            raise


class ThreadingCaseGroup(runnable.RunnableGroup):

    def __run__(self, result):
        self._is_run = True

        pool = ThreadPool(
            get_pool_size_of_value(self.config.ASYNC_TESTS, in_two=True),
        )

        try:
            for case in self.objects:
                pool.apply_async(target, args=(case, result))

            pool.close()
            pool.join()
        except ALLOW_RAISED_EXCEPTIONS:
            pool.terminate()
            raise
