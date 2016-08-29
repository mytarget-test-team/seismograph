# -*- coding: utf-8 -*-

from __future__ import absolute_import

import calendar
import datetime as _dt
from functools import wraps
from dateutil.relativedelta import relativedelta


DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


def _make_copy(instance, cls=None):
    if isinstance(instance, _dt.datetime):
        cls = cls or _dt.datetime
        return cls(
            instance.year,
            instance.month,
            instance.day,
            instance.hour,
            instance.minute,
            second=instance.second,
            microsecond=instance.microsecond,
            tzinfo=instance.tzinfo,
        )
    elif isinstance(instance, _dt.date):
        cls = cls or _dt.date
        return cls(
            instance.year,
            instance.month,
            instance.day,
        )

    raise TypeError(
        'Incorrect type of object {} Expected "datetime.date" or "datetime.datetime"'.format(instance),
    )


def _datetime_to_string(datetime, fmt):
    return datetime.strftime(fmt)


def date_to_string(date, fmt=DATE_FORMAT):
    """
    Convert date object to string by format

    :type date: datetime.date
    :type fmt: str
    """
    return _datetime_to_string(date, fmt)


def datetime_to_string(datetime, fmt=DATETIME_FORMAT):
    """
    Convert datetime object to string by format

    :type date: datetime.datetime
    :type fmt: str
    """
    return _datetime_to_string(datetime, fmt)


def date_args_to_string(fmt):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            new_args = []
            for a in args:
                if isinstance(a, _dt.date):
                    new_args.append(date_to_string(a, fmt))
                else:
                    new_args.append(a)

            for k, v in kwargs.items():
                if isinstance(v, _dt.date):
                    kwargs[k] = date_to_string(v, fmt)
            return f(*new_args, **kwargs)

        return wrapped
    return wrapper


def minus_delta(datetime, **kwargs):
    return _make_copy(datetime - _dt.timedelta(**kwargs))


def plus_delta(datetime, **kwargs):
    return _make_copy(datetime + _dt.timedelta(**kwargs))


def minus_seconds(datetime, seconds, handler=None):
    date = minus_delta(datetime, seconds=seconds)
    if handler:
        return handler(date)
    return date


def plus_seconds(datetime, seconds, handler=None):
    date = plus_delta(datetime, seconds=seconds)
    if handler:
        return handler(date)
    return date


def minus_minutes(datetime, minutes, handler=None):
    date = minus_delta(datetime, minutes=minutes)
    if handler:
        return handler(date)
    return date


def plus_minutes(datetime, minutes, handler=None):
    return plus_delta(datetime, minutes=minutes)


def minus_hours(datetime, hours, handler=None):
    date = minus_delta(datetime, hours=hours)
    if handler:
        return handler(date)
    return date


def plus_hours(datetime, hours, handler=None):
    return plus_delta(datetime, hours=hours)


def minus_days(datetime, days, handler=None):
    return minus_delta(datetime, days=days)


def plus_days(datetime, days, handler=None):
    date = plus_delta(datetime, days=days)
    if handler:
        return handler(date)
    return date


def minus_weeks(datetime, weeks, handler=None):
    date = minus_delta(datetime, weeks=weeks)
    if handler:
        return handler(date)
    return date


def plus_weeks(datetime, weeks, handler=None):
    date = plus_delta(datetime, weeks=weeks)
    if handler:
        return handler(date)
    return date


def minus_months(datetime, months, handler=None):
    date = _make_copy(datetime - relativedelta(months=months))
    if handler:
        return handler(date)
    return date


def plus_months(datetime, months, handler=None):
    date = _make_copy(datetime - relativedelta(months=-months))
    if handler:
        return handler(date)
    return date


def minus_years(datetime, years, handler=None):
    date = _make_copy(datetime - relativedelta(years=years))
    if handler:
        return handler(date)
    return date


def plus_years(datetime, years, handler=None):
    date = _make_copy(datetime - relativedelta(years=-years))
    if handler:
        return handler(date)
    return date


def to_start_month(datetime, handler=None):
    date = _make_copy(datetime.replace(day=1))
    if handler:
        return handler(date)
    return date


def to_start_year(datetime, handler=None):
    date = _make_copy(datetime.replace(day=1, month=1))
    if handler:
        return handler(date)
    return date


def to_end_month(datetime, handler=None):
    _, end_day = calendar.monthrange(datetime.year, datetime.month)
    date = _make_copy(datetime.replace(day=end_day))
    if handler:
        return handler(date)
    return date
