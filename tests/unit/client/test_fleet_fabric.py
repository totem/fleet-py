from mock import patch

from fleet.client.fleet_fabric import Provider
from tests.helper import dict_compare
from nose.tools import eq_

__author__ = 'sukrit'


def _get_fleet_provider():
    return Provider()


@patch('fleet.client.fleet_fabric.run')
def test_fetch_units_matching_with_no_match(mock_run):
    """
    Should return empty list when there are no matching units found
    """
    # Given: Fleet provider
    provider = _get_fleet_provider()

    # And no existing units for given service prefix
    mock_run.return_value = ''

    # When: I try to fetch units with no matching unit
    units = list(provider.fetch_units_matching('non-existing-unit-'))

    # Then: Empty list is returned
    eq_(units, [])


@patch('fleet.client.fleet_fabric.run')
def test_fetch_units_matching_with_multiple_match(mock_run):
    """
    Should return empty list when there are no matching units found
    """
    # Given: Fleet provider
    provider = _get_fleet_provider()

    # And no existing units for given service prefix
    mock_run.return_value = '''cluster-deployer-develop-v1-app@1.service		442337f12da14ad7830cda843079730b/10.249.0.235	active	running
cluster-deployer-develop-v1-app@2.service		0a5239ec591e4981905c792e99341f03/10.229.23.106	activating	start-pre
invalidrow
    '''  # noqa

    # When: I try to fetch units with no matching unit
    units = list(provider.fetch_units_matching('cluster-deployer-develop-'))

    # Then: Empty list is returned
    eq_(len(units), 2, 'Expecting 2 units to be returned. Found: %d' %
        len(units))
    dict_compare(units[0], {
        'unit': 'cluster-deployer-develop-v1-app@1.service',
        'machine': '442337f12da14ad7830cda843079730b/10.249.0.235',
        'active': 'active',
        'sub': 'running'
    })
    dict_compare(units[1], {
        'unit': 'cluster-deployer-develop-v1-app@2.service',
        'machine': '0a5239ec591e4981905c792e99341f03/10.229.23.106',
        'active': 'activating',
        'sub': 'start-pre'
    })
