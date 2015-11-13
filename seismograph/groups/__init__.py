# -*- coding: utf-8 -*-

"""
Alternative for test runner.
Combine runnable objects and run their.
"""

from __future__ import absolute_import


def get_pool_size_of_value(value, in_two=False):
    from multiprocessing import cpu_count

    size = value

    if size <= 0:
        size = cpu_count()

    if in_two:
        return int(round(size / 2)) or 2

    return size
