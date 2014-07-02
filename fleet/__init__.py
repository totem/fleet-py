import fleetctl_wrapper as fleetctl

__author__ = 'sukrit'
__all__ = ['get_provider','get_client','FleetClient']

DEFAULT_PROVIDER = 'fleetctl'

PROVIDER_DICT = {
    'fleetctl': fleetctl.Provider
}

def get_provider(type=DEFAULT_PROVIDER, *args, **kwargs):
    if type in PROVIDER_DICT:
        return PROVIDER_DICT[type](*args, **kwargs)
    else:
        return None

def get_client(provider=None):
    return FleetClient(provider)

class FleetClient:
    def __init__(self,provider=None):
        self.provider = provider or get_provider()

    def verify(self):
        return self.provider.verify()

    def get_version(self):
        return self.provider.client_version()

if __name__ == "__main__":
    client = get_client()
    print(client.get_version())
