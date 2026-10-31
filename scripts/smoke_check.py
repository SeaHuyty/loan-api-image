"""Post-deploy check against the live API. Env: API_URL, API_KEY, EXPECTED_COMMIT."""
import json
import os
import sys
import time
import urllib.error
import urllib.request

API_URL = os.environ["API_URL"].rstrip("/")
API_KEY = os.environ["API_KEY"]
EXPECTED_COMMIT = os.environ["EXPECTED_COMMIT"]
DEADLINE = time.time() + 15 * 60  # free instances sleep and builds are slow


def call(method, path, token=None, body=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API_URL + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, None
    except (urllib.error.URLError, TimeoutError):
        return None, None


def fail(message):
    print(f"SMOKE TEST FAILED: {message}")
    sys.exit(1)


# 1. wait until the commit we just pushed is the one serving traffic and every dependency is up
while True:
    status, health = call("GET", "/health")
    if status == 200 and health["commit"] == EXPECTED_COMMIT:
        break
    if time.time() > DEADLINE:
        fail(f"/health never reported commit {EXPECTED_COMMIT[:7]} as healthy (last: {status} {health})")
    print(f"waiting for deploy... ({status} {health and health.get('commit')})")
    time.sleep(15)
print(f"live commit {health['commit'][:7]}, model {health['model_version']}")

# 2. the key is enforced
if call("GET", "/api/v1/applications")[0] != 401:
    fail("request without a key was not rejected")
if call("GET", "/api/v1/applications", token="wrong-key")[0] != 401:
    fail("request with a wrong key was not rejected")

# 3. a real application gets a real probability
status, app = call("POST", "/api/v1/applications", API_KEY,
                   {"borrower_id": 1042, "amount_usd": 1500, "term_months": 12})
if status != 201:
    fail(f"create application returned {status}")
status, pred = call("POST", f"/api/v1/applications/{app['id']}/predictions", API_KEY)
if status != 201 or not 0 <= pred["default_probability"] <= 1:
    fail(f"prediction returned {status} {pred}")
if pred["model_version"] != health["model_version"]:
    fail(f"prediction used {pred['model_version']}, health says {health['model_version']}")
print(f"OK: default_probability={pred['default_probability']}")
