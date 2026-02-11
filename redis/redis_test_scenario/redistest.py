# redistest.py

import redis


class RedisScenarioTester:
    def __init__(self, host="localhost", port=6380, db=0):
        self.client = redis.Redis(
            host="localhost",
            port=6380,   # Use the Docker port here
            db=db,
            decode_responses=True
        )

    def write_to_redis(self, scenario_name: str, scenario_dict: dict):
        key = f"scenario:{scenario_name}"
        self.client.json().set(key, "$", scenario_dict)
        print(f"Scenario '{scenario_name}' written to Redis as JSON.")

    def read_from_redis(self, scenario_name: str):
        key = f"scenario:{scenario_name}"
        data = self.client.json().get(key)

        if data:
            print(f"Scenario '{scenario_name}' read from Redis.")
            return data
        else:
            print("Scenario not found in Redis.")
            return None
