# scenario_generator.py

class FakeEntityManager:
    def __init__(self):
        self.entities = {
            "E1": {"name": "Tank", "hp": 100},
            "E2": {"name": "Infantry", "hp": 50}
        }

    def get_entities(self):
        return self.entities


class FakeScenario:
    def __init__(self, name="Default"):
        self.name = name

    def to_dict_with_entities(self, entity_manager):
        return {
            "name": self.name,
            "zones": {
                "zone1": {"type": "control", "value": 10}
            },
            "paths": {},
            "entity_positions": {
                "E1": "3,4",
                "E2": "5,6"
            },
            "entities": entity_manager.get_entities()
        }
