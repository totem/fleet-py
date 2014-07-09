from cStringIO import StringIO

__author__ = 'sukrit'

import fleet.client as fleet_client

TEMPLATES = {
    "default_app":"""
[Unit]
Description={name}-{version}-{unit} Application

[Service]
Restart=always
RestartSec=20s
TimeoutStartSec=20m
ExecStartPre=/usr/bin/docker pull {image}
ExecStartPre=/bin/sh -c 'docker inspect {name}-{version} >/dev/null && \\
             docker rm -f {name}-{version} || true'
ExecStart=/bin/sh -c '/usr/bin/docker run --rm {docker_args} {docker_env} \\
          --name {name}-{version} {image} {app_cmd}'
ExecStop=/usr/bin/docker rm -f {name}-{version} > /dev/null || true

[X-Fleet]
X-Conflicts={name}-{version}-*.service
    """,



    "default_logger": """
[Unit]
Description={name}-{version}-{unit} Logger
BindsTo={name}-{version}-{unit}.service

[Service]
Restart=always
RestartSec=20s
ExecStartPre=/bin/sh -c "until docker inspect {name}-{version} >/dev/null 2>&1; do sleep 1; done"
ExecStart=/bin/sh -c "docker logs -f {name}-{version} 2>&1 | logger -p local0.info -t \\"{name} {version} {unit}\\" --udp --server $(etcdctl get /deis/logs/host | cut -d ':' -f1) --port $(etcdctl get /deis/logs/port | cut -d ':' -f2)"


[X-Fleet]
X-ConditionMachineOf={name}-{version}-{unit}.service
""",

    "default_register": """
[Unit]
Description={name}-{version}-{unit} Register
BindsTo={name}-{version}-{unit}.service

[Service]
EnvironmentFile=/etc/environment
Restart=always
RestartSec=20s

ExecStartPre=/bin/sh -c "until docker inspect -f '{{{{range $i, $e := .HostConfig.PortBindings }}}}{{{{$p := index $e 0}}}}{{{{$p.HostPort}}}}{{{{end}}}}' {name}-{version} >/dev/null 2>&1; \\
  do sleep 2; done; \\
  port=$(docker inspect -f '{{{{range $i, $e := .HostConfig.PortBindings }}}}{{{{$p := index $e 0}}}}{{{{$p.HostPort}}}}{{{{end}}}}' {name}-{version}); \\
  echo Waiting for $port/tcp...; until netstat -lnt | grep :$port >/dev/null; do sleep 1; done"
ExecStart=/bin/sh -c "port=$(docker inspect -f '{{{{range $i, $e := .HostConfig.PortBindings }}}}{{{{$p := index $e 0}}}}{{{{$p.HostPort}}}}{{{{end}}}}' {name}-{version}); echo Connected to $COREOS_PRIVATE_IPV4:$port/tcp, publishing to etcd...; while netstat -lnt | grep :$port >/dev/null; do etcdctl set /deis/services/{name}-{version}/{name}-{version}-{unit} $COREOS_PRIVATE_IPV4:$port --ttl 60 >/dev/null; sleep 45; done"
ExecStop=/usr/bin/etcdctl rm --recursive /deis/services/{name}-{version}/{name}-{version}-{unit}

[X-Fleet]
X-ConditionMachineOf={name}-{version}-{unit}.service
    """


}

class Deployment:
    def __init__(self, **kwargs):
        self.app_template = kwargs.get('app_template',
                                       TEMPLATES['default_app'])
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

        if kwargs.get('use_logger', True):
            self.log_template = kwargs.get('log_template',
                                           TEMPLATES['default_logger'])
        if kwargs.get('use_register', True):
            self.register_template = kwargs.get('register_template',
                                                TEMPLATES['default_register'])
    def _deploy(self, fleet_provider, template, service_name_prefix):
        template_args = self.template_args.copy()
        for unit in range(1, self.nodes+1):
            template_args['unit'] = unit
            unit_data = template.format(**template_args)
            service_name = "{}-{}".format(service_name_prefix, unit)
            unit_stream = StringIO()
            unit_stream.write(unit_data)
            fleet_provider.deploy(service_name, unit_stream)

    def deploy_app(self, fleet_provider):
        self._deploy(fleet_provider,
                     self.app_template,
                     "{}-{}".format(self.name, self.version))

    def deploy_register(self, fleet_provider):
        self._deploy(fleet_provider, self.register_template,
                     "{}-announce-{}".format(self.name, self.version))

    def deploy_logger(self, fleet_provider):
        self._deploy(fleet_provider, self.log_template,
                     "{}-logger-{}".format(self.name, self.version))

    def deploy(self, fleet_provider):
        self.deploy_app(fleet_provider)
        if self.register_template:
            self.deploy_register(fleet_provider)
        if self.log_template:
            self.deploy_logger(fleet_provider)


def deploy(fleet_provider, **kwargs):
    deployment = Deployment(**kwargs)
    deployment.deploy(fleet_provider)
    #Replace

if __name__ == "__main__":
    provider = fleet_client.get_provider(
        hosts='core@ec2-54-176-123-236.us-west-1.compute.amazonaws.com')

    deploy(provider,
        image='coreos/apache',
        name='apache',
        version='a234wdsa34',
        use_logger=True,
        use_register=True,
        nodes = 3,
        docker_args='-p :80',
        app_cmd='/bin/bash -c "echo \\\\"<h1>a234wdsa34</h1>\\\\" \
            >/var/www/index.html &&\
            /usr/sbin/apache2ctl -D FOREGROUND"' )