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


def date_args_to_str(fmt):
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


def minus_seconds(datetime, seconds):
    return minus_delta(datetime, seconds=seconds)


def plus_seconds(datetime, seconds):
    return plus_delta(datetime, seconds=seconds)


def minus_minutes(datetime, minutes):
    return minus_delta(datetime, minutes=minutes)


def plus_minutes(datetime, minutes):
    return plus_delta(datetime, minutes=minutes)


def minus_hours(datetime, hours):
    return minus_delta(datetime, hours=hours)


def plus_hours(datetime, hours):
    return plus_delta(datetime, hours=hours)


def minus_days(datetime, days):
    return minus_delta(datetime, days=days)


def plus_days(datetime, days):
    return plus_delta(datetime, days=days)


def minus_weeks(datetime, weeks):
    return minus_delta(datetime, weeks=weeks)


def plus_weeks(datetime, weeks):
    return plus_delta(datetime, weeks=weeks)


def minus_months(datetime, months):
    return _make_copy(datetime - relativedelta(months=months))


def plus_months(datetime, months):
    return _make_copy(datetime - relativedelta(months=-months))


def minus_years(datetime, years):
    return _make_copy(datetime - relativedelta(years=years))


def plus_years(datetime, years):
    return _make_copy(datetime - relativedelta(years=-years))


def to_start_month(datetime):
    return _make_copy(datetime.replace(day=1))


def to_start_year(datetime):
    return _make_copy(datetime.replace(day=1, month=1))


def to_end_month(datetime):
    _, end_day = calendar.monthrange(datetime.year, datetime.month)
    return _make_copy(datetime.replace(day=end_day))
