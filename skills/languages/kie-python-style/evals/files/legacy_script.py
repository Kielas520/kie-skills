from __future__ import annotations

import os
import logging
from typing import Dict, Iterable, List, Optional, Union

logging.basicConfig(level=logging.INFO)


def parse_entry(line: str) -> tuple:
    key, value = line.split("=", 1)
    return (key, value)


def collect_logs(root: Optional[str], suffix: str) -> Union[Dict[str, int], None]:
    if root is None:
        logging.warning("no root given")
        return None
    sizes = {}
    for name in os.listdir(root):
        if name.endswith(suffix):
            sizes[name] = os.path.getsize(os.path.join(root, name))
    return sizes


def summarize(entries: Iterable[str]) -> Dict[str, int]:
    counts = {}
    for entry in entries:
        key, value = parse_entry(entry)
        counts[key] = counts.get(key, 0) + 1
    return counts


def main() -> None:
    sizes = collect_logs(os.getcwd(), ".log")
    logging.info("found %s files", len(sizes or {}))
    for name, size in (sizes or {}).items():
        logging.info("%s %s bytes", name, size)
    logging.info("summaries: %s", summarize(["a=1", "a=2", "b=3"]))


if __name__ == "__main__":
    main()
