import redis
import random
import time

# Connect to Redis
r = redis.Redis(host='localhost', port=6380, decode_responses=True)
r.flushall() # Start fresh for the demo

states = ["bridge_crossing", "forest_ambush", "urban_assault", "base_defense"]
actions = ["attack", "retreat", "flank", "hold_position"]

print("⚔️ WARGAME SIMULATION STARTED...")

try:
    while True:
        # 1. Pick a scenario
        current_state = random.choice(states)
        
        # 2. Tell Redis/Monitor where the agent is
        r.set("active_state", current_state)
        
        # 3. Simulate learning (Update Q-values)
        action = random.choice(actions)
        # We simulate a "learned" value between -1.0 and 1.0
        q_value = round(random.uniform(-1, 1), 2)
        
        # HSET into the Q-Table
        r.hset(f"q_table:{current_state}", action, q_value)
        
        print(f"Update: {current_state} -> {action}: {q_value}")
        time.sleep(1.0) # Speed of the simulation

except KeyboardInterrupt:
    print("\nSimulation Halted.")