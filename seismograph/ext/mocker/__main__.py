# -*- coding: utf-8 -*-

from optparse import OptionParser


DEFAULT_PORT = 5000
DEFAULT_HOST = '127.0.0.1'


def get_parser():
    parser = OptionParser('python -m seismograph.ext.mock_server [options]')

    parser.add_option(
        '-p', '--port',
        type=int,
        dest='PORT',
        default=DEFAULT_PORT,
        help='Server port'
    )
    parser.add_option(
        '-i', '--host',
        dest='HOST',
        default=DEFAULT_HOST,
        help='Server host'
    )
    parser.add_option(
        '-m', '--mocks-dir',
        dest='MOCKS_DIR',
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
        '--multiprocessing',
        dest='MULTIPROCESSING',
        action='store_true',
        default=False,
        help='Use fork server',
    )
    parser.add_option(
        '--threading',
        dest='THREADING',
        action='store_true',
        default=False,
        help='Use thread server',
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
        from seismograph.utils import pyv
        pyv.check_gevent_supported()

        from gevent.monkey import patch_all
        patch_all(thread=False)

    from seismograph.ext.mocker import SERVER_TYPES

    try:
        mock_server_class = SERVER_TYPES[options.SERVER_TYPE]
    except KeyError:
        raise ValueError('Incorrect server type')

    server = mock_server_class(
        options.MOCKS_DIR,
        host=options.HOST,
        port=options.PORT,
        debug=options.NO_DEBUG,
        gevent=options.GEVENT,
        threading=options.THREADING,
        multiprocessing=options.MULTIPROCESSING,
    )
    server.serve_forever()


if __name__ == '__main__':
    main()
