# -*- coding: utf-8 -*-

from functools import wraps


RESET = '\033[0m'


def reset_color(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return '{}{}'.format(
            f(*args, **kwargs), RESET,
        )
    return wrapper


@reset_color
def green(string):
    return '\033[32m{}\033[42m'.format(string)


@reset_color
def red(string):
    return '\033[31m{}\033[41m'.format(string)


@reset_color
def yellow(string):
    return '\033[33m{}\033[43m'.format(string)


@reset_color
def blue(string):
    return '\033[34m{}\033[44m'.format(string)
