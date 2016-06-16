# -*- coding: utf-8 -*-

from . import signature
from . import exceptions
from .rule import RuleObject
from .staging import Staging


class PendingList(object):

    def __init__(self):
        self.__lst = []

    def add(self, rule_object, option_value):
        self.__lst.append((rule_object, option_value))

    def delete(self, rule_object, option_value):
        self.__lst.remove((rule_object, option_value))

    def items(self):
        return tuple(self.__lst)

    def unlocked_items(self):
        return tuple(filter(lambda i: i[0].can_be_compiled, self.__lst))

    def locked_items(self):
        return tuple(filter(lambda i: not i[0].can_be_compiled, self.__lst))

    def join(self):
        iteration = 0
        length = len(self.__lst)

        while self.__lst:
            for rule_object, option_value in self.unlocked_items():
                for sig in signature.create_signatures(option_value):
                    create_schema(rule_object.compile(sig))

                self.delete(rule_object, option_value)

            iteration += 1

            if iteration > length:
                errors = []

                for rule_object, _ in self.locked_items():
                    errors.append(
                        'Builder schema "{}" can not be collected. Was required {} but does not created.'.format(
                            rule_object.name, ', '.join('"{}"'.format(r) for r in rule_object.get_current_requires())
                        ),
                    )

                    raise exceptions.SchemaError('\n'.join(errors))


def create_schema(compiled_rule):
    staging = Staging(compiled_rule)

    staging.pre()
    staging.create()
    staging.post()

    if compiled_rule.embedded_options:
        collect(
            compiled_rule.builder,
            schema=compiled_rule.embedded_schema,
            options=compiled_rule.embedded_options,
            instance=staging.embedded_instance,
        )


def collect(builder, schema=None, options=None, instance=None):
    pending_list = PendingList()

    instance = instance or builder.schema
    schema = schema or builder.__build_schema__
    options = options or builder.settings.options

    for option_name, option_value in options.items():
        try:
            option_schema = schema[option_name]
        except KeyError:
            raise exceptions.ConfigurationError(
                'Incorrect option "{}". Builder has not schema for it.'.format(option_name),
            )

        rule_object = RuleObject(option_name, builder, option_schema, instance)

        if rule_object.can_be_compiled:
            for sig in signature.create_signatures(option_value):
                create_schema(rule_object.compile(sig))
        else:
            pending_list.add(rule_object, option_value)

    pending_list.join()
