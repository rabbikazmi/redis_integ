# main_test.py

from scenario_gen import FakeScenario, FakeEntityManager
from redistest import RedisScenarioTester


def main():
    # STEP 1️ Generate Scenario
    scenario = FakeScenario("Battle_Test")
    entity_manager = FakeEntityManager()

    scenario_data = scenario.to_dict_with_entities(entity_manager)
    print("Scenario Generated:")
    print(scenario_data)

    # STEP 2️ Write to Redis
    redis_mgr = RedisScenarioTester()
    redis_mgr.write_to_redis(scenario.name, scenario_data)

    # STEP 3 Read from Redis
    loaded_data = redis_mgr.read_from_redis(scenario.name)

    # STEP 4️ Confirm Data Integrity
    if loaded_data:
        print("\nLoaded Data:")
        print(loaded_data)

        if loaded_data == scenario_data:
            print("\nSUCCESS: Data matches!")
        else:
            print("\nWARNING: Data mismatch!")


if __name__ == "__main__":
    main()
