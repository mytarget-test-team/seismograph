# -*- coding: utf-8 -*-

"""
Alternative for test runner.
Combine runnable objects and run their.
"""

from __future__ import absolute_import


def get_pool_size_of_value(value, in_two=False):
    from multiprocessing import cpu_count

    if value <= 0:
        size = cpu_count()
    else:
        size = value

    if in_two and value <= 0:
        return int(round(size / 2)) or 2

    return size
