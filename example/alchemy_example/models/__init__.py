# -*- coding: utf-8 -*-

import sqlalchemy

from seismograph.ext.alchemy import orm


class UsersModel(orm.BaseModel):

    __bind_key__ = 'test'
    __tablename__ = 'users'

    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        autoincrement=True,
        primary_key=True,
    )
    name = sqlalchemy.Column(
        sqlalchemy.String(30),
        nullable=False,
    )
    age = sqlalchemy.Column(
        sqlalchemy.Integer,
        nullable=False,
    )
