# -*- coding: utf-8 -*-

import logging


logger = logging.getLogger(__name__)


TO_INIT = []


try:
    from . import mocker
    TO_INIT.append(mocker)
except ImportError:
    pass

try:
    from . import alchemy
    TO_INIT.append(alchemy)
except ImportError:
    pass

try:
    from . import selenium
    TO_INIT.append(selenium)
except ImportError:
    pass


logger.debug('Available extensions: {}'.format(TO_INIT))
