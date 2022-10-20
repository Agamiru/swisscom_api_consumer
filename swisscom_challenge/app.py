from celery import Celery
import requests
import redis
from typing import Optional, List
from decouple import config

docker_env = config("DOCKER_ENV", default=False, cast=bool)

redis_host = "localhost" if not docker_env else "redis-server"

r = redis.Redis(host=redis_host, port=6379, db=0)

app = Celery("app", broker=f"redis://{redis_host}:6379/0")


app.conf.beat_schedule = {
    'delete_every_ten_seconds': {
        'task': 'app.delete_task',
        'schedule': 10
    },
}

HOSTS = [
    'http://node01.app.internal.com',
    'http://node02.app.internal.com',
    'http://node03.app.internal.com',
]

# set low, so test host servers can easily mimic timeout errors
TIMEOUT = 2


# our connector class
class APICaller:

    def __init__(self) -> None:
        headers = { "accept": "application/json" }
        self.req_params = {
            "headers": headers, "timeout": TIMEOUT,
        }

    def create(self, data: dict, hosts=HOSTS, url_suffix = "/v1/group/") -> bool:
        """Create group data"""

        return self.fire_group_request(data, 201, "post", hosts, url_suffix)

    def delete(self, data: dict, hosts=HOSTS, url_suffix = "/v1/group/") -> bool:
        """Delete group data"""

        return self.fire_group_request(data, 200, "delete", hosts, url_suffix)

    def get(self, host: str, grp_id: str, url_suffix = "/v1/group/") -> Optional[requests.Response]:
        """Retrieve item if groupId not in 'blacklisted' keys set for deletion"""

        if not bytes(grp_id, encoding="utf8") in r.keys("*"):
            url = f"{host}{grp_id}/" if url_suffix is None else host + f"{url_suffix}{grp_id}/"
            return requests.get(url, self.req_params)
        # Ideally, in a web application, the response of this call could
        # be a 404 (NotFound), but for simplicity sakes we use this. 
        print(f"Skipping get request for group id: {grp_id} and host: {host}")

    def fire_group_request(
        self, data: dict, status_check: int, method: str,
        hosts: List[str], url_suffix: Optional[str] = None
    ) -> bool:
        """Method to create or delete group items"""

        grp_id: str = data["groupId"]
        # to avoid possible unique key integrity errors 
        if grp_id in r.keys("*"):
            print("Key already up for delete")
            return False

        clean_up_hosts = []
        clean_up = False
        for host in hosts:
            try:
                url = host if url_suffix is None else host + url_suffix
                resp = getattr(requests, method)(url, json=data, **self.req_params)
                if resp.status_code != status_check:
                    # Delete requests are expected to be idempotent, so even
                    # non existing group id's should not return unsuccessful.
                    # As a result, it is safe to assume all unsuccessful requests
                    # persisted data on the remote server, warranting a clean up.
                    clean_up_hosts.append(host)
                    clean_up = True
                    break
            except requests.Timeout:
                # If timeout occurs during read from the host server, data will 
                # already have been persisted, so clean up.
                print(f"{method.upper()} request timed out for group id: {grp_id}")
                clean_up_hosts.append(host)
                clean_up = True
                break
            
            clean_up_hosts.append(host)

        # check to know if all requests were successful
        if clean_up:
            self.set_for_clean_up(grp_id, clean_up_hosts)
            return False
        else:
            return True

    def set_for_clean_up(self, group_id: str, hosts: List[str]):
        """
        Redis is used to persist group id's and hosts that are up for deletion.
        They will also be used in retrieving items.    
        """
        for host in hosts:
            r.lpush(group_id, host)



def is_integer(v) -> bool:
    """
    Keys used for this app are integers. Celery stores a couple of non-integer
    keys in redis by default, this function helps us exclude them.
    """
    try:
        int(v)
        return True
    except Exception:
        return False



@app.task
def delete_task():
    """
    Task to periodically delete all inconsistent group_ids
    from their respective hosts.
    """
    headers = { "accept": "application/json" }
    req_params = {
        "headers": headers, "timeout": TIMEOUT,
    }

    for grp_id in r.keys("*"):
        if is_integer(grp_id):
            str_grp_id = str(int(grp_id))
            if r.llen(grp_id) != 0:
                for host in r.lrange(grp_id, 0, -1):
                    host = str(host, encoding="utf8")
                    try:
                        data = {"groupId": str_grp_id}
                        resp = requests.delete(host, json=data, **req_params)
                        if resp.status_code != 200:
                            # allow task progress
                            continue
                    except Exception:
                        # allow task progress
                        continue
                    
                    # remove host from list
                    r.lrem(grp_id, 0, host)
                    if r.llen(grp_id) == 0:
                        r.delete(grp_id)
            else:
                # remove key
                r.delete(grp_id)

