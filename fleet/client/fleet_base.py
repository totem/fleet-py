__author__ = 'sukrit'


class Provider:
    """
    Base Provider class for API Client implementation.
    """

    def __init__(self, **kwargs):
        super(Provider, self).__init__()

    def not_supported(self):
        """
        Raises NotImplementedError with a message
        :return:
        """
        raise NotImplementedError(
            'Provider: {} does not support this operation'
            .format(self.__class__))

    def client_version(self):
        raise NotImplementedError("Implementation coming soon...")

    def deploy_units(self, template_name, service_data_stream, units=1,
                     start=True):
        """
        :param template_name: Template name must contain '@' param for
            deploying multiple instances
        :param service_data_stream: Stream cotaining template data
        :param units: No. of units to deploy
        :return: None
        """
        self.not_supported()

    def start_units(self, template_name, units=1):
        """
        Starts units with given count for a given template.

        :param template_name: The template name for the unit.
            Note: It assumes that template_name is already installed.
            See: deploy_units for installing templates programatically.
        :param units: No. of units to deploy
        :return: None
        """
        self.not_supported()

    def deploy(self, service_name, service_data_stream, force_remove=False):
        self.not_supported()

    def destroy_units_matching(self, service_prefix, exclude_prefix=None):
        """
        Destroys unit matching the given prefix.
        :param service_prefix: Units with given prefix that needs to be
            destriyrf
        :type service_prefix: str
        :param exclude_prefix: Units with specified prefix should be excluded
            from beiing stopped
        :type exclude_prefix: str
        :return: None
        """
        self.not_supported()

    def destroy(self, service):
        self.not_supported()

    def status(self, service_name):
        self.not_supported()

    def stop_units_matching(self, service_prefix, exclude_prefix=None):
        """
        Stops unit matching the given prefix.
        :param service_prefix: Units with given prefix that needs to be stopped
        :type service_prefix: str
        :param exclude_prefix: Units with specified prefix should be excluded
            from beiing stopped
        :type exclude_prefix: str
        :return: None
        """
        self.not_supported()

    def fetch_units_matching(self, service_prefix, exclude_prefix=None):
        """
        Fetch units matching prefix.

        :param service_prefix:
        :type service_prefix: str
        :keyword exclude_prefix: Units with specified prefix should be excluded
            from fetch list
        :type exclude_prefix: str
        :return: list of units where each unit is represented as dict
            comprising of
                - unit : Name of fleet unit,
                - machine : Machine for the unit
                - active : Activation status ('activating', 'active')
                - sub : Current state of the unit
        """
        self.not_supported()
