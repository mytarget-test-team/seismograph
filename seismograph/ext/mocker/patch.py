# -*- coding: utf-8 -*-

try:
    import httplib
except ImportError:
    import http.client as httplib

from functools import wraps

from flask import abort
from flask.app import _endpoint_from_view_func


def add_url_rule(self, rule, endpoint=None, view_func=None, **options):
    if endpoint is None:
        endpoint = _endpoint_from_view_func(view_func)

    options['endpoint'] = endpoint
    methods = options.pop('methods', None)

    if methods is None:
        methods = getattr(view_func, 'methods', None) or ('GET',)

    methods = set(methods)
    required_methods = set(getattr(view_func, 'required_methods', ()))

    provide_automatic_options = getattr(
        view_func, 'provide_automatic_options', None,
    )

    if provide_automatic_options is None:
        if 'OPTIONS' not in methods:
            provide_automatic_options = True
            required_methods.add('OPTIONS')
        else:
            provide_automatic_options = False

    methods |= required_methods

    options['defaults'] = options.get('defaults') or None

    rule = self.url_rule_class(rule, methods=methods, **options)
    rule.provide_automatic_options = provide_automatic_options

    self.url_map.add(rule)

    if view_func is not None:
        old_func = self.view_functions.get(endpoint)

        if old_func is not None and old_func != view_func:
            raise AssertionError(
                'View function mapping is overwriting '
                'an existing endpoint function: %s' % endpoint,
            )

        self.view_functions[endpoint] = view_func


def dispatch_request(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except KeyError:
            abort(int(httplib.NOT_FOUND))
    return wrapper
