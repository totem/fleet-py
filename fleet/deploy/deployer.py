__author__ = 'sukrit'

from cStringIO import StringIO
import time

from jinja2 import Environment, FileSystemLoader, ChoiceLoader

from fleet.deploy.github_loader import GithubTemplateLoader


def default_jinja_environment(local_search_path=None, owner='totem',
                              repo='fleet-templates', path='templates',
                              ref='master', token=None):
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
            GithubTemplateLoader(owner=owner, repo=repo, path=path,
                                 ref=ref, token=token)
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
        self.version = str(version) if version else \
            str(int(round(time.time() * 1000)))
        self.template_args = template_args.copy() if template_args else {}
        self.template_args.setdefault('name', self.name)
        self.template_args.setdefault('version', self.version)
        self.template_args.setdefault('service_type', self.service_type)
        self.service_name_prefix = '{}-{}-{}'.format(
            self.name, self.version, self.service_type)
        self.template_name = '{}@.service'.format(self.service_name_prefix)

    def deploy(self, start=True):
        """
        Provisions the deployment
        :return: None
        """
        template_args = self.template_args.copy()
        template_data = self.jinja_env.get_template(self.template) \
            .render(template_args)
        template_stream = StringIO()
        template_stream.write(template_data)
        self.fleet_provider.deploy_units(self.template_name, template_stream,
                                         start=start)

    def start_units(self):
        """
        Starts units specified with the current deployment.
        """
        self.fleet_provider.start_units(self.template_args, units=self.nodes)


def _get_service_prefix(name, version, service_type):
    """
    Gets the service prefix

    :param name: Name of the application
    :type name: str
    :param version: Version of the application. If none, all versions are
        undeployed.
    :type version: str
    :param service_type: Service type (e.g. 'app', 'logger' etc)
    :type service_type: str
    :return: Service Prefix
    :rtype: str
    """
    if not version and not service_type:
        return '%s-' % name
    elif not service_type:
        return '%s-%s-' % (name, version)
    else:
        return '%s-%s-%s@' % (name, version, service_type)


def undeploy(fleet_provider, name, version=None, exclude_version=None,
             service_type=None):
    """
    Un-deploys the application from the fleet cluster.

    :param fleet_provider: Fleet provider for connecting to fleet cluster.
    :type fleet_provider: fleet.client.fleet_base.Provider
    :param name: Name of the application
    :type name: str
    :param version: Version of the application. If none, all versions are
        undeployed.
    :type version: str
    :param service_type: Service type (e.g. 'app', 'logger' etc)
    :type service_type: str
    :return: List of fleet units (dict)
    :rtype: list
    """

    service_prefix = _get_service_prefix(name, version, service_type)
    exclude_prefix = _get_service_prefix(
        name, exclude_version, service_type) if exclude_version else None
    fleet_provider.destroy_units_matching(service_prefix, exclude_prefix)


def filter_units(fleet_provider, name, version=None, service_type=None):
    """
    Filters unit with given name and option version and service type.
    :param fleet_provider:
    :param name:
    :param version:
    :param service_type:
    :return:
    """
    service_prefix = _get_service_prefix(name, version, service_type)
    return fleet_provider.fetch_units_matching(service_prefix)


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
    return fleet_provider.status(service)
