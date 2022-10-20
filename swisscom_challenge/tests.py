import redis
from app import APICaller
from decouple import config

docker_env = config("DOCKER_ENV", default=False, cast=bool)

redis_host = "localhost" if not docker_env else "redis-server"
r = redis.Redis(host=redis_host, port=6379, db=0)

# Clear all pre-existing keys
print("Flushing DB...")
r.flushdb()

print("Starting tests...")

if config("DOCKER_ENV", default=False, cast=bool):
    hosts = [
        "http://flask-app:5000/v1/group_one/",
        "http://flask-app:5000/v1/group_two/",
        "http://flask-app:5000/v1/group_three/"
    ]
else:
    hosts = [
        "http://localhost:5000/v1/group_one/",
        "http://localhost:5000/v1/group_two/",
        "http://localhost:5000/v1/group_three/"
    ]

api = APICaller()

partially_persisted = []
fully_persisted = []

print("Atempt to persist data in cluster for 20 groupId's...")
for num in range(1, 21):
    data = {"groupId": str(num)}
    if not api.create(data, hosts, url_suffix=None):
        partially_persisted.append(num)
    else:
        fully_persisted.append(num)

print("partially_persisted: ", partially_persisted)
print("fully_persisted: ", fully_persisted)

print("Any attemtpt to get an inconsistent group id should not succeed...")
for num in partially_persisted:
    for host in hosts:
        try:
            resp = api.get(host, str(num), url_suffix=None)
            if resp is not None:
                assert resp.status_code != 200, "Failure"
        except Exception:
            pass

print("No inconsistent ID was successfully retrieved")

print("Attemtps to get consistent group ids should EVENTUALLY succeed...")
consume_fully_persisted = fully_persisted.copy()
while True:
    for idx, num in enumerate(consume_fully_persisted):
        for host in hosts:
            try:
                resp = api.get(host, str(num), url_suffix=None)
                if resp.status_code == 200:
                    consume_fully_persisted.pop(idx)
            except Exception:
                pass
    print("Remainig ID's to retrieve: ", consume_fully_persisted)
    if not consume_fully_persisted:
        break

print("All fully consistent ID's successfully retrieved")
        

partially_deleted = []
print("Deleting all consistent group ids...")
# Atempt to delete all ID's that are consistent
for num in fully_persisted:
    data = {"groupId": str(num)}
    if not api.delete(data, hosts, url_suffix=None):
        partially_deleted.append(num)

print("All attempts to get any partially deleted ID's should fail...")
print("Partially deleted ids: ", partially_deleted)
for num in partially_deleted:
    for host in hosts:
        resp = api.get(host, str(num), url_suffix=None)
        if resp is not None:
            assert resp.status_code != 200, "This shouldn't happen."


print("Ensure all partially deleted ID's are EVENTUALLY removed from blacklist...")
print("Please wait, might take a while...")
consume_partially_deleted = partially_deleted.copy()
while True:
    if consume_partially_deleted:
        for idx, grp_id in enumerate(consume_partially_deleted):
            if not bytes(str(grp_id), encoding="utf8") in r.keys("*"):
                consume_partially_deleted.pop(idx)
    else:
        break

print("Done!")

# All inconsistent id's up for delete should EVENTUALLY be deleted across all hosts
# They wont be skipped this time during get requests, but the host servers shouldn't
# return a successful response
print("Attempting to get partially deleted id's...")
for i in range(4):  # lets try this 4 times just to be sure
    print("Attempt %i" % (i + 1,))
    for grp_id in partially_deleted:
        for host in hosts:
            try:
                resp = api.get(host, str(grp_id), url_suffix=None)
                assert resp is not None, "No GET request should be skipped"
                assert resp.status_code != 200, "All GET requests should fail"
            except Exception:
                pass

print("No partially deleted ID found on host servers...")
print("APPLICATION CONSISTENT ACROSS ALL NODES!")








