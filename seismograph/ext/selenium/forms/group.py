# -*- coding: utf-8 -*-

import logging
from contextlib import contextmanager

from six import with_metaclass

from .. import pageobject
from .fields import FormField
from ..query import QueryObject
from .iterators import FieldsIterator
from .fields import SimpleFieldInterface
from .iterators import RequiredFieldsIterator
from .iterators import FieldsWithContainsInvalidValueIterator


logger = logging.getLogger(__name__)


def make_field(group_class, weight=None, name=None):
    if not issubclass(group_class, FieldsGroup):
        raise ValueError('group_class is not FieldsGroup subclass')

    return GroupContainer(group_class, weight, name)


@contextmanager
def preserve_original(group, ignore_exc=None):
    try:
        if ignore_exc:
            try:
                yield
            except ignore_exc:
                pass
        else:
            yield
    finally:
        group.reload()


def iter_fields(group, exclude=None):
    assert isinstance(group, FieldsGroup)
    return FieldsIterator(group, exclude=exclude)


def iter_required(group, exclude=None):
    assert isinstance(group, FieldsGroup)
    return RequiredFieldsIterator(group, exclude=exclude)


def iter_invalid(group, exclude=None):
    assert isinstance(group, FieldsGroup)
    return FieldsWithContainsInvalidValueIterator(group, exclude=exclude)


class GroupContainer(object):

    def __init__(self, group_class, weight, name):
        self.__group_class = group_class
        self.__weight = weight
        self.__name = name

    @property
    def name(self):
        return self.__name

    def __call__(self, group):
        return self.__group_class(
            group.driver,
            parent=group,
            name=self.__name,
            weight=self.__weight,
        )


class GroupMemento(dict):

    def _set_field(self, filed):
        self[filed] = {
            'value': filed.value,
            'required': filed.required,
            'error_mess': filed.error_mess,
            'invalid_value': filed.invalid_value,
        }

    def get_field(self, filed):
        return self.get(filed)

    def add_field(self, field):
        assert isinstance(field, FormField)
        self._set_field(field)

    def restore(self, field_list):
        for field in field_list:
            orig = self.get_field(field)

            if orig:
                field.value = orig['value']
                field.required = orig['required']
                field.error_mess = orig['error_mess']
                field.invalid_value = orig['invalid_value']
            else:
                continue


class FieldsGroupMeta(pageobject.PageMeta):

    def __call__(self, *args, **kwargs):
        instance = super(FieldsGroupMeta, self).__call__(*args, **kwargs)
        attributes = (
            a for a in dir(instance.__class__) if not a.startswith('_')
        )

        for attr_name in attributes:
            attr_value = getattr(instance.__class__, attr_name, None)

            if isinstance(attr_value, (FormField, GroupContainer)):
                if attr_value.name in instance.__exclude__:
                    try:
                        delattr(instance, attr_name)
                    except AttributeError as warn:
                        logger.warn(warn, exc_info=True)
                    continue

                instance.add_field(attr_name, attr_value)

        return instance


class FieldsGroup(with_metaclass(FieldsGroupMeta, SimpleFieldInterface)):

    __wrapper__ = None
    __remember__ = True
    __exclude__ = tuple()
    __allow_raises__ = True

    def __init__(self, proxy, weight=None, name=None, parent=None):
        self.name = name or self.__class__.__name__

        self.__fields = []
        self.__parent = parent
        self.__weight = weight
        self.__fill_memo = set()
        self.__memento = GroupMemento()
        self.__proxy = proxy

    def __getattr__(self, item):
        return getattr(self.area, item)

    @property
    def driver(self):
        return self.__proxy.driver

    @property
    def area(self):
        if self.__wrapper__:
            if not isinstance(self.__wrapper__, QueryObject):
                raise TypeError(
                    '"__wrapper__" can be instance of QueryObject only',
                )
            return self.__proxy.query.from_object(
                self.__wrapper__,
            ).first()

        return self.__proxy

    @property
    def query(self):
        return self.area.query

    @property
    def fields(self):
        return self.__fields

    @property
    def weight(self):
        return self.__weight

    @property
    def fill_memo(self):
        return self.__fill_memo

    def relate_to(self, proxy):
        self.__proxy = proxy

    def add_field(self, name, field):
        if isinstance(field, GroupContainer):
            field = field(self)
            setattr(self, name, field)
        elif isinstance(field, FormField):
            field = field(self)
            setattr(self, name, field)
            self.__memento.add_field(field)
        else:
            raise TypeError('Unknown field type')

        self.__fields.append(field)
        self.__fields.sort(key=lambda f: f.weight)

    def add_subgroup(self, name, cls, weight=None):
        assert issubclass(cls, FieldsGroup),\
            '"{}" is not FieldsGroup subclass'.format(cls.__name__)

        self.add_field(
            name,
            make_field(
                cls, weight=weight, name=name,
            ),
        )

    def add_subform(self, *args, **kwargs):
        self.add_subgroup(*args, **kwargs)

    def reload(self):
        self.__memento.restore(self.__fields)

    def reset_memo(self):
        self.__fill_memo.clear()

        groups = (
            field for field in self.__fill_memo
            if isinstance(field, FieldsGroup)
        )

        for group in groups:
            group.reset_memo()

    def update(self, **kwargs):
        for field_name, value in kwargs.items():
            field = getattr(self, field_name, None)

            if isinstance(field, FieldsGroup):
                field.update(**value)
            elif isinstance(field, FormField):
                field.value = value
            else:
                raise LookupError(
                    'Field "{}" not found'.format(field_name),
                )

    def fill(self, exclude=None):
        exclude = exclude or tuple()

        for field in self.__fields:
            if (field not in self.__fill_memo) and (field not in exclude):
                field.fill()

        if self.__parent:
            self.__parent.fill_memo.add(self)

        self.reset_memo()

    def clear(self):
        for field in self.__fields:
            field.clear()

        self.reset_memo()


assert issubclass(FieldsGroup, SimpleFieldInterface)
