from cStringIO import StringIO
from time import sleep

__author__ = 'sukrit'

import fleet.client as fleet_client
import  template_manager as tmgr

class Deployment:
    def __init__(self, **kwargs):
        template_group = kwargs.get('template_group', 'default')
        app_template_url = kwargs.get(
            'app_template_url', tmgr.fetch_bundled_template_url(
                group=template_group, type='app'))

        self.app_template = tmgr.fetch_template(app_template_url)
        self.image = kwargs['image']
        self.nodes = kwargs.get('nodes', 1)
        self.name = kwargs['name']
        self.version = kwargs['version']
        self.docker_args = kwargs.get('docker_args', '')
        self.docker_env = kwargs.get('docker_env', '')
        self.app_cmd = kwargs.get('app_cmd', '')
        self.template_args = kwargs.get('template_additional_vars',{})\
            .copy()
        self.template_args.setdefault('image', self.image)
        self.template_args.setdefault('name', self.name)
        self.template_args.setdefault('version', self.version)
        self.template_args.setdefault('docker_args', self.docker_args)
        self.template_args.setdefault('docker_env', self.docker_env)
        self.template_args.setdefault('app_cmd', self.app_cmd)
        self.logger_template = None
        self.register_template = None

        if kwargs.get('use_logger', True):
            logger_template_url = kwargs.get(
                'logger_template_url', tmgr.fetch_bundled_template_url(
                    group=template_group, type='logger'))
            self.logger_template = tmgr.fetch_template(logger_template_url)
        if kwargs.get('use_register', True):
            register_template_url = kwargs.get(
                'register_template_url', tmgr.fetch_bundled_template_url(
                    group=template_group, type='register'))
            self.register_template = tmgr.fetch_template(register_template_url)

    def _deploy(self, fleet_provider, template, service_name_prefix,
                force_remove=False):
        template_args = self.template_args.copy()
        for unit in range(1, self.nodes+1):
            template_args['unit'] = unit
            unit_data = template.format(**template_args)
            service_name = "{}-{}.service".format(service_name_prefix, unit)
            unit_stream = StringIO()
            unit_stream.write(unit_data)
            fleet_provider.deploy(service_name, unit_stream,
                                  force_remove=force_remove)

    def deploy_app(self, fleet_provider, force_remove=False):
        self._deploy(fleet_provider,
                     self.app_template,
                     "{}-{}".format(self.name, self.version),
                     force_remove=force_remove)

    def deploy_register(self, fleet_provider, force_remove=True):
        self._deploy(fleet_provider, self.register_template,
                     "{}-register-{}".format(self.name, self.version),
                     force_remove=force_remove)

    def deploy_logger(self, fleet_provider, force_remove=True):
        self._deploy(fleet_provider, self.logger_template,
                     "{}-logger-{}".format(self.name, self.version),
                     force_remove=force_remove)

    def deploy(self, fleet_provider):
        self.deploy_app(fleet_provider)
        if self.register_template:
            self.deploy_register(fleet_provider)
        if self.logger_template:
            self.deploy_logger(fleet_provider)


def deploy(fleet_provider, **kwargs):
    deployment = Deployment(**kwargs)
    deployment.deploy(fleet_provider)
    #Replace

def undeploy(fleet_provider, name, version, nodes):
    for unit in range(1, nodes+1):
        app_service = "{}-{}-{}.service".format(name, version, unit)
        register_service = "{}-register-{}-{}.service".format(
            name, version, unit)
        log_service = "{}-logger-{}-{}.service".format(name, version, unit)

        fleet_provider.destroy(app_service)
        fleet_provider.destroy(register_service)
        fleet_provider.destroy(log_service)

def app_status(fleet_provider, name, version, node_num):
    app_service = "{}-{}-{}.service".format(name, version, node_num)
    return fleet_provider.status(app_service)

def register_status(fleet_provider, name, version, node_num):
    register_service = "{}-register-{}-{}.service".format(
        name, version, node_num)
    return fleet_provider.status(register_service)

def logger_status(fleet_provider, name, version, node_num):
    log_service = "{}-logger-{}-{}.service".format(name, version, node_num)
    return fleet_provider.status(log_service)



if __name__ == "__main__":
    provider = fleet_client.get_provider(
        hosts='core@ec2-54-176-123-236.us-west-1.compute.amazonaws.com')

    num_nodes=3
    undeploy(provider,
             name='apache',
             version='a234wdsa34',
             nodes=num_nodes
    )

    #In SWF We will poll
    sleep(10)

    deploy(provider,
        image='coreos/apache',
        template_group='default',
        name='apache',
        version='a234wdsa34',
        use_logger=True,
        use_register=True,
        nodes = num_nodes,
        docker_args='-p :80',
        app_cmd='''/bin/bash -c \'echo \\"<h1>a234wdsa34</h1>\\" \\
            >/var/www/index.html &&\\
            /usr/sbin/apache2ctl -D FOREGROUND\'''' )

    sleep(10)

    print app_status(provider,
               name='apache',
               version='a234wdsa34',
               node_num=1
               )


    # num_nodes=3
    # undeploy(provider,
    #          name='spec-python-master',
    #          version='d0c5b0fc5ebe1f73d00e99b9b783054ac70a894e',
    #          nodes=num_nodes
    # )
    # sleep(10)
    # deploy(provider,
    #     image='quay.io/totem/totem-spec-python:d0c5b0fc5ebe1f73d00e99b9b783054ac70a894e',
    #     template_group='default',
    #     name='spec-python-master',
    #     version='d0c5b0fc5ebe1f73d00e99b9b783054ac70a894e',
    #     use_logger=True,
    #     use_register=True,
    #     nodes = num_nodes)



