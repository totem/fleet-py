__author__ = 'sukrit'

from cStringIO import StringIO
import time

from jinja2 import Environment, FileSystemLoader, ChoiceLoader

from fleet.deploy.github_loader import GithubTemplateLoader


def default_jinja_environment(local_search_path=None):
    """
    Creates default jinja environment using FileSystemLoader and
    GithubTemplateLoader. Basically , it will try to locate the template in
    local file system first. If not found, it will try to find it in public
    github repository (https://github.com/totem/fleet-templates).

    :param local_search_path: Local path for searching the templates
    :type local_search_path: list or str
    :return: Jinja Environment
    :rtype: Environment
    """
    return Environment(
        loader=ChoiceLoader([
            FileSystemLoader(local_search_path or ['./templates']),
            GithubTemplateLoader()
        ]))


class Deployment:
    """
    Class for creating new deployment using Jinja templates

    :param fleet_provider: Fleet provider for connecting to fleet cluster.
    :param jinja_env: Jinja environment for loading Jinja templates.
    :param template: Template to be used for creating cluster deployment.
    :param name: Application name
    :param version: Application version
    :param nodes: No. of nodes to be created for the deployment.
    :param service_type: Type of service to be created. This is basically used
        for naming fleet services.
    :param template_args: Arguments to be passed to the jinja template for
        creating fleet unit files.
    """
    def __init__(self, fleet_provider, jinja_env, name,
                 template='default-app.service',
                 version=None, nodes=1, service_type='app',
                 template_args=None):
        self.fleet_provider = fleet_provider
        self.service_type = service_type
        self.nodes = nodes
        self.jinja_env = jinja_env
        self.name = name

        if not template.endswith('.service'):
            self.template = template + '.service'
        else:
            self.template = template
        # If version is not set, use current timestamp in ms.
        self.version = str(version) or str(int(round(time.time() * 1000)))
        self.template_args = template_args.copy() if template_args else {}
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
        self.fleet_provider.deploy_units(template_name, template_stream,
                                         units=self.nodes)

    def deploy(self):
        """
        Provisions the deployment
        :return: None
        """
        service_name_prefix = '{}-{}-{}'.format(
            self.name, self.version, self.service_type)
        self._deploy(service_name_prefix)


def undeploy(fleet_provider, name, version, service_type='app'):
    """
    Un-deploys the application from the fleet cluster.
    :param fleet_provider:
    :param name:
    :param version:
    :param service_type:
    :return:
    """
    service_prefix = "{}-{}-{}@".format(name, version, service_type)
    fleet_provider.destroy_units_matching(service_prefix)
    fleet_provider.destroy('{}.service'.format(service_prefix))


def status(fleet_provider, name, version, node_num, service_type='app'):
    """
    Gets the status for a node in cluster.
    :param fleet_provider:
    :param name:
    :param version:
    :param node_num:
    :param service_type:
    :return:
    """
    service = "{}-{}-{}@{}.service".format(
        name, version, service_type, node_num)
    fleet_provider.status(service)
