# -*- coding: utf-8 -*-

import logging


def set_log_level_for_dependency(debug):
    loggers = (
        logging.getLogger('flask'),
        logging.getLogger('werkzeug'),
    )

    handler = [logging.StreamHandler() if debug else logging.NullHandler()]

    for logger in loggers:
        logger.handlers = handler
        logger.setLevel(logging.INFO if debug else logging.ERROR)


def endpoint(url_rule, method):
    return '{}({})'.format(method.upper(), url_rule)
