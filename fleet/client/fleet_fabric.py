from io import BytesIO
__author__ = 'sukrit'

from fabric.api import run, settings, put, hide


import logging

import random

DEFAULT_FAB_SETTINGS = {
    'timeout': 10,
    'command_timeout': 60,
    'connection_attempts': 3,
    'disable_known_hosts': True,
    'abort_on_prompts': True,
    'abort_exception': None,
    'forward_agent': True,
    'colorize_errors': False,
    'user': 'core'
}

FLEETCTL_VERSION_CMD = 'fleetctl version'
FLEET_UPLOAD_DIR = '/tmp/services'

logger = logging.getLogger(__name__)


def _apply_defaults(fab_settings, default_settings=DEFAULT_FAB_SETTINGS):
    fab_settings = fab_settings or {}
    for key, value in default_settings.iteritems():
        fab_settings.setdefault(key, value)
    return fab_settings


class Provider:
    """
    Provider for fabric based implementation. Requires fabric : 1.10+
    """

    def __init__(self, hosts='core@172.17.42.1', **kwargs):
        fab_settings = kwargs.get('fab_settings', {})
        self.log_metadata = kwargs.get('meta_data', {})
        self.fab_settings = _apply_defaults(fab_settings)
        self.host = random.choice(hosts.split(','))

    def _settings(self, **additional_settings):
        additional_settings = additional_settings or {}
        additional_settings = _apply_defaults(
            additional_settings, self.fab_settings)
        return settings(hide('warnings'),
                        host_string=self.host,
                        **additional_settings)

    def _logger_stream(self):
        return LoggerStream(log_metadata=self.log_metadata)

    def client_version(self):
        with self._settings():
            version_string = run(FLEETCTL_VERSION_CMD)
            version_string = version_string.decode(encoding='UTF-8').strip()
            if version_string.startswith('{} '.format(FLEETCTL_VERSION_CMD)):
                return version_string.replace(
                    '{} '.format(FLEETCTL_VERSION_CMD), '')
            else:
                return None

    def deploy_units(self, template_name, service_data_stream, units=1):
        """
        :param template_name: Template name must contain '@' param for
            deploying multiple instances
        :param service_data_stream: Stream cotaining template data
        :param units: No. of units to deploy
        :return: None
        """

        destination_service = '{upload_dir}/{template_name}'. \
            format(template_name=template_name, upload_dir=FLEET_UPLOAD_DIR)
        with self._settings():
            try:
                with self._logger_stream() as stream:
                    run('mkdir -p {}'.format(FLEET_UPLOAD_DIR), stdout=stream,
                        stderr=stream)
                    put(service_data_stream, destination_service)

                    run('fleetctl submit {destination_service}'
                        .format(destination_service=destination_service),
                        stdout=stream, stderr=stream)
                    service = template_name.replace('@', '@{1..%d}' % units)
                    run('fleetctl start -no-block=true {service}'
                        .format(service=service),
                        stdout=stream, stderr=stream)
            finally:
                run('if [ -f {} ]; then echo rm {}; fi'
                    .format(destination_service, destination_service))

    def deploy(self, service_name, service_data_stream, force_remove=False):
        destination_service = '{upload_dir}/{service_name}'. \
            format(service_name=service_name, upload_dir=FLEET_UPLOAD_DIR)
        with self._settings():
            try:
                with self._logger_stream() as stream:
                    run('mkdir -p {}'.format(FLEET_UPLOAD_DIR), stdout=stream,
                        stderr=stream)
                    put(service_data_stream, destination_service)
                    if force_remove:
                        run('fleetctl destroy {destination_service}'
                            .format(destination_service=destination_service),
                            stdout=stream, stderr=stream)

                    run('fleetctl start -no-block {destination_service}'
                        .format(destination_service=destination_service),
                        stdout=stream, stderr=stream)
            finally:
                run('if [ -f {} ]; then echo {}; fi'
                    .format(destination_service, destination_service))

    def destroy_units_matching(self, service_prefix):
        with self._logger_stream() as stream:
            with self._settings():
                run('fleetctl list-unit-files | grep {} | '
                    'awk \'{{print $1}}\' | xargs fleetctl destroy'
                    .format(service_prefix), stdout=stream, stderr=stream)

    def destroy(self, service):
        with self._logger_stream() as stream:
            with self._settings():
                run('fleetctl destroy {}'.format(service), stdout=stream,
                    stderr=stream)

    def status(self, service_name):
        with self._logger_stream() as stream:
            with self._settings():
                return run('fleetctl list-units | grep {} | '
                           'awk \'{{{{print $4}}}}\''.format(service_name),
                           stdout=stream, stderr=stream)


class LoggerStream:
    def __init__(self, stream=None, log_metadata=None):
        self.stream = stream or BytesIO()
        self.log_metadata = log_metadata or {}

    def __enter__(self):
        return self.stream

    def __exit__(self, exc_type, value, traceback):
        logger.info(self.stream.getvalue(), extra=self.log_metadata)
