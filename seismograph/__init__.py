# -*- coding: utf-8 -*-

"""
A powerful, extensible and easy to use framework for test development

By Trifonov Mikhail

For support, use the https://github.com/trifonovmixail/seismograph/issues tracker
"""

from .case import skip
from .case import Case
from .case import flows
from .case import skip_if
from .case import assertion
from .case import CaseLayer
from .case import skip_unless
from .case import AssertionBase

from .suite import Suite
from .suite import SuiteLayer

from .script import Script
from .script import AfterScript
from .script import BeforeScript

from .program import main
from .program import Program
from .program import ProgramLayer

from .config import get_config_path_by_env

from .steps import step

from .datastructures import Context


__version__ = '0.2.6'


__all__ = (
    'main',
    'skip',
    'step',
    'Case',
    'flows',
    'Suite',
    'skip_if',
    'Context',
    'Program',
    'assertion',
    'CaseLayer',
    'SuiteLayer',
    'AfterScript',
    'skip_unless',
    'ProgramLayer',
    'BeforeScript',
    'AssertionBase',
    'get_config_path_by_env',
)


from .utils.pyv import check_py_version

check_py_version()

del check_py_version
