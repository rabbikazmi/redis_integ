import redis

r = redis.Redis(host="127.0.0.1", port=6380, decode_responses=True)

print("PING:", r.ping())
print("MODULES:", r.execute_command("MODULE", "LIST"))

