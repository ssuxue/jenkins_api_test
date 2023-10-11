# -*- encoding: utf-8 -*-
"""
@version 1.0
@Description
@Author Chase
@Date 2023/10/11 23:19
"""
import argparse
import json
import logging
import sys
from typing import Dict, Any, Optional
from urllib import request, error


class GitHubRepo:

    def __init__(self, user, repo, token):
        self.token = token
        self.user = user
        self.repo = repo
        self.base = f"https://api.github.com/repos/{user}/{repo}/"

    def headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
        }

    def _request(self, full_url: str, body: Dict[str, Any], method: str) -> Dict[str, Any]:
        logging.info(f"Requesting {method} to {full_url} with {body}")
        req = request.Request(full_url, headers=self.headers(), method=method.upper())
        req.add_header("Content-Type", "application/json; charset=utf-8")
        data = json.dumps(body)
        data = data.encode("utf-8")
        req.add_header("Content-Length", str(data))

        try:
            with request.urlopen(req, data) as response:
                content = response.read()
        except error.HTTPError as e:
            msg = str(e)
            error_data = e.read().decode()
            raise RuntimeError(f"Error response: {msg}\n{error_data}")

        logging.info(f"Got response from {full_url}: {content}")
        try:
            response = json.loads(content)
        except json.decoder.JSONDecodeError as e:
            return content

        return response

    def post(self, url: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._request(self.base + url, data, method="POST")


def cancel_workflow(run_id: int, token: str):
    api = GitHubRepo("ssuxue", "jenkins_api_test", token=token)

    try:
        api.post(f"actions/runs/{run_id}/cancel")
    except KeyboardInterrupt:
        sys.exit()
    except (RuntimeError, error.HTTPError) as e:
        # Catch any exception so other reviewers can be processed
        print(f"Failed to cancel workflow: {e}")


def get_parse():
    desc = "Send token to api to perform workflow"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("--token", help="github token")
    parser.add_argument("--rid", help="The unique identifier of the workflow run")
    args = parser.parse_args()
    return args


def main():
    args = get_parse()
    cancel_workflow(args.rid, args.token)


if __name__ == '__main__':
    main()
