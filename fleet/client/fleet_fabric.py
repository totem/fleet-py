from io import BytesIO

from fleet.client import fleet_base


__author__ = 'sukrit'

from fabric.api import run, settings, put, hide


import logging
import time
import random

DEFAULT_FAB_SETTINGS = {
    'timeout': 30,
    'command_timeout': 180,
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


class Provider(fleet_base.Provider):
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

    def _fabric_wrapper(self):
        return FabricWrapper(log_metadata=self.log_metadata)

    def _fabric_error_wrapper(self):
        pass

    def client_version(self):
        with self._settings():
            with self._fabric_wrapper() as stream:
                try:
                    version_string = run(FLEETCTL_VERSION_CMD, stderr=stream)
                except SystemExit:
                    raise FleetExecutionException(
                        message='Failed to get fleet client version',
                        command_output=stream.getvalue())
                version_string = version_string.decode(encoding='UTF-8') \
                    .strip()
                if version_string.startswith('{} '.format(
                        FLEETCTL_VERSION_CMD)):
                    return version_string.replace(
                        '{} '.format(FLEETCTL_VERSION_CMD), '')
                else:
                    return None

    def deploy_units(self, template_name, service_data_stream, units=1,
                     start=True):
        """
        :param template_name: Template name must contain '@' param for
            deploying multiple instances
        :param service_data_stream: Stream cotaining template data
        :param units: No. of units to deploy. Defaults to 1. It is only needed
            when units needs to be started after install.
        :return: None
        """

        destination_service = '{upload_dir}/{template_name}'. \
            format(template_name=template_name, upload_dir=FLEET_UPLOAD_DIR)
        with self._settings():

            with self._fabric_wrapper() as stream:
                try:
                    run('mkdir -p {}'.format(FLEET_UPLOAD_DIR), stdout=stream,
                        stderr=stream)
                    put(service_data_stream, destination_service)

                    run('fleetctl submit {destination_service}'
                        .format(destination_service=destination_service),
                        stdout=stream, stderr=stream)
                    service = template_name.replace('@', '@{1..%d}'
                                                    % units)
                    run('fleetctl load  -no-block=true {service}'
                        .format(service=service), stdout=stream, stderr=stream)
                    # Sleep for sometime as we are using no-block
                    # In future we need to write a logic to ensure units have
                    # been loaded
                    time.sleep(2)
                    if start:
                        run('fleetctl start -no-block=true {service}'
                            .format(service=service),
                            stdout=stream, stderr=stream)
                except SystemExit:
                    raise FleetExecutionException(
                        message='Failed to deploy unit: %s' % template_name,
                        command_output=stream.getvalue())

    def start_units(self, template_name, units=1):
        """
        Starts units with given count for a given template.

        :param template_name: The template name for the unit.
            Note: It assumes that template_name is already installed.
            See: deploy_units for installing templates programtically.
        :param units: No. of units to deploy
        :return: None
        """
        with self._settings():

            with self._fabric_wrapper() as stream:
                try:
                    service = template_name.replace('@', '@{1..%d}'
                                                    % units)
                    run('fleetctl start -no-block=true {service}'
                        .format(service=service),
                        stdout=stream, stderr=stream)
                except SystemExit:
                    raise FleetExecutionException(
                        message='Failed to deploy unit: %s' % template_name,
                        command_output=stream.getvalue())

    def deploy(self, service_name, service_data_stream, force_remove=False):
        destination_service = '{upload_dir}/{service_name}'. \
            format(service_name=service_name, upload_dir=FLEET_UPLOAD_DIR)
        with self._settings():
            with self._fabric_wrapper() as stream:
                try:
                    run('mkdir -p {}'.format(FLEET_UPLOAD_DIR), stdout=stream,
                        stderr=stream)
                    put(service_data_stream, destination_service)
                    if force_remove:
                        run('fleetctl stop -no-block=true {}'.format(
                            destination_service), stdout=stream, stderr=stream,
                            warn_only=True)
                        run('fleetctl destroy {destination_service}'
                            .format(destination_service=destination_service),
                            stdout=stream, stderr=stream)

                    run('fleetctl start -no-block {destination_service}'
                        .format(destination_service=destination_service),
                        stdout=stream, stderr=stream)
                except SystemExit:
                    raise FleetExecutionException(
                        message='Failed to deploy service: %s' % service_name,
                        command_output=stream.getvalue())

    def destroy_units_matching(self, service_prefix, exclude_prefix=None):
        with self._fabric_wrapper() as stream:
            with self._settings():
                try:
                    exclude_prefix = exclude_prefix or '^$'
                    run('fleetctl list-units | grep \'%s\' | grep -v \'%s\' |'
                        ' awk \'{print $1}\' | '
                        'xargs fleetctl stop -no-block=true '
                        % (service_prefix, exclude_prefix), stdout=stream,
                        stderr=stream, warn_only=True)
                    # Sleep for couple of seconds to prevent timeout issue
                    # with fabric.
                    time.sleep(2)
                    run('fleetctl list-units | grep \'%s\' | grep -v \'%s\' |'
                        ' awk \'{print $1}\' | xargs fleetctl unload'
                        % (service_prefix, exclude_prefix), stdout=stream,
                        stderr=stream)
                    run('fleetctl list-unit-files | grep \'%s\' | '
                        'grep -v \'%s\' | awk \'{print $1}\' | '
                        'xargs fleetctl destroy'
                        % (service_prefix, exclude_prefix), stdout=stream,
                        stderr=stream)
                except SystemExit:
                    raise FleetExecutionException(
                        message='Failed to destroy units with prefix: %s '
                                'exclude prefix: %s'
                                % (service_prefix, exclude_prefix),
                        command_output=stream.getvalue())

    def fetch_units_matching(self, service_prefix, exclude_prefix=None):
        exclude_prefix = exclude_prefix or '^$'
        list_cmd = 'fleetctl list-units -no-legend ' \
            '-fields unit,machine,active,sub -full | ' \
            'grep \'{}\' | grep -v \'{}\''.format(
                service_prefix, exclude_prefix)
        with self._fabric_wrapper() as stream:
            with self._settings():
                try:
                    logger.info('fetch_units_matching: {}'.format(list_cmd))
                    units_raw = run(list_cmd, stdout=stream, stderr=stream,
                                    warn_only=True)

                    for line in units_raw.splitlines():
                        cols = line.split()
                        if not cols or len(cols) < 4:
                            continue
                        else:
                            yield {
                                'unit': cols[0],
                                'machine': cols[1],
                                'active': cols[2],
                                'sub': cols[3]
                            }

                except SystemExit:
                    raise FleetExecutionException(
                        message='Failed to Fetch units with prefix: %s'
                                % service_prefix,
                        command_output=stream.getvalue())

    def destroy(self, service):
        with self._fabric_wrapper() as stream:
            with self._settings():
                try:
                    run('fleetctl stop -no-block=true  {}'.format(service),
                        stdout=stream, stderr=stream, warn_only=False)
                    run('fleetctl destroy {}'.format(service), stdout=stream,
                        stderr=stream)
                except SystemExit:
                    raise FleetExecutionException(
                        message='Failed to destroy unit: %s'
                                % service,
                        command_output=stream.getvalue())

    def status(self, service_name):
        with self._fabric_wrapper() as stream:
            with self._settings():
                try:
                    return run('fleetctl list-units | grep {} | '
                               'awk \'{{{{print $4}}}}\''.format(service_name),
                               stdout=stream, stderr=stream)
                except SystemExit:
                    raise FleetExecutionException(
                        message='Failed to get status for unit: %s'
                                % service_name,
                        command_output=stream.getvalue())

    def stop_units_matching(self, service_prefix, exclude_prefix=None):
        exclude_prefix = exclude_prefix or '^$'
        stop_cmd = 'fleetctl list-units | grep \'%s\' | grep -v \'%s\' | ' \
            'awk \'{print $1}\' | ' \
            'xargs fleetctl stop -no-block=true ' % (
                service_prefix, exclude_prefix)
        with self._fabric_wrapper() as stream:
            with self._settings():
                try:
                    logger.info('stop_units_matching: {}'.format(stop_cmd))
                    run(stop_cmd, stdout=stream,
                        stderr=stream, warn_only=False)
                    # Sleep for couple of seconds to prevent timeout issue
                    # with fabric.
                    time.sleep(2)
                except SystemExit:
                    raise FleetExecutionException(
                        message='Failed to stop units with prefix: %s '
                                'exclude prefix: %s'
                                % (service_prefix, exclude_prefix),
                        command_output=stream.getvalue())


class FleetExecutionException(Exception):
    def __init__(self, message='One or more commands failed to get '
                               'executed on coreos cluster.',
                 command_output='', log_metadata=None):
        self.message = message
        self.command_output = command_output
        Exception.__init__(self, message, command_output, log_metadata)

    def __repr__(self):
        return 'FleetExecutionException: %s \noutput: %s' % \
               (self.message, self.command_output)

    def __str__(self):
        return self.__repr__()


class FabricWrapper:
    def __init__(self, stream=None, log_metadata=None):
        self.stream = stream or BytesIO()
        self.log_metadata = log_metadata or {}

    def __enter__(self):
        return self.stream

    def __exit__(self, exc_type, value, traceback):
        output = self.stream.getvalue()
        if isinstance(value, BaseException):
            logger.exception(value)
        else:
            logger.info(output, extra=self.log_metadata)
