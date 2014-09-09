import fleet.client.fleet_fabric

__author__ = 'sukrit'
__all__ = ['get_provider','get_client','FleetClient']

_DEFAULT_PROVIDER = 'fabric'

_PROVIDER_DICT = {
    'fabric': fleet_fabric.Provider
}

def get_provider(provider_type=_DEFAULT_PROVIDER, **kwargs):
    if provider_type in _PROVIDER_DICT:
        return _PROVIDER_DICT[provider_type](**kwargs)
    else:
        return None

if __name__ == "__main__":
    client = get_provider(
        hosts='ec2-54-176-123-236.us-west-1.compute.amazonaws.com')
    print(client.client_version())
