import redis
import json

# Connect to Redis Stack (Docker)
r = redis.Redis(
    host="127.0.0.1",
    port=6380,          # IMPORTANT
    db=0,
    decode_responses=True
)

# Sanity check
print("PING:", r.ping())

# Test data
data = {
    "system": "DirectFire",
    "status": "working",
    "weapon": {
        "type": "MG",
        "accuracy": 0.65,
        "range": 1200
    },
    "target": {
        "side": "Red",
        "x": 150,
        "y": 200
    }
}

key = "directfire:test:1"

# Save JSON
r.execute_command(
    "JSON.SET",
    key,
    "$",
    json.dumps(data)
)

# Fetch JSON
result = r.execute_command(
    "JSON.GET",
    key
)

print("STORED JSON:")
print(result)
