# -*- coding: utf-8 -*-

import re
import json

from .mock import BaseMock
from .base import BaseMockServer


CLEAN_DATA_REGEXP = re.compile(r'^\s{2}|\n|\r$')
FILE_EXTENSIONS = BaseMockServer.__file_extensions__ + ('.json', )


class JsonMock(BaseMock):

    __mime_type__ = 'application/json'
    __content_type__ = 'application/json'

    @property
    def body(self):
        return json.dumps(self._body)

    @property
    def json(self):
        return self._body

    def __on_file__(self, fp):
        super(JsonMock, self).__on_file__(fp)

        # for pre validation only
        self._body = json.loads(
            CLEAN_DATA_REGEXP.sub('', self._body),
        )


class JsonApiMockServer(BaseMockServer):

    __mock_class__ = JsonMock
    __file_extensions__ = FILE_EXTENSIONS
