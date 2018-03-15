# -*- coding: utf-8 -*-

from __future__ import absolute_import

from seisma import Seisma

from ... import reason
from ...utils import pyv
from ... import layers as _layers


CONFIG_KEY = 'SEISMA_EX'

DEFAULT_JOB_NAME = 'seismograph'
DEFAULT_JOB_TITLE = 'Testing with seismograph library'


def _get_doc_from_object(obj):
    doc = getattr(obj, '__doc__', None)

    if doc:
        if pyv.IS_PYTHON_2:
            return doc.decode('utf-8').strip()
        return doc.strip()

    return None


def _get_client_kwargs_from_config(config):
    params = config.get(CONFIG_KEY, {})

    base_url = config.SEISMA_URL or params.get('URL')
    assert base_url, '"URL" to seisma is not configured'

    job_name = params.get('JOB_NAME', DEFAULT_JOB_NAME)
    job_title = params.get('JOB_TITLE', DEFAULT_JOB_TITLE)

    build_title = config.SEISMA_BUILD_TITLE or params.get('BUILD_TITLE')

    api_version = params.get('API_VERSION')
    build_name = config.SEISMA_BUILD_NAME or params.get('BUILD_NAME')
    build_metadata = params.get('BUILD_METADATA')

    return {
        'base_url': base_url,
        'job_name': job_name,
        'job_title': job_title,
        'build_name': build_name,
        'build_title': build_title,
        'api_version': api_version,
        'build_metadata': build_metadata,
    }


def _get_reason(obj, tb):
    return reason.format_reason(
        reason.create(
            obj, tb, config=obj.config,
        ),
    )


def _get_case_name(case):
    return '{}:{}'.format(
        case.__mount_data__.suite_name,
        case.__class__.__name__
    )


class SeismaProgramLayer(_layers.ProgramLayer):

    client = None

    def on_init(self, program):
        if program.config.SEISMA:
            self.client = Seisma(
                **_get_client_kwargs_from_config(program.config)
            )
        else:
            self.enabled = False

    def on_setup(self, program):
        if not self.client.job_exists():
            kwargs = {}
            doc = _get_doc_from_object(program)

            if doc:
                kwargs['description'] = doc

            self.client.create_job(**kwargs)

        self.client.start_build()

    def on_teardown(self, program):
        kwargs = {
            'runtime': program.result.current_state.runtime,
            'tests_count': program.result.current_state.tests,
            'error_count': program.result.current_state.errors,
            'fail_count': program.result.current_state.failures,
            'was_success': program.result.current_state.was_success,
            'success_count': program.result.current_state.successes,
        }

        self.client.stop_build(**kwargs)


class SeismaCaseLayer(_layers.CaseLayer):

    client = None

    def on_init(self, case):
        if case.config.SEISMA:
            self.client = Seisma(
                **_get_client_kwargs_from_config(case.config)
            )
        else:
            self.enabled = False

    def on_setup(self, case):
        case_name = _get_case_name(case)

        if not self.client.case_exists_on_job(case_name):
            kwargs = {
                'name': case_name,
            }
            doc = _get_doc_from_object(case)

            if doc:
                kwargs['description'] = doc

            self.client.add_case_to_job(**kwargs)

    def on_success(self, case, timer):
        kwargs = {
            'name': _get_case_name(case),
            'status': 'passed',
            'runtime': timer(),
        }
        metadata = getattr(case, 'metadata', None)

        if isinstance(metadata, dict):
            kwargs['metadata'] = metadata

        self.client.add_case_result(**kwargs)

    def on_fail(self, fail, case, result, tb, timer):
        kwargs = {
            'name': _get_case_name(case),
            'status': 'failed',
            'runtime': timer(),
            'reason': _get_reason(case, tb),
        }
        metadata = getattr(case, 'metadata', None)

        if isinstance(metadata, dict):
            kwargs['metadata'] = metadata

        self.client.add_case_result(**kwargs)

    def on_any_error(self, error, case, result, tb, timer):
        kwargs = {
            'name': _get_case_name(case),
            'status': 'error',
            'runtime': timer(),
            'reason': _get_reason(case, tb),
        }
        metadata = getattr(case, 'metadata', None)

        if isinstance(metadata, dict):
            kwargs['metadata'] = metadata

        self.client.add_case_result(**kwargs)

    def on_skip(self, case, reason, result):
        # If case was skipped and not created
        # for seisma server we should create
        # it because 404 otherwise
        self.on_setup(case)

        params = {
            'name': _get_case_name(case),
            'status': 'skipped',
            'runtime': 0.0,
            'reason': reason,
        }
        metadata = getattr(case, 'metadata', None)

        if isinstance(metadata, dict):
            params['metadata'] = metadata

        self.client.add_case_result(**params)
