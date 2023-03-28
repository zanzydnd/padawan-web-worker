import datetime
import json
import logging
import re
from typing import List

import requests
from requests import Request

from src.core.exceptions import ValidatorWentWrongException

logger = logging.getLogger()


class ScenarioRunner:
    def __init__(self, scenario_dict: dict, host_address: str = None):
        self.return_data = {}
        self.data_container = {}
        self.scenario_dict = scenario_dict
        self.host_address = host_address or "127.0.0.1"

    def render_template(self, str_from_template: str) -> str:
        result = str_from_template
        for template_var_usage in re.findall("\${.*}\$", str_from_template):
            ref_test_name, test_subject, test_subject_key = template_var_usage.strip("${").strip("}$").split(":")
            to_insert = self.data_container.get(ref_test_name).get(test_subject).get(test_subject_key)
            result = result.replace(template_var_usage, str(to_insert))
        return result

    def make_request_url(self, test_url: str) -> str:
        return f"http://{self.host_address}:8002{self.render_template(test_url)}"

    def make_step_headers(self, test_headers: str) -> dict:
        headers_dict = json.loads(test_headers)
        result = {}
        for key in headers_dict.keys():
            result[self.render_template(key)] = self.render_template(headers_dict.get(key))

        result["Content-Type"] = result["Content-Type"] + "; charset=utf-8"
        return result

    def make_test_body(self, body_str: str) -> str:
        return self.render_template(body_str)

    def _process_validator(self, response: requests.Response, test: dict, duration: datetime.timedelta):
        self.return_data[test.get("name")] = []
        print(self.return_data[test.get("name")])
        for validator in test.get("validators"):
            for key in validator.keys():
                if key == "allowed_response_statuses" and validator.get(key):
                    if response.status_code not in validator.get(key):
                        self.return_data[test.get("name")].append(
                            {
                                "validator": "allowed_response_statuses",
                                "status": response.status_code,
                                "headers": dict(response.headers),
                                "body": response.json() if response.text else "Нет тела.",
                                "message": f"Недопустимый статус ответа. Статус: {response.status_code}. Допустимые: {validator.get(key)}",
                            }
                        )
                        raise ValidatorWentWrongException()
                if key == "expected_response_body" and validator.get(key):
                    rendered_expected = self.render_template(validator.get(key))
                    if response.json() != json.loads(rendered_expected):
                        self.return_data[test.get("name")].append(
                            {
                                "validator": "expected_response_body",
                                "status": response.status_code,
                                "headers": dict(response.headers),
                                "body": response.json() if response.text else "Нет тела.",
                                "message": f"Несовпадение. Вернувшийся результат: {response.json()}. Ожидаемый: {json.loads(rendered_expected)}",
                            }
                        )
                        raise ValidatorWentWrongException()
                if key == "timeout" and validator.get(key):
                    if duration.seconds > validator.get(key):
                        self.return_data[test.get("name")].append(
                            {
                                "validator": "timeout",
                                "status": response.status_code,
                                "headers": dict(response.headers),
                                "body": response.json() if response.text else "Нет тела.",
                                "message": f"Timeout. Ваше время: {duration.seconds}c. Ожидаемое время: {validator.get(key)}с.",
                            }
                        )
                        raise ValidatorWentWrongException()

    def process_response(self, response: requests.Response, test: dict,
                         duration: datetime.timedelta = datetime.timedelta(seconds=0)):
        self.data_container[test.get("name")] = {
            "Response": response.json() if response.text else {},
            "Headers": response.headers,
        }
        self._process_validator(response,test,duration)

    def run(self):
        logger.info(f"Running scenario: {self.scenario_dict}")
        session = requests.Session()
        for i, test_dict in enumerate(self.scenario_dict.get("tests")):
            print(test_dict.get("name"))
            request_obj = Request(
                method=test_dict.get("method"),
                url=self.make_request_url(test_dict.get("url")),
                data=self.make_test_body(test_dict.get("body")).encode("utf-8"),
                headers=self.make_step_headers(test_dict.get("headers"))
            )

            prepared_request = request_obj.prepare()
            start_time = datetime.datetime.now()
            response = session.send(prepared_request)
            end_time = datetime.datetime.now()

            try:
                self.process_response(response, test_dict, end_time - start_time)
            except ValidatorWentWrongException as v_w_e:
                for j in range(i + 1, len(self.scenario_dict.get("tests"))):
                    self.return_data[self.scenario_dict.get("tests")[j].get("name")] = "-"
                return
# TODO: последний шаг(последний параметр - сделать бесконечную вложенность)
