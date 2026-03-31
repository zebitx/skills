"""Fetch interface definitions from Apifox API.

Usage: python3 fetch-api.py <token> <project_id> <identifier1> [identifier2 ...]

Each identifier is either:
  - A numeric string  → fetch by ID (GET /http-apis/{id})
  - A text string     → search by name (GET /http-apis?keywords={name})

Outputs (one per line, then RESULTS: last):
  NOT_FOUND_ID:{id}              — numeric ID returned empty data
  NOT_FOUND_NAME:{name}          — name search returned 0 results
  MULTIPLE:{name}:[{...}, ...]   — name search returned >1 results (JSON array)
  HTTP_ERROR:{code}:{url}        — HTTP error from Apifox API
  RESULTS:[{...}, ...]           — JSON array of fetched interface objects
"""
import urllib.request, urllib.error, urllib.parse, json, sys

token = sys.argv[1]
project_id = sys.argv[2]
identifiers = sys.argv[3:]

BASE = "https://api.apifox.com/v1"
HEADERS = {
    "Authorization": f"Bearer {token}",
    "X-Apifox-Api-Version": "2024-03-28"
}


def api_get(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"HTTP_ERROR:{e.code}:{url}")
        return None


results = []
for ident in identifiers:
    if str(ident).isdigit():
        data = api_get(f"{BASE}/projects/{project_id}/http-apis/{ident}")
        if data is None:
            continue
        api = data.get("data", {})
        if api:
            results.append(api)
        else:
            print(f"NOT_FOUND_ID:{ident}")
    else:
        encoded = urllib.parse.quote(str(ident))
        data = api_get(f"{BASE}/projects/{project_id}/http-apis?keywords={encoded}")
        if data is None:
            continue
        items = data.get("data", {}).get("items", [])
        if len(items) == 0:
            print(f"NOT_FOUND_NAME:{ident}")
        elif len(items) == 1:
            results.append(items[0])
        else:
            candidates = [
                {"id": i["id"], "name": i.get("name", ""), "method": i.get("method", ""), "path": i.get("path", "")}
                for i in items
            ]
            print(f"MULTIPLE:{ident}:" + json.dumps(candidates, ensure_ascii=False))

print("RESULTS:" + json.dumps(results, ensure_ascii=False))
