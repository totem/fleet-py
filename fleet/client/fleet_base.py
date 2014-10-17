__author__ = 'sukrit'


class Provider:
    """
    Base Provider class for API Client implementation.
    """

    def __init__(self, **kwargs):
        super(Provider, self).__init__()

    def client_version(self):
        raise NotImplementedError("Implementation coming soon...")

    def deploy_units(self, template_name, service_data_stream, units=1):
        """
        :param template_name: Template name must contain '@' param for
            deploying multiple instances
        :param service_data_stream: Stream cotaining template data
        :param units: No. of units to deploy
        :return: None
        """
        raise NotImplementedError("Implementation coming soon...")

    def deploy(self, service_name, service_data_stream, force_remove=False):
        raise NotImplementedError("Implementation coming soon...")

    def destroy_units_matching(self, service_prefix):
        raise NotImplementedError("Implementation coming soon...")

    def destroy(self, service):
        raise NotImplementedError("Implementation coming soon...")

    def status(self, service_name):
        raise NotImplementedError("Implementation coming soon...")
