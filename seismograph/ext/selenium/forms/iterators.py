# -*- coding: utf-8 -*-

from collections import Iterator


class FieldsIterator(Iterator):

    def __init__(self, group, exclude=None):
        exclude = exclude or tuple()

        self.__current_index = 0
        self.__fields = [
            field for field in group.fields
            if field not in exclude
        ]

    def next(self):
        try:
            field = self.__fields[self.__current_index]
        except IndexError:
            self.__current_index = 0
            raise StopIteration

        self.__current_index += 1

        return field


class FieldsWithContainsInvalidValueIterator(Iterator):

    def __init__(self, group, exclude=None):
        exclude = exclude or tuple()

        self.__current_index = 0
        self.__fields = [
            field for field in group.fields
            if field not in exclude and field.invalid_value is not None
        ]

    def next(self):
        try:
            field = self.__fields[self.__current_index]
        except IndexError:
            self.__current_index = 0
            raise StopIteration

        self.__current_index += 1

        return field


class RequiredFieldsIterator(Iterator):

    def __init__(self, group, exclude=None):
        exclude = exclude or tuple()

        self.__current_index = 0
        self.__fields = [
            field for field in group.fields
            if field.required and field not in exclude
        ]

    def next(self):
        try:
            field = self.__fields[self.__current_index]
        except IndexError:
            self.__current_index = 0
            raise StopIteration

        self.__current_index += 1

        return field
