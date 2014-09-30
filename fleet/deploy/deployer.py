from cStringIO import StringIO
from jinja2 import Environment, PrefixLoader, FileSystemLoader, ChoiceLoader
import time
from fleet.client import get_provider
from fleet.deploy.github_loader import GithubTemplateLoader

__author__ = 'sukrit'

import template_manager as tmgr


def default_jinja_environment(local_search_path=['./templates']):
    """
    Creates default environment using github template loader.
    :param github_token: Github token for connecting to private repositories.
        Use none for connecting to public repositories only.
    :return:
    """
    return Environment(
        loader=ChoiceLoader([
            FileSystemLoader(local_search_path),
            GithubTemplateLoader()
        ]))


class Deployment:
    """
    Class for creating new deployment using Jinja templates
    """
    def __init__(self, fleet_provider, jinja_env, template, name,
                 version=None, nodes=1, service_type='app', template_args={}):
        self.fleet_provider = fleet_provider
        self.service_type = service_type
        self.nodes = nodes
        self.jinja_env = jinja_env
        self.name = name
        self.template = template
        self.version = str(version) or str(int(round(time.time() * 1000)))
        self.template_args = template_args.copy()
        self.template_args.setdefault('name', self.name)
        self.template_args.setdefault('version', self.version)
        self.template_args.setdefault('service_type', self.service_type)

    def _deploy(self, service_name_prefix):
        template_args = self.template_args.copy()
        template_name = '{}@.service'.format(service_name_prefix)
        template_data = self.jinja_env.get_template(self.template)\
            .render(template_args)
        template_stream = StringIO()
        template_stream.write(template_data)
        print(template_data)
        self.fleet_provider.deploy_units(template_name, template_stream,
                                         units=self.nodes)

    def deploy(self):
        """
        Provisions the deployment
        :return: None
        """
        if self.service_type == 'app':
            service_name_prefix = '{}-{}'.format(self.name, self.version)
        else:
            service_name_prefix = '{}-{}-{}'.format(
                self.name, self.service_type, self.version)
        self._deploy(service_name_prefix)


def undeploy(fleet_provider, name, version, service_type='app'):
    if service_type == 'app':
        service_prefix = "{}-{}@".format(name, version)
    else:
        service_prefix = "{}-{}-{}@".format(name, service_type, version)
    fleet_provider.destroy_units_matching(service_prefix)
    fleet_provider.destroy('{}.service'.format(service_prefix))


def status(fleet_provider, name, version, node_num, service_type='app'):
    if service_type == 'app':
        service = "{}-{}@{}.service".format(name, version, node_num)
    else:
        service = "{}-{}-{}@{}.service".format(
            name, service_type, version, node_num)
    fleet_provider.status(service)

if __name__ == '__main__':
    provider = get_provider(
        hosts='core@east.th.melt.sh')

    jinja_env = default_jinja_environment(
        local_search_path=['/home/sukrit/git/fleet-templates/templates1'])

    deployment = Deployment(
        fleet_provider=provider,
        jinja_env=jinja_env,
        template='default-app.service',
        template_args={
            'image': 'quay.io/totem/totem-spec-python:'
                     '892d0d662a70fa2f198037fc18e742a927f8e4cf',
            },
        name='totem-spec-python',
        version='1412033793605',
        nodes=2,
        service_type='app')

    undeploy(fleet_provider=provider, name=deployment.name,
             version=deployment.version, service_type='app')

    deployment.deploy()
    #deployment.deploy()


