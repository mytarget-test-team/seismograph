# -*- coding: utf-8 -*-

import json
import pickle
import marshal

from .utils import pyv


XML_VERSION = '1.0'
XML_ENCODING = 'UTF-8'

ROUND_RUNTIME = 3


class XUnitData(object):

    def __init__(self,
                 exc=None,
                 reason=None,
                 runtime=None,
                 exc_type=None,
                 class_name=None,
                 method_name=None,
                 exc_message=None):
        if exc:
            self.parse_exc(exc)
        else:
            self.__exc_type = exc_type
            self.__exc_message = exc_message

        self.__reason = reason
        self.__runtime = runtime
        self.__class_name = class_name
        self.__method_name = method_name

    @classmethod
    def from_dict(cls, dct):
        return cls(**dct)

    @classmethod
    def from_json(cls, string):
        return cls(**json.loads(string))

    @classmethod
    def from_pickle(cls, string):
        return cls(**pickle.loads(string))

    @classmethod
    def from_marshal(cls, string):
        return cls(**marshal.loads(string))

    @property
    def reason(self):
        return self.__reason

    @reason.setter
    def reason(self, value):
        self.__reason = value

    @property
    def runtime(self):
        return round(self.__runtime, ROUND_RUNTIME)

    @property
    def exc_type(self):
        return self.__exc_type

    @property
    def class_name(self):
        return self.__class_name

    @property
    def exc_message(self):
        return self.__exc_message or 'Exception was raised without message. Look at reason.'

    @exc_message.setter
    def exc_message(self, value):
        self.__exc_message = value

    @property
    def method_name(self):
        return self.__method_name

    def to_dict(self):
        return {
            'reason': self.__reason,
            'runtime': self.__runtime,
            'exc_type': self.__exc_type,
            'class_name': self.__class_name,
            'exc_message': self.__exc_message,
            'method_name': self.__method_name,
        }

    def parse_exc(self, exc):
        self.__exc_type = '{}.{}'.format(
            exc.__class__.__module__, exc.__class__.__name__,
        )
        self.__exc_message = pyv.get_exc_message(exc)

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_pickle(self):
        return pickle.dumps(self.to_dict())

    def to_marshal(self):
        return marshal.dumps(self.to_dict())


def dict_to_tag_attributes(dct):
    string = u' ' + u' '.join(
        (
            u'{}="{}"'.format(k, screening_line(pyv.unicode(v)))
            for k, v in dct.items() if v is not None
        )
    )

    if string == ' ':
        return ''

    return string


def screening_line(string):
    string = string.replace('<', '&lt;')
    string = string.replace('>', '&gt;')
    string = string.replace('"', '&quot;')
    return string


def cdata(string):
    return u'<![CDATA[{}]]>'.format(string)


def to_xml_tag(tag_name, contains, **attributes):
    if contains:
        return u'<{0}{1}>{2}</{0}>'.format(
            tag_name, dict_to_tag_attributes(attributes), contains,
        )

    return u'<{}{} />'.format(
        tag_name, dict_to_tag_attributes(attributes))


def create_xml_document(result):
    def render_result_proxy(result_proxy):
        cases_report = []

        for _, xunit_data in result_proxy.successes:
            cases_report.append(
                to_xml_tag('testcase', None,
                           time=xunit_data.runtime,
                           name=xunit_data.method_name,
                           classname=xunit_data.class_name,
                           ),
            )

        for _, xunit_data in result_proxy.skipped:
            cases_report.append(
                to_xml_tag('testcase',
                           to_xml_tag('skipped',
                                      cdata(xunit_data.reason),
                                      ),
                           time=xunit_data.runtime,
                           name=xunit_data.method_name,
                           classname=xunit_data.class_name,
                           ),
            )

        for _, xunit_data in result_proxy.failures:
            cases_report.append(
                to_xml_tag('testcase',
                           to_xml_tag('failure',
                                      cdata(xunit_data.reason),
                                      type=xunit_data.exc_type,
                                      message=xunit_data.exc_message,
                                      ),
                           time=xunit_data.runtime,
                           name=xunit_data.method_name,
                           classname=xunit_data.class_name,
                           ),
            )

        for _, xunit_data in result_proxy.errors:
            cases_report.append(
                to_xml_tag('testcase',
                           to_xml_tag('error',
                                      cdata(xunit_data.reason),
                                      type=xunit_data.exc_type,
                                      message=xunit_data.exc_message,
                                      ),
                           time=xunit_data.runtime,
                           name=xunit_data.method_name,
                           classname=xunit_data.class_name,
                           ),
            )

        state = result_proxy.get_state()

        return to_xml_tag('testsuite',
                          u''.join(cases_report),
                          name=result_proxy.name,
                          tests=state.tests,
                          time=state.runtime,
                          skip=state.skipped,
                          errors=state.errors,
                          failures=state.failures,
                          )

    data = u''.join(
        (
            u'<?xml version="{version}" encoding="{encoding}"?>'.format(
                version=XML_VERSION,
                encoding=XML_ENCODING,
            ),
            to_xml_tag('testsuites',
                       u''.join(
                           map(render_result_proxy, result.proxies),
                       )
                       if result.proxies else render_result_proxy(result),
                       name=result.name,
                       tests=result.current_state.tests,
                       time=result.current_state.runtime,
                       skip=result.current_state.skipped,
                       errors=result.current_state.errors,
                       failures=result.current_state.failures,
                       ),
        ),
    )

    if pyv.IS_PYTHON_2:
        return data.encode('utf-8')

    return data
