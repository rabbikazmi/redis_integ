# redis_manager.py

import redis
from redis.commands.json.path import Path


class RedisScenarioManager:
    """
    Handles saving and loading Scenario objects to/from Redis.
    Does NOT modify structure.
    Works directly with Scenario.to_dict() output.
    """

    def __init__(self, host="localhost", port=6380, db=0):
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            decode_responses=True
        )

        try:
            self.client.ping()
            print("Connected to Redis.")
        except redis.ConnectionError:
            print("Redis connection failed.")
            raise

    # -------------------------------------------------
    # SAVE SCENARIO (without entities)
    # -------------------------------------------------
    def save_scenario(self, scenario):
        """
        Save Scenario object using scenario.to_dict()
        """
        key = f"scenario:{scenario.name}"
        data = scenario.to_dict()

        self.client.json().set(key, Path.root_path(), data)
        print(f"Scenario '{scenario.name}' saved to Redis.")

    # -------------------------------------------------
    # SAVE SCENARIO WITH ENTITIES
    # -------------------------------------------------
    def save_scenario_with_entities(self, scenario, entity_manager):
        """
        Save Scenario object including entities.
        """
        key = f"scenario:{scenario.name}"
        data = scenario.to_dict_with_entities(entity_manager)

        self.client.json().set(key, Path.root_path(), data)
        print(f"Scenario '{scenario.name}' (with entities) saved to Redis.")

    # -------------------------------------------------
    # LOAD SCENARIO (structure only)
    # -------------------------------------------------
    def load_scenario(self, scenario, scenario_name: str):
        """
        Load scenario data into existing Scenario object.
        """
        key = f"scenario:{scenario_name}"
        data = self.client.json().get(key)

        if not data:
            print("Scenario not found in Redis.")
            return False

        scenario.load_from_dict(data)
        print(f"Scenario '{scenario_name}' loaded into object.")
        return True

    # -------------------------------------------------
    # LOAD SCENARIO WITH ENTITIES
    # -------------------------------------------------
    def load_scenario_with_entities(self, scenario, scenario_name: str, entity_manager):
        """
        Load scenario including entities.
        """
        key = f"scenario:{scenario_name}"
        data = self.client.json().get(key)

        if not data:
            print("Scenario not found in Redis.")
            return False

        scenario.load_from_dict_with_entities(data, entity_manager)
        print(f"Scenario '{scenario_name}' loaded with entities.")
        return True

    # -------------------------------------------------
    # UPDATE ONLY ENTITY POSITION (Efficient for RL)
    # -------------------------------------------------
    def update_entity_position(self, scenario_name: str, entity_id: str, new_position_str: str):
        """
        Update entity position directly in Redis JSON.

        new_position_str format: "col,row"
        """
        key = f"scenario:{scenario_name}"
        path = Path(f".entity_positions.{entity_id}")

        self.client.json().set(key, path, new_position_str)
        print(f"Updated position for entity {entity_id}")

    # -------------------------------------------------
    # DELETE SCENARIO
    # -------------------------------------------------
    def delete_scenario(self, scenario_name: str):
        key = f"scenario:{scenario_name}"
        self.client.delete(key)
        print(f"Scenario '{scenario_name}' deleted.")

    # -------------------------------------------------
    # LIST ALL SCENARIOS
    # -------------------------------------------------
    def list_scenarios(self):
        return self.client.keys("scenario:*")
