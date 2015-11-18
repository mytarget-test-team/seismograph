# -*- coding: utf8 -*-

import logging

try:
    from urllib import urlencode
except ImportError:  # please python 3
    from urllib.parse import urlencode

from sqlalchemy import event
from sqlalchemy.pool import NullPool
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.result import exc
from sqlalchemy.orm import scoped_session

from . import registry
from .session import Session
from .constants import DEFAULT_BIND_KEY
from .constants import DEFAULT_POOL_CLASS


logger = logging.getLogger(__name__)


DEFAULT_AUTO_FLUSH = True
DEFAULT_AUTO_COMMIT = False
DEFAULT_EXPIRE_ON_COMMIT = True


def ping_connection(connection, connection_record, connection_proxy):
    cursor = connection.cursor()

    try:
        cursor.execute('SELECT 1')
    except:
        raise exc.DisconnectionError()

    cursor.close()


def setup_engine(
        protocol,
        host,
        port,
        db,
        user,
        password=None,
        dns_params=None,
        bind_key=DEFAULT_BIND_KEY,
        pool_class=DEFAULT_POOL_CLASS,
        **engine_options):
    """
    :param host: db host
    :param port: db port
    :param db: db name
    :param user: user name
    :param password: user password
    :param protocol: dns protocol
    :param pool_class: pool class (original param name: poolclass)
    :param dns_params: params to dns
    :param engine_options: engine kwargs
    """
    logger.debug('Setup engine for database "{}"'.format(db))

    if dns_params and isinstance(dns_params, dict):
        dns_params = '?' + urlencode(dns_params)
    else:
        dns_params = ''

    dns = '{protocol}://{user}:{password}@{host}:{port}/{database}' + dns_params
    dns = dns.format(
        user=user,
        host=host,
        port=port,
        database=db,
        protocol=protocol,
        password=password or '',
    )
    pool_class = pool_class or DEFAULT_POOL_CLASS

    logger.debug('DNS is "{}"'.format(dns))
    logger.debug('Bind key is "{}"'.format(bind_key))
    logger.debug('Pool class is "{}"'.format(pool_class.__name__))

    engine = create_engine(
        dns,
        poolclass=pool_class,
        **engine_options
    )

    if pool_class != NullPool:
        event.listen(engine, 'checkout', ping_connection)

    registry.register_engine(bind_key, engine)


def setup_session(
        autoflush=DEFAULT_AUTO_FLUSH,
        autocommit=DEFAULT_AUTO_COMMIT,
        expire_on_commit=DEFAULT_EXPIRE_ON_COMMIT,
        **options):
    """
    Setup orm session
    """
    logger.debug('Setup orm session')

    sess = scoped_session(
        sessionmaker(
            class_=Session,
            autoflush=autoflush,
            autocommit=autocommit,
            expire_on_commit=expire_on_commit,
            **options
        ),
    )
    registry.register_session(sess)
