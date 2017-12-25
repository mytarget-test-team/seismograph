# -*- coding: utf-8 -*-

"""
To release library.

Usage:

    python to_release.py
"""

import os
import subprocess


GIT_BIN = 'git'
PYTHON_BIN = 'python'
FROM_BRANCH = '0.5.x'
PACKAGE_NAME = 'seismograph'

SELF_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
    ),
)

SUBPROCESS_OPTIONS = {
    'shell': True,
    'cwd': SELF_PATH,
}


def sudo(command):
    if os.getlogin() != 'root':
        return 'sudo {}'.format(command)
    return command


def python(command, env=None, version='2.7'):
    if env:
        env = ' '.join(
            '{}={}'.format(k, v) for k, v in env.items()
        ) + ' '
    else:
        env = ''

    return '{}{}{} {}'.format(env, PYTHON_BIN, version, command)


def git(command):
    return '{} {}'.format(GIT_BIN, command)


def call(command, **params):
    subprocess_options = SUBPROCESS_OPTIONS.copy()
    subprocess_options.update(params)
    return subprocess.call(command, **subprocess_options)


def check_output(command):
    return subprocess.check_output(command, **SUBPROCESS_OPTIONS)


def check_git_branch():
    command = git('branch')
    output = check_output(command)

    assert '* {}'.format(FROM_BRANCH) in output.split('\n'),\
        'Please check current git branch. Branch for build "{}"'.format(FROM_BRANCH)


def delete_old_files():
    command = sudo('rm -rf ./{}.egg-info ./dist/'.format(PACKAGE_NAME))
    call(command)


def run_example(pyv='2.7'):
    command = 'PYTHONPATH={} SEISMOGRAPH_CONF={} python{} -m seismograph {} -v -x'
    assert call(
        command.format(
            SELF_PATH, 'example.etc.base', pyv, os.path.join(SELF_PATH, 'example'),
        ),
    ) == 0, 'Example tests was worked with errors'


def run_tests(pyv='2.7'):
    command = sudo(python('setup.py test', version=pyv))
    assert call(command) == 0, 'Tests was worked with errors'


def upload_to_pip():
    command = sudo(python('setup.py sdist'))
    exit_code = call(command)

    if not exit_code:
        call('twine upload dist/*')

    assert exit_code == 0, 'Upload to pip error'


def rebuild_docs():
    exit_code = subprocess.call(
        'make html',
        shell=True,
        cwd=os.path.join(SELF_PATH, 'docs'),
    )

    assert exit_code == 0, 'Rebuild docs error'


def main():
    check_git_branch()
    delete_old_files()
    run_tests(pyv='2.7')
    run_tests(pyv='3.4')
    # run_example(pyv='2.7')
    # run_example(pyv='3.4')
    rebuild_docs()
    upload_to_pip()


if __name__ == '__main__':
    main()
