"""Upload a locally generated OpenAPI spec to Apifox.

Usage:
  python3 sync-upload.py <project_name> <project_id> <module_id|null> <folder_id|null> <overwrite> <token>

Arguments:
  project_name   — used to locate /tmp/apifox-client-sync-{name}.json
  project_id     — Apifox project ID
  module_id      — Apifox module ID, or the string "null" to omit
  folder_id      — Apifox folder ID, or the string "null" to omit
  overwrite      — one of: OVERWRITE_EXISTING AUTO_MERGE KEEP_EXISTING CREATE_NEW
  token          — Apifox access token

Outputs:
  SPEC_NOT_FOUND:{path}  — spec file not found (Step 3 did not produce output)
  {raw API response}     — Apifox response JSON
  SYNC_ERROR:{path}      — upload failed; temp file preserved for inspection
"""
import json, subprocess, os, sys

project_name = sys.argv[1]
project_id = sys.argv[2]
module_id = None if sys.argv[3] == "null" else sys.argv[3]
folder_id = None if sys.argv[4] == "null" else sys.argv[4]
overwrite = sys.argv[5]
token = sys.argv[6]

spec_file = f"/tmp/apifox-client-sync-{project_name}.json"

if not os.path.exists(spec_file):
    print(f"SPEC_NOT_FOUND:{spec_file} Step 3 未生成 spec 文件，请检查源码扫描步骤")
    sys.exit(0)

spec = open(spec_file).read()

payload = {
    "input": spec,
    "options": {
        "endpointOverwriteBehavior": overwrite,
        "schemaOverwriteBehavior": "OVERWRITE_EXISTING",
        "updateFolderOfChangedEndpoint": False
    }
}
if module_id is not None:
    payload["options"]["moduleId"] = module_id
if folder_id is not None:
    payload["options"]["targetEndpointFolderId"] = folder_id

result = subprocess.run([
    "curl", "-s", "-X", "POST",
    f"https://api.apifox.com/v1/projects/{project_id}/import-openapi",
    "-H", f"Authorization: Bearer {token}",
    "-H", "X-Apifox-Api-Version: 2024-03-28",
    "-H", "Content-Type: application/json",
    "-d", json.dumps(payload)
], capture_output=True, text=True)

response_text = result.stdout
print(response_text)

try:
    resp = json.loads(response_text)
    if resp.get("success") is False or "error" in resp:
        print(f"SYNC_ERROR:{spec_file} 保留临时文件供排查")
    else:
        os.remove(spec_file)
except (json.JSONDecodeError, Exception):
    print(f"SYNC_ERROR:{spec_file} 无法解析响应，保留临时文件供排查")
