# -*- coding: utf8 -*-

import sys
from warnings import warn

from .utils import pyv


def _print_line(string, spaces=0):
    sys.stdout.write('| {}{}\n'.format(_get_spaces(spaces), string))


def _print_total_info(suites, cases, methods):
    info = 'suites={} cases={} tests={}'.format(
        suites, cases, methods,
    )

    sys.stdout.write(
        '\n{}\n'.format(
            ''.join('-' for _ in pyv.xrange(len(info))),
        ),
    )
    sys.stdout.write(info)
    sys.stdout.write('\n')


def _get_spaces(num):
    return ''.join(' ' for _ in pyv.xrange(num))


def _li(string):
    return '\_ * {}'.format(string)


def _doc(string, is_end):
    return '| - {}{}'.format(string, '...' if is_end else '')


def print_tree(suites, show_docs=True, doc_lines=1, exit=True):
    case_counter = 0
    suite_counter = 0
    method_counter = 0
    suite_names = set()

    suites = list(suites)
    suites.sort(key=lambda s: s.name)

    # Suites
    for suite in suites:
        suite_counter += 1
        suite_name = suite.name

        if suite_name in suite_names:
            warn(
                'Duplicate suite name "{}"'.format(
                    suite_name,
                ),
                RuntimeWarning,
            )
        suite_names.add(suite_name)

        _print_line('* {}'.format(suite_name))

        mp = suite.get_map()

        # Cases
        for cls_name in mp:
            case_counter += 1

            _print_line(
                _li(
                    '{case} ({suite}:{case})'.format(
                        case=cls_name,
                        suite=suite_name,
                    ),
                ),
                spaces=2,
            )

            if show_docs:
                cls_doc = mp[cls_name]['cls'].__doc__

                if cls_doc:
                    line_counter = 0

                    for line in cls_doc.splitlines():
                        line = line.strip()

                        if line:
                            is_end = line_counter == doc_lines - 1

                            _print_line(_doc(line, is_end), spaces=4)

                            line_counter += 1

                            if is_end:
                                break

            if len(mp[cls_name]['tests']) == 1:
                method_counter += 1
                continue

            # Tests
            for test_method in mp[cls_name]['tests']:
                method_counter += 1

                _print_line(
                    _li(
                        '{test} ({suite}:{case}.{test})'.format(
                            test=test_method,
                            case=cls_name,
                            suite=suite_name,
                        ),
                    ),
                    spaces=4,
                )

                if show_docs:
                    method_doc = mp[cls_name]['tests'][test_method].__doc__

                    if method_doc:
                        line_counter = 0

                        for line in method_doc.splitlines():
                            line = line.strip()

                            if line:
                                is_end = line_counter == doc_lines - 1

                                _print_line(_doc(line, is_end), spaces=6)

                                line_counter += 1

                                if is_end:
                                    break

    _print_total_info(suite_counter, case_counter, method_counter)

    if exit:
        sys.exit(0)
