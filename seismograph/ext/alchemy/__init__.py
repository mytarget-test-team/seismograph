# -*- coding: utf-8 -*-

from .extension import EX_NAME
from .extension import DBClient
from .exceptions import ConfigurationError


CONFIG_KEY = 'ALCHEMY_EX'


def __install__(program):
    config = program.config.get(CONFIG_KEY, {})

    if config:
        from . import install

        default_host = config.get('HOST')
        default_port = config.get('PORT')
        default_user = config.get('USER')
        default_password = config.get('PASSWORD')
        default_protocol = config.get('PROTOCOL')
        default_dns_params = config.get('DNS_PARAMS')
        default_pool_class = config.get('POOL_CLASS')

        session_config = config.get('SESSION', {})
        databases_config = config.get('DATABASES', {})

        for db_name, db_config in databases_config.items():
            protocol = db_config.pop('protocol', default_protocol)
            if not protocol:
                raise ConfigurationError(
                    '"protocol" is required param for database "{}"'.format(db_name),
                )

            host = db_config.pop('host', default_host)
            if not host:
                raise ConfigurationError(
                    '"host" is required param for database "{}"'.format(db_name),
                )

            port = db_config.pop('port', default_port)
            if not port:
                raise ConfigurationError(
                    '"port" is required param or database "{}"'.format(db_name),
                )

            user = db_config.pop('user', default_user)
            if not user:
                raise ConfigurationError(
                    '"user" is required param for database "{}"'.format(db_name),
                )

            password = db_config.pop('password', default_password)
            dns_params = db_config.pop('dns_params', default_dns_params)
            pool_class = db_config.pop('pool_class', default_pool_class)

            install.setup_engine(
                protocol,
                host,
                port,
                db_name,
                user,
                password=password,
                dns_params=dns_params,
                pool_class=pool_class,
                **db_config
            )

        install.setup_session(**session_config)

        program.shared_extension(EX_NAME, DBClient)
    else:
        def extension_mock():
            raise ConfigurationError(
                'Alchemy extension is not configured. Use config key "{}" for this.'.format(
                    CONFIG_KEY,
                ),
            )

        program.shared_extension(EX_NAME, extension_mock)