import os
import logging
from typing import List, Optional, Union

logging.basicConfig(level=logging.INFO)


def collect_logs(root: Optional[str], suffix: str) -> Union[List[str], None]:
    if root is None:
        logging.warning("no root given")
        return None
    found = []
    for name in os.listdir(root):
        if name.endswith(suffix):
            found.append(os.path.join(root, name))
    return found


def size_of(path: str) -> int:
    return os.path.getsize(path)


def main() -> None:
    files = collect_logs(os.getcwd(), ".log")
    logging.info("found %s files", len(files or []))
    for item in files or []:
        logging.info("%s %s bytes", item, size_of(item))


if __name__ == "__main__":
    main()
