"""
Client module that allows you to create provider to connect to fleet.
"""
import importlib

__author__ = 'sukrit'
__all__ = ['get_provider']

_DEFAULT_PROVIDER = 'fabric'

_PROVIDER_DICT = {
    'fabric': 'fleet.client.fleet_fabric',
    'api': 'fleet.fleet_api'
}


def get_provider(provider_type=_DEFAULT_PROVIDER, **kwargs):
    """
    Gets provider for connecting to fleet.

    :param provider_type: Type of provider. (e.g. fabric)
    :type provider_type: str
    :param kwargs: Provider arguments
    :return: provider instance for connecting to fleet.
    """
    if provider_type in _PROVIDER_DICT:
        return importlib.import_module(_PROVIDER_DICT[provider_type])\
            .Provider(**kwargs)
    else:
        return None
