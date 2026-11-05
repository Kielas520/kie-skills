"""把日志批次上传到采集服务。"""

import json
import time
import urllib.request

ENDPOINT = "https://collect.example.com/v1/logs"
RETRY_TIMES = 3


def build_request(batch: list[dict]) -> urllib.request.Request:
    data = json.dumps(batch).encode("utf-8")
    return urllib.request.Request(
        ENDPOINT, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )


def upload(batch: list[dict]) -> bool:
    """上传一批日志，失败时重试，返回是否成功。"""
    attempt = 0
    while attempt < RETRY_TIMES:
        try:
            with urllib.request.urlopen(build_request(batch), timeout=5) as resp:
                return resp.status == 200
        except Exception:
            attempt += 1
            time.sleep(2 ** attempt)
    return False


def main(path: str) -> int:
    with open(path, encoding="utf-8") as f:
        batch = [json.loads(line) for line in f if line.strip()]
    ok = upload(batch)
    print("uploaded" if ok else "failed")
    return 0
