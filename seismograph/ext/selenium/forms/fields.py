# -*- coding: utf-8 -*-

from functools import wraps

from selenium.common.exceptions import NoSuchElementException

from ....utils import pyv
from ..query import make_result
from ..exceptions import FieldError
from ..utils import declare_standard_callback


def _if_value_is_int_then_to_string(value):
    if type(value) is int:
        return str(value)
    return value


def selector(**kwargs):
    """
    proxy for tag attributes
    """
    return kwargs


def fill_field_handler(f):
    @wraps(f)
    def wrapper(self, value=None):
        if self.value is None and value is None:
            return

        if callable(self.before_fill_trigger):
            self.before_fill_trigger(self)

        result = f(self, value=value)

        if callable(self.after_fill_trigger):
            self.after_fill_trigger(self)

        self.group.fill_memo.add(self)

        return result
    return wrapper


def clear_field_handler(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        result = f(self, *args, **kwargs)

        try:
            self.group.fill_memo.remove(self)
        except KeyError:
            pass

        return result
    return wrapper


class SimpleFieldInterface(object):

    @property
    def weight(self):
        raise NotImplementedError(
            'Property "weight" not implemented in "{}"'.format(
                self.__class__.__name__,
            ),
        )

    def fill(self, value=None):
        raise NotImplementedError(
            'Method "fill" not implemented in "{}"'.format(
                self.__class__.__name__,
            ),
        )

    def clear(self):
        raise NotImplementedError(
            'Method "clear" not implemented in "{}"'.format(
                self.__class__.__name__,
            ),
        )


class FormField(object):
    """
    Base class for all fields
    """

    __tag__ = None

    def __init__(self,
                 name,
                 value=None,
                 group=None,
                 weight=None,
                 selector=None,
                 required=False,
                 error_mess=None,
                 invalid_value=None,
                 before_fill_trigger=None,
                 after_fill_trigger=None,
                 area=None):

        self.name = name

        self.value = value
        self.required = required
        self.error_mess = error_mess
        self.invalid_value = invalid_value

        self.__area = area
        self.__group = group

        self.__weight = weight
        self.__selector = selector or {}

        self.before_fill_trigger = declare_standard_callback(before_fill_trigger)
        self.after_fill_trigger = declare_standard_callback(after_fill_trigger)

    def __getattr__(self, item):
        return getattr(self.we, item)

    def __call__(self, group, **kwargs):
        kwargs.setdefault('area', self.__area)
        kwargs.setdefault('weight', self.__weight)
        kwargs.setdefault('selector', self.selector)
        kwargs.setdefault('required', self.required)
        kwargs.setdefault('error_mess', self.error_mess)
        kwargs.setdefault('before_fill_trigger', self.before_fill_trigger)
        kwargs.setdefault('after_fill_trigger', self.after_fill_trigger)
        kwargs.setdefault('value', self.value() if callable(self.value) else self.value)
        kwargs.setdefault(
            'invalid_value', self.invalid_value() if callable(self.invalid_value) else self.invalid_value,
        )

        return self.__class__(
            self.name,
            group=group,
            **kwargs
        )

    @property
    def browser(self):
        return self.group.browser

    @property
    def area(self):
        if self.__area:
            return self.__area(self.group.area)
        return self.group.area

    @property
    def group(self):
        if not self.__group:
            raise RuntimeError(
                'Field is not binding to group',
            )
        return self.__group

    @property
    def weight(self):
        return self.__weight

    @property
    def selector(self):
        return self.__selector

    @property
    def we(self):
        return make_result(
            self.area,
            self.__tag__,
        )(**self.__selector).first()

    @property
    def attr(self):
        return self.we.attr

    @property
    def css(self):
        return self.we.css


class Input(FormField, SimpleFieldInterface):

    __tag__ = 'input'

    @fill_field_handler
    def fill(self, value=None):
        value = _if_value_is_int_then_to_string(value or self.value)

        self.we.send_keys(*value)

    @clear_field_handler
    def clear(self):
        self.we.clear()


assert issubclass(Input, SimpleFieldInterface)


class TextArea(Input):

    __tag__ = 'textarea'


assert issubclass(TextArea, SimpleFieldInterface)


class DateInput(Input):

    __default_format__ = '%d.%m.%Y'

    def __init__(self, name, **kwargs):
        self.format = kwargs.pop('format', self.__default_format__)

        super(DateInput, self).__init__(name, **kwargs)

    def __call__(self, group, **kwargs):
        kwargs.setdefault('format', self.format)
        return super(DateInput, self).__call__(group, **kwargs)

    def _get_value(self, value):
        date = value or self.value
        if isinstance(date, pyv.basestring):
            return date
        return date.strftime(self.format)

    def fill(self, value=None):
        return super(DateInput, self).fill(
            self._get_value(value),
        )


assert issubclass(DateInput, Input)


class Checkbox(FormField, SimpleFieldInterface):

    __tag__ = 'input'

    def __init__(self,
                 name,
                 **kwargs):
        self.force = kwargs.pop('force', False)

        super(Checkbox, self).__init__(name, **kwargs)

    def __call__(self, group, **kwargs):
        kwargs.setdefault('force', self.force)
        return super(Checkbox, self).__call__(group, **kwargs)

    @fill_field_handler
    def fill(self, value=None):
        value = value or self.value

        el = self.we
        current_value = el.is_selected()

        if self.group.__allow_raises__:

            if current_value and value:
                raise FieldError('Oops, checkbox was selected')
            elif not current_value and not value:
                raise FieldError('Oops, checkbox was unselected')

        if (value and not current_value) or (not value and current_value):
            if self.force:
                while not el.is_selected():
                    el.click()
            else:
                el.click()

    @clear_field_handler
    def clear(self):
        el = self.we

        if el.is_selected():
            el.click()


assert issubclass(Checkbox, SimpleFieldInterface)


class RadioButton(Checkbox):

    __tag__ = 'input'

    @fill_field_handler
    def fill(self, value=None):
        value = value or self.value

        if value is None:
            return False

        el = self.we
        current_value = el.is_selected()
        changed = False

        if (value and not current_value) or (not value and current_value):
            if self.force:
                while not el.is_selected():
                    el.click()
            else:
                el.click()
            changed = True

        return changed

    @clear_field_handler
    def clear(self):
        pass


assert issubclass(RadioButton, SimpleFieldInterface)


class Select(FormField, SimpleFieldInterface):

    __tag__ = 'select'

    FILL_BY_TEXT = 'by text'
    FILL_BY_VALUE = 'by value'

    def __init__(self,
                 name,
                 **kwargs):
        self.fill_strategy = kwargs.pop('fill_strategy', self.FILL_BY_VALUE)

        super(Select, self).__init__(name, **kwargs)

    def __call__(self, group, **kwargs):
        kwargs.setdefault('fill_strategy', self.fill_strategy)
        return super(Select, self).__call__(group, **kwargs)

    @fill_field_handler
    def fill(self, value=None):
        value = _if_value_is_int_then_to_string(value or self.value)

        filters = {}
        if self.fill_strategy == self.FILL_BY_TEXT:
            filters['text'] = value
        elif self.fill_strategy == self.FILL_BY_VALUE:
            filters['value'] = value
        else:
            raise ValueError(
                'Incorrect value from "fill_strategy": "{}"'.format(self.fill_strategy),
            )

        option = self.we.option().all().get_by(**filters)

        if option:
            option.click()
        else:
            raise NoSuchElementException(
                u'Can not select value "{}" of field "{}", selector "{}"'.format(
                    value, self.name, str(self.selector),
                ),
            )

    @clear_field_handler
    def clear(self):
        pass


assert issubclass(Select, SimpleFieldInterface)
