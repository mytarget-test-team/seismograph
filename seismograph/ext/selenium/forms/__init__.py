# -*- coding: utf-8 -*-

from . import fields
from .group import make_field
from .group import FieldsGroup
from .group import iter_fields
from .group import iter_invalid
from .group import iter_required
from .group import preserve_original


class UIForm(FieldsGroup):

    def __init__(self, proxy):
        super(UIForm, self).__init__(proxy)


__all__ = (
    'fields',
    'UIForm',
    'make_field',
    'FieldsGroup',
    'iter_fields',
    'iter_invalid',
    'iter_required',
    'preserve_original',
)
