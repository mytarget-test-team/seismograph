# -*- coding: utf-8 -*-

from seismograph import Suite
from seismograph.ext.alchemy.exceptions import InvalidBindKey

from .models import UsersModel


suite = Suite(__name__, require=['db'])


@suite.register
def simple_test(case):
    db = case.ext('db')

    def incorrect_bind_key():
        with db.read('incorrect_bind_key'):
            execute('SELECT * FROM PLUGINS').fetchall()

    case.assertion.raises(InvalidBindKey, incorrect_bind_key)

    with db.read() as execute:
        result = execute('SELECT * FROM PLUGINS').fetchall()

    case.assertion.greater(len(result), 0)


@suite.register
def test_model(case):
    db = case.ext('db')

    def incorrect_bind_key():
        with db('incorrect_bind_key', UsersModel):
            UsersModel.objects.getlist()

    case.assertion.raises(InvalidBindKey, incorrect_bind_key)

    case.assertion.greater(
        len(UsersModel.objects.getlist()), 0,
    )

    case.assertion.greater(
        len(UsersModel.objects.getlist()), 0,
    )
