import logging
from typing import List

from src.testing import ScenarioRunner

logger = logging.getLogger()


class TestRunner:
    def __init__(self, submission_id: int, scenarios: List[dict], host_address: str = "127.0.0.1"):
        self.host_address = host_address
        self.submission_id = submission_id
        self.scenarios = scenarios
        self.scenario_runners = []
        self.result_data = []
        self.data = []

    def run(self):
        logger.info("Test running")
        for scenario_dict in self.scenarios:
            scenario_runner = ScenarioRunner(
                scenario_dict=scenario_dict,
                host_address=self.host_address
            )
            self.scenario_runners.append(scenario_runner)
            scenario_runner.run()

    def create_result_data(self):
        for sc_runner in self.scenario_runners:
            print(sc_runner.return_data)
