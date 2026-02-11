import redis
import time


class BattleEnv:
    def __init__(self, scenario_name="Battle_Test"):
        self.redis = redis.Redis(
            host="localhost",   # change if needed
            port=6380,          # your Redis Stack port docker is using
            db=0,
            decode_responses=True
        )
        self.key = f"scenario:{scenario_name}"
        self.state = None

    # ---------------------------
    # RESET ENVIRONMENT
    # ---------------------------
    def reset(self):
        self.state = self.redis.json().get(self.key)  #loads the scenario from redis and pulls it into the environment

        if not self.state:
            raise Exception(f"Scenario '{self.key}' not found in Redis.")

        print("Environment Reset.")
        return self.state

    # ---------------------------
    # STEP FUNCTION (RL STYLE)
    # ---------------------------
    def step(self, action):
        """
        Example action:
        {
            "type": "attack",
            "attacker": "E1",
            "target": "E2"
        }
        """

        if action["type"] == "attack":
            attacker = action["attacker"]
            target = action["target"]

            # Redis JSONPath returns a LIST
            hp_list = self.redis.json().get(
                self.key,
                f"$.entities.{target}.hp"
            )

            if not hp_list:
                print("Target not found.")
                return self.redis.json().get(self.key), 0, False

            hp = hp_list[0]

            if hp > 0:
                new_hp = max(0, hp - 10)

                self.redis.json().set(
                    self.key,
                    f"$.entities.{target}.hp",
                    new_hp
                )

                print(f"{attacker} attacked {target}. New HP: {new_hp}")

                reward = 10
                done = new_hp == 0

                return self.redis.json().get(self.key), reward, done

        return self.redis.json().get(self.key), 0, False


# -----------------------------------
# TEST RUN
# -----------------------------------
if __name__ == "__main__":

    env = BattleEnv("Battle_Test")

    state = env.reset()
    print("Initial State:")
    print(state)

    print("\nStarting Simulation...\n")

    for i in range(10):

        action = {
            "type": "attack",
            "attacker": "E1",
            "target": "E2"
        }

        state, reward, done = env.step(action)

        print("Reward:", reward)

        if done:
            print("Target Destroyed.")
            break

        time.sleep(1)

    print("\nFinal State in Redis:")
    print(env.redis.json().get("scenario:Battle_Test"))

