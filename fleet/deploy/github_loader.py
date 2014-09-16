from jinja2 import BaseLoader, TemplateNotFound, Environment, PrefixLoader
import requests

import base64


class InvalidCredentials(Exception):
    pass


class GithubTemplateLoader(BaseLoader):
    """
    Jinja2 template loader using github API.
    """

    def __init__(self, token=None):
        """
        Constructor
        :param token: Option token used for connecting to repositories. If None
            no token will be passed.
        :type token: str
        """
        self.token = token
        self.auth = (self.token, 'x-oauth-basic') if self.token else None

    def _github_fetch(self, template_path, owner, repo, path, ref):
        path_params = {
            'owner': owner,
            'repo': repo,
            'path': path
        }
        query_params = {
            'ref': ref
        }
        resp = requests.get(
            'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
            .format(**path_params), params=query_params, auth=self.auth)
        if resp.status_code == 404:
            raise TemplateNotFound(template_path)
        elif resp.status_code == 401:
            raise InvalidCredentials()
        elif resp.status_code != 200:
            raise RuntimeError('Unknown exception happened while '
                               'calling github. Message: %s' % resp.text)
        return resp.json()

    def _github_sha(self, owner, repo, path, ref):
        path_params = {
            'owner': owner,
            'repo': repo,
        }
        query_params = {
            'path': path,
            'sha': ref
        }
        resp = requests.get(
            'https://api.github.com/repos/{owner}/{repo}/commits'
            .format(**path_params), params=query_params, auth=self.auth)
        if resp.status_code != 200:
            return None
        else:
            return resp.json()[0][u'sha']

    def get_source(self, environment, template_path):
        git_split = template_path.split(':')
        if len(git_split) <= 3:
            raise ValueError('Template path(%s) is invalid. Expecting path to '
                             'use format: {owner}:{repo}:{path}:{ref} %d'
                             % template_path)
        owner, repo, path, ref = git_split
        sha = self._github_sha(owner, repo, path, ref)
        github_data = self._github_fetch(template_path, owner, repo, path, sha)
        contents = base64.decodestring(github_data[u'content'])

        def uptodate():
            return sha == self._github_sha(owner, repo, path, ref)
        return contents, None, uptodate


if __name__ == "__main__":
    env = Environment(
        loader=PrefixLoader({
            'github': GithubTemplateLoader()
        }, delimiter='>'))
    template = env.get_template(
        'github>totem:fleet-templates:templates/default-app.service:master')
    print(template.render())

    template = env.get_template(
        'github>totem:fleet-templates:templates/default-app.service:master')
    print(template.render())
