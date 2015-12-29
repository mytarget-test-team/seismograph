# -*- coding: utf-8 -*-

"""
Usage:
    python -m seismograph <suites path> [options]
"""

import sys
from importlib import import_module


def apply_gevent_patch():
    try:
        from gevent.monkey import patch_all
    except ImportError as e:
        from seismograph.utils import pyv
        pyv.check_gevent_supported()
        raise e

    patch_all()


def get_suites_path():
    try:
        suites_path = sys.argv[1]
        if not suites_path.startswith('-'):
            sys.argv.remove(suites_path)
            return suites_path
    except IndexError:
        pass
    return None


def get_user_main():
    try:
        main_path = sys.argv[1]
        if not main_path.startswith('-') and ':' in main_path:
            import_path, function_name = main_path.split(':')
            user_main = getattr(import_module(import_path), function_name)
            sys.argv.remove(main_path)
            return user_main
    except IndexError:
        pass
    return None


def main():
    user_main = get_user_main()

    if not user_main and '--gevent' in sys.argv:
        apply_gevent_patch()

    if user_main:
        user_main()
    else:
        import seismograph

        seismograph.main(suites_path=get_suites_path())


if __name__ == '__main__':
    main()
