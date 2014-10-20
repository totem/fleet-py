from nose.tools import eq_
from fleet.deploy.deployer import _get_service_prefix


def test_get_service_name_prefix_for_all_versions():
    """
    Should get service name prefix for all versions
    """

    # When: I get service name prefix for all version
    service_prefix = _get_service_prefix('test', None, None)

    # Then: Expected value for service prefix is returned
    eq_(service_prefix, 'test-')


def test_get_service_name_prefix_for_given_version():
    """
    Should get service name prefix for given version
    """

    # When: I get service name prefix for all version
    service_prefix = _get_service_prefix('test', 'v1', None)

    # Then: Expected value for service prefix is returned
    eq_(service_prefix, 'test-v1-')


def test_get_service_name_prefix_for_given_type():
    """
    Should get service name prefix for given version
    """

    # When: I get service name prefix for all version
    service_prefix = _get_service_prefix('test', 'v1', 'app')

    # Then: Expected value for service prefix is returned
    eq_(service_prefix, 'test-v1-app@')
