# -*- coding: utf-8 -*-

from optparse import OptionParser

from seismograph.ext.mocker import constants
from seismograph.ext.mocker.extension import Config
from seismograph.ext.mocker.server import MockServer


def get_parser():
    parser = OptionParser('python -m seismograph.ext.mocker [options]')

    parser.add_option(
        '-p', '--port',
        type=int,
        dest='PORT',
        default=constants.DEFAULT_PORT,
        help='Server port'
    )
    parser.add_option(
        '-i', '--host',
        dest='HOST',
        default=constants.DEFAULT_HOST,
        help='Server host'
    )
    parser.add_option(
        '-m', '--path-to-mocks',
        dest='PATH_TO_MOCKS',
        default=None,
        help='Path to dir within mock files'
    )
    parser.add_option(
        '-t', '--type',
        dest='SERVER_TYPE',
        default='json_api',
        help='Server type. Can be in ({}). "json_api" by default'.format(
            ', '.join(('"simple"', '"json_api"')),
        )
    )

    parser.add_option(
        '--no-debug',
        dest='NO_DEBUG',
        action='store_false',
        default=True,
        help='No use debug for output',
    )
    parser.add_option(
        '--gevent',
        dest='GEVENT',
        action='store_true',
        default=False,
        help='Use gevent wsgi server',
    )

    return parser


def main():
    parser = get_parser()
    options, _ = parser.parse_args()

    if options.GEVENT:
        from gevent.monkey import patch_all
        patch_all(thread=False)

    config = Config(
        host=options.HOST,
        port=options.PORT,
        debug=options.NO_DEBUG,
        gevent=options.GEVENT,
        path_to_mocks=options.PATH_TO_MOCKS,
        block_timeout=constants.DEFAULT_BLOCK_TIMEOUT,
    )

    server = MockServer(config)
    server.serve_forever()


if __name__ == '__main__':
    main()
