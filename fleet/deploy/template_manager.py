__author__ = 'sukrit'

from pkg_resources import resource_string


BUNDLED_TEMPLATE_PREFIX = "bundled://"
RAW_TEMPLATE_PREFIX = "raw://"


def fetch_template(template_url):

    if template_url.startswith('http://') or \
            template_url.startswith('https://'):
        pass

    if template_url.startswith(BUNDLED_TEMPLATE_PREFIX) and \
            len(template_url) > len(BUNDLED_TEMPLATE_PREFIX):
        template_file = template_url[len(BUNDLED_TEMPLATE_PREFIX):] +\
            ".service"
        template = resource_string(__name__, '../../templates/'+template_file)
        return template

    if template_url.startswith(RAW_TEMPLATE_PREFIX) and \
            len(template_url) > len(RAW_TEMPLATE_PREFIX):
        return template_url[len(RAW_TEMPLATE_PREFIX):]


def fetch_bundled_template_url(group='default', template_type='app'):
    template_url = '{}{}-{}'.format(BUNDLED_TEMPLATE_PREFIX, group,
                                    template_type)
    return template_url
