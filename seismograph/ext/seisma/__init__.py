# -*- coding: utf-8 -*-

from optparse import OptionGroup

from .layers import SeismaCaseLayer
from .layers import SeismaProgramLayer


__all__ = (
    'SeismaCaseLayer',
    'SeismaProgramLayer',
)


def __add_options__(parser):
    group = OptionGroup(parser, 'Seisma extension options')

    group.add_option(
        '--seisma',
        dest='SEISMA',
        action='store_true',
        default=False,
        help='Use aggregation analytics to seisma.'
    )
    group.add_option(
        '--seisma-url',
        dest='SEISMA_URL',
        default=None,
        help='Base URL to seisma.',
    )
    group.add_option(
        '--seisma-build-name',
        dest='SEISMA_BUILD_NAME',
        default=None,
        help='Unique build name.',
    )
    group.add_option(
        '--seisma-build-title',
        dest='SEISMA_BUILD_TITLE',
        default=None,
        help='Title of build.',
    )

    parser.add_option_group(group)


def __install__(program):
    if program.config.SEISMA:
        from seismograph import case as c
        from seismograph import program as p

        c.DEFAULT_LAYERS.append(
            SeismaCaseLayer(),
        )
        p.DEFAULT_LAYERS.append(
            SeismaProgramLayer(),
        )
