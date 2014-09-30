from jinja2 import BaseLoader, TemplateNotFound, Environment, PrefixLoader, \
    ChoiceLoader
import requests

import base64


class InvalidCredentials(Exception):
    pass


class GithubTemplateLoader(BaseLoader):
    """
    Jinja2 template loader using github API.
    """

    def __init__(self, owner='totem', repo='fleet-templates', path='templates',
                 ref='master', token=None):
        """
        Constructor
        :param token: Option token used for connecting to repositories. If None
            no token will be passed.
        :type token: str
        """
        self.token = token
        self.owner = owner
        self.repo = repo
        self.path = path
        self.ref = ref
        self.auth = (self.token, 'x-oauth-basic') if self.token else None

    def _github_fetch(self, name):
        path_params = {
            'owner': self.owner,
            'repo': self.repo,
            'path': '%s/%s' % (self.path, name)
        }
        query_params = {
            'ref': self.ref
        }
        resp = requests.get(
            'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
            .format(**path_params), params=query_params, auth=self.auth)
        if resp.status_code == 404:
            raise TemplateNotFound(name)
        elif resp.status_code == 401:
            raise InvalidCredentials()
        elif resp.status_code != 200:
            raise RuntimeError('Unknown exception happened while '
                               'calling github. Message: %s' % resp.text)
        return resp.json()

    def _github_sha(self, name):
        path_params = {
            'owner': self.owner,
            'repo': self.repo,
        }
        query_params = {
            'path': '%s/%s' % (self.path, name),
            'sha': self.ref
        }
        resp = requests.get(
            'https://api.github.com/repos/{owner}/{repo}/commits'
            .format(**path_params), params=query_params, auth=self.auth)
        if resp.status_code != 200:
            return None
        else:
            commits = resp.json()
            return commits[0][u'sha'] if len(commits) > 0 else None

    def get_source(self, environment, name):
        sha = self._github_sha(name)
        github_data = self._github_fetch(name)
        contents = base64.decodestring(github_data[u'content'])

        def uptodate():
            return sha == self._github_sha(name)
        return contents, None, uptodate


if __name__ == "__main__":
    env = Environment(
        loader=ChoiceLoader([
            GithubTemplateLoader()
        ]))
    template = env.get_template('default-app.service')
    print(template.render())

    template = env.get_template('default-app.service')
    print(template.render())
