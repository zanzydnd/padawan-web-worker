from typing import List


def set_all_steps_failed_with_message(scenarios: List[dict], submission_id: int, message: str):
    data = {}
    for scenario in scenarios:
        data[scenario.get("id")] = {
            test.get("name"): message
            for test in scenario.get("tests")
        }

    return {
        "submission_id": submission_id,
        "scenarios": data
    }
