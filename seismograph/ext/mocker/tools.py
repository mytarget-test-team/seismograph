# -*- coding: utf-8 -*-

import logging


def set_log_level_for_dependency(debug):
    loggers = (
        logging.getLogger('flask'),
        logging.getLogger('werkzeug'),
    )

    handlers = {
        False: logging.NullHandler,
        True: logging.StreamHandler,
    }

    for logger in loggers:
        logger.handlers = []
        logger.handlers.append(handlers[bool(debug)]())
        logger.setLevel(logging.INFO if debug else logging.ERROR)


def endpoint(url_rule, method):
    return '{}({})'.format(method.upper(), url_rule)
