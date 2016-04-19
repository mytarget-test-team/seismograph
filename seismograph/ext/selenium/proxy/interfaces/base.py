# -*- coding: utf-8 -*-

from ...query import Query


ANY_TAG_METHOD_NAME = 'any'


# Tag's names when is allowed as attribute name on proxy object instance
HTML_TAGS_ALLOWED_AS_METHOD = (
    Query.A, Query.B, Query.P, Query.U, Query.UL,
    Query.LI, Query.BR, Query.EM, Query.HR, Query.TR,
    Query.TD, Query.TH, Query.TT, Query.VAR, Query.IMG,
    Query.DIV, Query.MAP, Query.HEAD, Query.FORM, Query.BODY,
    Query.AREA, Query.CODE, Query.BASE, Query.SPAN, Query.LINK,
    Query.META, Query.SMALL, Query.TABLE, Query.INPUT, Query.LABEL,
    Query.FRAME, Query.EMBED, Query.BLINK, Query.IFRAME, Query.CENTER,
    Query.STRONG, Query.BUTTON, Query.OBJECT, Query.OPTION, Query.SELECT,
    Query.TEXTAREA, Query.OPTGROUP, Query.FRAMESET, ANY_TAG_METHOD_NAME,
)


class BaseInterface(object):
    """
    Base class to interface for proxy object
    """

    def __getattr_from_webdriver_or_webelement__(self, item):
        raise NotImplementedError(
            'Method "__getattr_from_webdriver_or_webelement__" does not implemented in "{}"'.format(
                self.__class__.__name__,
            ),
        )

    def __setattr_to_webdriver_or_webelement__(self, item, value):
        raise NotImplementedError(
            'Method "__setattr_to_webdriver_or_webelement__" does not implemented in "{}"'.format(
                self.__class__.__name__,
            ),
        )
