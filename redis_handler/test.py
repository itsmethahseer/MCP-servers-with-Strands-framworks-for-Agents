import redis
import json

r = redis.Redis(host="redis", port=6379, decode_responses=True)

# Save dummy data
r.set("callmap:test456", json.dumps({"hello": "world"}), ex=300)

# Retrieve it
value = r.get("callmap:test456")
print(value)

# Delete using GETDEL
deleted = r.execute_command("GETDEL", "callmap:test456")
print("Deleted:", deleted)