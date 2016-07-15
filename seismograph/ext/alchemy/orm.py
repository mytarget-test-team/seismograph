# -*- coding: utf-8 -*-

import logging
from contextlib import contextmanager

from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.ext.declarative import declarative_base as _declarative_base

from . import registry
from .constants import DEFAULT_BIND_KEY


logger = logging.getLogger(__name__)

Session = registry.get_session()


@contextmanager
def session_scope(rollback=False):
    session = Session()
    try:
        yield session
    except BaseException as error:
        if rollback:
            session.rollback()
        raise error
    finally:
        session.close()


def dict_info(params):
    """
    :type params: dict
    """
    return u', '.join([u'%s=%s' % p for p in params.items()])


class StaticProperty(property):

    def __get__(self, obj, type=None):
        return classmethod(self.fget).__get__(obj, type)()


class ModelObjects(object):

    DEFAULT_OFFSET = 0
    DEFAULT_LIMIT = 100

    def __init__(self, model):
        self.__model = model

    def get(self, pk):
        with session_scope() as session:
            obj = session.query(self.__model).get(pk)
        return obj

    def get_by(self, **params):
        with session_scope() as session:
            obj = session.query(self.__model).filter_by(**params).first()
        return obj

    def getlist(self, offset=DEFAULT_OFFSET, limit=DEFAULT_LIMIT):
        with session_scope() as session:
            result = session.query(self.__model).offset(offset).limit(limit).all()
        return result

    def getlist_by(self, offset=DEFAULT_OFFSET, limit=DEFAULT_LIMIT, **params):
        with session_scope() as session:
            result = session.query(self.__model).filter_by(**params).offset(offset).limit(limit).all()
        return result

    def update_by(self, by, **params):
        with session_scope(rollback=True) as session:
            objects = session.query(self.__model).filter_by(**by).all()

        for obj in objects:
            for k, v in params.items():
                setattr(obj, k, v)

            with session_scope() as session:
                session.add(obj)
                session.commit()
                session.refresh(obj)

        return objects

    def remove_by(self, **params):
        with session_scope() as session:
            objects = session.query(self.__model).filter_by(**params).all()

        for obj in objects:
            with session_scope(rollback=True) as session:
                session.delete(obj)
                session.commit()


class ModelCRUD(object):

    query = Session.query_property()

    def __init__(self, **params):
        logger.debug('create new object of model {}'.format(self.__class__.__name__))

        for k, v in params:
            setattr(self, k, v)

    @StaticProperty
    def objects(cls):
        return ModelObjects(cls)

    @classmethod
    @contextmanager
    def bind_key(cls, bind_key):
        to_restore = cls.__mapper__.mapped_table.info['bind_key']
        cls.__mapper__.mapped_table.info['bind_key'] = bind_key
        try:
            yield
        finally:
            cls.__mapper__.mapped_table.info['bind_key'] = to_restore

    @classmethod
    def create(cls, **params):
        instance = cls(**params)

        with session_scope(rollback=True) as session:
            session.add(instance)
            session.commit()
            try:
                session.refresh(instance)
            except InvalidRequestError as error:
                if not getattr(cls, '__disable_worn__', None):
                    logger.warn(error, exc_info=True)

        return instance

    def to_dict(self):
        return dict(
            (k, self.__dict__[k])
            for k in self.__dict__
            if not k.startswith('_')
        )

    def update(self, **params):
        with session_scope() as session:

            for k, v in params.items():
                setattr(self, k, v)

            session.add(self)
            session.commit()

            try:
                session.refresh(self)
            except InvalidRequestError as error:
                if not getattr(self, '__disable_worn__', None):
                    logger.warn(error, exc_info=True)

    def remove(self):
        with session_scope() as session:
            session.delete(self)
            session.commit()

    def refresh(self):
        pk_columns = self.__table__.primary_key.columns.keys()
        refreshed_obj = self.objects.get_by(**dict((n, getattr(self, n)) for n in pk_columns))
        data_to_update = dict((k, v) for k, v in refreshed_obj.to_dict().items() if k not in pk_columns)

        for k, v in data_to_update.items():
            setattr(self, k, v)

    def __repr__(self):
        if hasattr(self, 'id'):
            return '<{} id={}>'.format(self.__class__.__name__, self.id or 'NULL')

        return '<{}>'.format(self.__class__.__name__)


class BoundDeclarativeMeta(DeclarativeMeta):

    def __init__(self, name, bases, d):
        DeclarativeMeta.__init__(self, name, bases, d)

        try:
            bind_key = d.pop('__bind_key__', None)

            if not bind_key:
                for base in bases:
                    if getattr(base, '__bind_key__', None):
                        bind_key = getattr(base, '__bind_key__')
                        break
                else:
                    bind_key = DEFAULT_BIND_KEY

            self.__table__.info['bind_key'] = bind_key
        except AttributeError:
            pass


def declarative_base(cls=None, bind_key=None, **kw):
    return _declarative_base(
        cls=type(
            'ModelCRUD',
            (cls, ModelCRUD) if cls else (ModelCRUD, ),
            {'__bind_key__': bind_key or DEFAULT_BIND_KEY},
        ),
        metaclass=BoundDeclarativeMeta,
        **kw
    )


BaseModel = _declarative_base(cls=ModelCRUD, metaclass=BoundDeclarativeMeta)
