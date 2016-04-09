# -*- coding: utf-8 -*-

from functools import wraps

from selenium.common.exceptions import NoSuchElementException

from ..query import make_result
from ..exceptions import FieldError
from ..utils import declare_standard_callback


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
                 after_fill_trigger=None):

        self.name = name

        if not isinstance(selector, dict):
            raise ValueError('incorrect selector')

        self.value = value
        self.required = required
        self.error_mess = error_mess
        self.invalid_value = invalid_value

        self.__group = group

        self.__weight = weight
        self.__selector = selector

        self.before_fill_trigger = declare_standard_callback(before_fill_trigger)
        self.after_fill_trigger = declare_standard_callback(after_fill_trigger)

    def __getattr__(self, item):
        return getattr(self.we, item)

    def __call__(self, group):
        return self.__class__(
            self.name,
            group=group,
            weight=self.__weight,
            selector=self.selector,
            required=self.required,
            error_mess=self.error_mess,
            before_fill_trigger=self.before_fill_trigger,
            after_fill_trigger=self.after_fill_trigger,
            value=self.value() if callable(self.value) else self.value,
            invalid_value=self.invalid_value() if callable(self.invalid_value) else self.invalid_value,
        )

    @property
    def browser(self):
        return self.group.browser

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
            self.group.area, self.__tag__,
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
        value = value or self.value

        self.we.send_keys(*value)

    @clear_field_handler
    def clear(self):
        self.we.clear()


assert issubclass(Input, SimpleFieldInterface)


class TextArea(Input):

    __tag__ = 'textarea'


assert issubclass(TextArea, SimpleFieldInterface)


class Checkbox(FormField, SimpleFieldInterface):

    __tag__ = 'input'

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
            el.click()
            changed = True

        return changed

    @clear_field_handler
    def clear(self):
        pass


assert issubclass(RadioButton, SimpleFieldInterface)


class Select(FormField, SimpleFieldInterface):

    __tag__ = 'select'

    @fill_field_handler
    def fill(self, value=None):
        value = value or self.value
        option = self.we.option().all().get_by(value=value)

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
