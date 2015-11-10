# -*- coding: utf-8 -*-

from functools import wraps

from selenium.common.exceptions import NoSuchElementException

from ..query import QueryObject
from ..exceptions import FieldError


def selector(**kwargs):
    """
    proxy for tag attributes
    """
    return kwargs


def fill_field_handler(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        result = f(self, *args, **kwargs)

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
                 required=False,
                 selector=None,
                 error_mess=None,
                 invalid_value=None,
                 weight=None):

        self.name = name

        if not isinstance(selector, dict):
            raise ValueError('incorrect selector')

        self.value = value
        self.required = required
        self.error_mess = error_mess
        self.invalid_value = invalid_value

        self.__group = None

        self.__weight = weight
        self.__selector = selector

    @property
    def query(self):
        return self.we.query

    def bind(self, group):
        self.__group = group

        if callable(self.value):
            self.value = self.value()

        if callable(self.invalid_value):
            self.invalid_value = self.invalid_value()

    @property
    def driver(self):
        return self.group.driver

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
        return self.group.query.from_object(
            QueryObject(self.__tag__, **self.__selector),
        ).first()

    @property
    def attr(self):
        return self.we.attr


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

        options = filter(
            lambda opt: opt.get_attribute('value') == value,
            self.we.find_elements_by_tag_name('option'),
        )

        for option in options:
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
