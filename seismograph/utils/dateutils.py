# -*- coding: utf-8 -*-

from __future__ import absolute_import

import calendar
import datetime as _dt
from functools import wraps
from dateutil.relativedelta import relativedelta


DEFAULT_DATE_FORMAT = '%Y-%m-%d'
DEFAULT_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


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


def _make_result(data, *handlers):
    for handler in handlers:
        data = handler(data)

    return data


def to_string(d, fmt=None):
    default_fmt = (
        DEFAULT_DATETIME_FORMAT
        if isinstance(d, _dt.datetime)
        else
        DEFAULT_DATE_FORMAT
    )
    return d.strftime(fmt or default_fmt)


def date_args_to_string(fmt):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            new_args = []
            for a in args:
                if isinstance(a, _dt.date):
                    new_args.append(to_string(a, fmt))
                else:
                    new_args.append(a)

            for k, v in kwargs.items():
                if isinstance(v, _dt.date):
                    kwargs[k] = to_string(v, fmt)
            return f(*new_args, **kwargs)

        return wrapped
    return wrapper


def minus_delta(datetime, **kwargs):
    return _make_copy(datetime - _dt.timedelta(**kwargs))


def plus_delta(datetime, **kwargs):
    return _make_copy(datetime + _dt.timedelta(**kwargs))


def minus_seconds(datetime, seconds, *handlers):
    return _make_result(minus_delta(datetime, seconds=seconds), *handlers)


def plus_seconds(datetime, seconds, *handlers):
    return _make_result(plus_delta(datetime, seconds=seconds), *handlers)


def minus_minutes(datetime, minutes, *handlers):
    return _make_result(minus_delta(datetime, minutes=minutes), *handlers)


def plus_minutes(datetime, minutes, *handlers):
    return _make_result(plus_delta(datetime, minutes=minutes), *handlers)


def minus_hours(datetime, hours, *handlers):
    return _make_result(minus_delta(datetime, hours=hours), *handlers)


def plus_hours(datetime, hours, *handlers):
    return _make_result(plus_delta(datetime, hours=hours), *handlers)


def minus_days(datetime, days, *handlers):
    return _make_result(minus_delta(datetime, days=days), *handlers)


def plus_days(datetime, days, *handlers):
    return _make_result(plus_delta(datetime, days=days), *handlers)


def minus_weeks(datetime, weeks, *handlers):
    return _make_result(minus_delta(datetime, weeks=weeks), *handlers)


def plus_weeks(datetime, weeks, *handlers):
    return _make_result(plus_delta(datetime, weeks=weeks), *handlers)


def minus_months(datetime, months, *handlers):
    return _make_result(_make_copy(datetime - relativedelta(months=months)), *handlers)


def plus_months(datetime, months, *handlers):
    return _make_result(_make_copy(datetime - relativedelta(months=-months)), *handlers)


def minus_years(datetime, years, *handlers):
    return _make_result(_make_copy(datetime - relativedelta(years=years)), *handlers)


def plus_years(datetime, years, *handlers):
    return _make_result(_make_copy(datetime - relativedelta(years=-years)), *handlers)


def to_start_week(datetime, *handlers):
    days = _dt.datetime.now().weekday()
    return _make_result(minus_delta(datetime, days=days), *handlers)


def to_start_month(datetime, *handlers):
    return _make_result(_make_copy(datetime.replace(day=1)), *handlers)


def to_start_year(datetime, *handlers):
    return _make_result(_make_copy(datetime.replace(day=1, month=1)), *handlers)


def to_end_month(datetime, *handlers):
    _, end_day = calendar.monthrange(datetime.year, datetime.month)
    return _make_result(_make_copy(datetime.replace(day=end_day)), *handlers)


def to_date(date, *handlers):
    return _make_result(_dt.date(date.year, date.month, date.day), *handlers)


def now(*handlers):
   return _make_result(_dt.datetime.now(), *handlers)


def date(year, month, day, *handlers):
    return _make_result(_dt.date(year, month, day), *handlers)


def today(*handlers):
    return _make_result(_dt.date.today(), *handlers)


class delta:

    minus_seconds = staticmethod(lambda s: lambda d: minus_seconds(d, s))
    plus_seconds = staticmethod(lambda s: lambda d: plus_seconds(d, s))
    minus_minutes = staticmethod(lambda m: lambda d: minus_minutes(d, m))
    plus_minutes = staticmethod(lambda m: lambda d: plus_minutes(d, m))
    minus_hours = staticmethod(lambda h: lambda d: minus_hours(d, h))
    plus_hours = staticmethod(lambda h: lambda d: plus_hours(d, h))
    minus_days = staticmethod(lambda y: lambda d: minus_days(d, y))
    plus_days = staticmethod(lambda y: lambda d: plus_days(d, y))
    minus_weeks = staticmethod(lambda w: lambda d: minus_weeks(d, w))
    plus_weeks = staticmethod(lambda w: lambda d: plus_weeks(d, w))
    minus_months = staticmethod(lambda m: lambda d: minus_months(d, m))
    plus_months = staticmethod(lambda m: lambda d: plus_months(d, m))
    minus_years = staticmethod(lambda y: lambda d: minus_years(d, y))
    plus_years = staticmethod(lambda y: lambda d: plus_years(d, y))


class fmt:

    to_string = staticmethod(
        lambda f=None: lambda d: to_string(d, f or DEFAULT_DATE_FORMAT)
    )
