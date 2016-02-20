from jinja2 import Environment
from mock import Mock, patch
from nose.tools import eq_
from fleet.client.fleet_base import Provider
from fleet.deploy.deployer import _get_service_prefix, Deployment
from tests.helper import dict_compare


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


@patch('fleet.deploy.deployer.time')
def test_init_deployment(mock_time):
    """
    Should initialize deployment instance
    """
    # Given: Mock implementation for time
    mock_time.time.return_value = 0.12

    # When: I create a deployment instance
    deployment = Deployment(Mock(spec=Provider), Mock(spec=Environment),
                            'mock-app', template_args={
                                'arg-1': 'value1',
                                'arg_2': 'value2'})

    # Then: Deployment gets initialized as expected
    eq_(deployment.nodes, 1)
    eq_(deployment.version, '120')
    dict_compare(deployment.template_args, {
        'name': 'mock-app',
        'version': '120',
        'service_type': 'app',
        'arg_1': 'value1',
        'arg_2': 'value2'
    })
    eq_(deployment.service_name_prefix, 'mock-app-120-app')
    eq_(deployment.template_name, 'mock-app-120-app@.service')


def test_init_deployment_with_timer():
    """
    Should initialize deployment instance
    """

    # When: I create a deployment instance with timer
    deployment = Deployment(Mock(spec=Provider), Mock(spec=Environment),
                            'mock-app', timer=True,
                            service_type='timer')

    # Then: Service Type is initialized to app
    eq_(deployment.service_type, 'app')


@patch('fleet.deploy.deployer.time')
def test_init_timer_deployment(mock_time):
    """
    Should initialize deployment instance
    """
    # Given: Mock implementation for time
    mock_time.time.return_value = 0.12

    # When: I create a deployment instance
    deployment = Deployment(Mock(spec=Provider), Mock(spec=Environment),
                            'mock-app', template_args={
            'arg-1': 'value1',
            'arg_2': 'value2'}, timer=True)

    # Then: Deployment gets initialized as expected
    eq_(deployment.service_name_prefix, 'mock-app-120-app')
    eq_(deployment.template_name, 'mock-app-120-app@.timer')
