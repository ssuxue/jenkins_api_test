# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import argparse
import json
import logging
import sys
from enum import IntEnum
from typing import Dict, Any, Optional, Union
from urllib import request, error


class PerformType(IntEnum):
    cancel_actions = 1
    rerun_failed_jobs = 2
    rerun_failed_jobs_code = 3


class GheRepo:
    def __init__(self, base, token):
        self.token = token
        self.base = base

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
        except json.decoder.JSONDecodeError:
            return content

        return response

    def post(self, url: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._request(self.base + url, data, method="POST")

    def get_json_list(self, url: str) -> Any:
        url = self.base + url
        logging.info(f"Requesting GET to {url}")
        req = request.Request(url, headers=self.headers())

        with request.urlopen(req) as response:
            data = response.read().decode("UTF-8")
        return data

    def get(self, url: str) -> Dict[str, Any]:
        url = self.base + url
        print(url)
        logging.info(f"Requesting GET to {url}")
        req = request.Request(url, headers=self.headers())
        with request.urlopen(req) as response:
            print(response)
            response = json.loads(response.read())
        return response


def cancel_workflow(api: GheRepo, run_id: int):
    try:
        api.post(f"actions/runs/{run_id}/cancel")
    except KeyboardInterrupt:
        sys.exit()
    except (RuntimeError, error.HTTPError) as e:
        print(f"Failed to cancel workflow: {e}")


def rerun_failed_jobs(api: GheRepo, run_id: int):
    try:
        api.post(f"actions/runs/{run_id}/rerun-failed-jobs")
    except KeyboardInterrupt:
        sys.exit()
    except (RuntimeError, error.HTTPError) as e:
        print(f"Failed to rerun failed jobs: {e}")


def rerun(api: GheRepo, rid: int, err_code: Union[int, str]):
    # res = api.get(f"actions/runs/{rid}/jobs")
    # res = json.dumps(res)
    # res = res.replace("'", '"')
    jobs = res["jobs"]
    ids = []

    for job in jobs:
        if job["status"] == "completed" and job["conclusion"] == "failure":
            ids.append(job["id"])
    print(ids)

    for jid in ids:
        print(f"id -> {jid}")
        log = api.get_json_list(f"actions/jobs/{jid}/logs")
        if f"Process completed with exit code {err_code}" in log:
            rerun_failed_jobs(api, rid)
            break


def get_parse():
    desc = "Send token to api to perform workflow"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("--token", help="Github token")
    parser.add_argument("--rid", help="The unique identifier of the workflow run")
    parser.add_argument("--code", help="Error exit code")
    parser.add_argument("--url", help="The url of repo")
    parser.add_argument("--type", type=int, default=1, help="Type of operation to be performed")
    args = parser.parse_args()
    return args


def main():
    args = get_parse()
    api = GheRepo(args.url, token=args.token)
    if args.type == PerformType.cancel_actions.value:
        cancel_workflow(api, args.rid)
    elif args.type == PerformType.rerun_failed_jobs.value:
        rerun_failed_jobs(api, args.rid)
    elif args.type == PerformType.rerun_failed_jobs_code.value:
        rerun(api, args.rid, args.code)
    else:
        logging.info("No operation was performed.")


if __name__ == "__main__":
    main()
