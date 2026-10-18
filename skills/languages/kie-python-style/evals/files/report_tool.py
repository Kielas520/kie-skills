import os
from typing import Dict, Optional


def load_config(path: str) -> Dict[str, str]:
    config = {}
    with open(os.path.join(path, "config.ini"), encoding="utf-8") as handle:
        for line in handle:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                config[key] = value
    return config


def find_reports(root: Optional[str]) -> list:
    if root is None:
        return []
    return [name for name in os.listdir(root) if name.endswith(".csv")]
