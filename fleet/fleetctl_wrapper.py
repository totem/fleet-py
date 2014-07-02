__author__ = 'sukrit'

import subprocess
from distutils.version import LooseVersion, StrictVersion

DEFAULT_TIMEOUT=60
MINIMUM_SUPPORTED_VERSION='0.6.0'


class Provider:

    def __init__(self, fleetctl_cmd=None,timeout=DEFAULT_TIMEOUT):
        self.fleetctl_cmd= fleetctl_cmd or 'fleetctl'
        self.timeout = timeout

    def client_version(self):
        version_string = subprocess.check_output(
            [self.fleetctl_cmd,'--version'], timeout=self.timeout) \
            .decode(encoding='UTF-8').strip()
        if version_string.startswith('fleetctl version '):
            return version_string.replace('fleetctl version ','')
        else:
            None

    def verify(self):
        version = self.client_version()
        if LooseVersion(version) < LooseVersion(MINIMUM_SUPPORTED_VERSION):
            raise RuntimeError("Fleetctl version:{} is not supported"
                               .format(version))


if __name__ == "__main__":
    pass