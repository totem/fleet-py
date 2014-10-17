"""
Provides ability to connect to fleet using API. This is just a place holder
with no implementation
"""
from fleet.client import fleet_base


class Provider(fleet_base.Provider):
    """
    Provider class for API Client implementation.
    """

    def __init__(self, base_url='http://172.17.42.1:5000', **kwargs):
        self.base_url = base_url
