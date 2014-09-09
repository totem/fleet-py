from cStringIO import StringIO
from time import sleep

__author__ = 'sukrit'

import fleet.client as fleet_client
import template_manager as tmgr


class Deployment:
    """
    Class for creating new docker deployment in fleet. If a template does not
    require docker , it can also run a simple command as specified in
    template
    """
    def __init__(self, fleet_provider, **kwargs):
        self.fleet_provider = fleet_provider
        self.service_type = kwargs.get('service_type', 'app')
        template_group = kwargs.get('template_group', 'default')
        template_url = kwargs.get(
            'template_url', tmgr.fetch_bundled_template_url(
                group=template_group, type=self.service_type))

        self.template = tmgr.fetch_template(template_url)
        self.image = kwargs.get('image', None)
        self.nodes = kwargs.get('nodes', 1)
        self.name = kwargs['name']
        self.version = kwargs['version']
        self.docker_args = kwargs.get('docker_args', '')
        self.docker_env = kwargs.get('docker_env', '')
        self.docker_cmd = kwargs.get('docker_cmd', '')
        self.template_args = kwargs.get('template_additional_vars',{})\
            .copy()
        self.template_args.setdefault('image', self.image)
        self.template_args.setdefault('name', self.name)
        self.template_args.setdefault('version', self.version)
        self.template_args.setdefault('docker_args', self.docker_args)
        self.template_args.setdefault('docker_env', self.docker_env)
        self.template_args.setdefault('docker_cmd', self.docker_cmd)
        self.template_args.setdefault('service_type', self.service_type)

    def _deploy(self, service_name_prefix):
        template_args = self.template_args.copy()
        template_name = "{}@.service".format(service_name_prefix)
        template_data = self.template.format(**template_args)
        template_stream = StringIO()
        template_stream.write(template_data)
        self.fleet_provider.deploy_units(template_name, template_stream,
                                         units=self.nodes)

    def deploy(self):
        if self.service_type == 'app':
            service_name_prefix = '{}-{}'.format(self.name, self.version)
        else :
            service_name_prefix = '{}-{}-{}'.format(
                self.name, self.service_type, self.version)
        self._deploy(service_name_prefix)


def deploy(fleet_provider, **kwargs):
    deployment = Deployment(fleet_provider, **kwargs)
    deployment.deploy()
    #Replace


def undeploy(fleet_provider, name, version, service_type='app'):
    if service_type == 'app':
        service_prefix = "{}-{}@".format(name, version)
    else:
        service_prefix = "{}-{}-{}@".format(name, service_type, version)
    fleet_provider.destroy(service_prefix)


def status(fleet_provider, name, version, node_num, service_type='app'):
    if service_type == 'app':
        service = "{}-{}@{}.service".format(name, version, node_num)
    else:
        service = "{}-{}-{}@{}.service".format(
            name, service_type, version, node_num)
    fleet_provider.status(service)