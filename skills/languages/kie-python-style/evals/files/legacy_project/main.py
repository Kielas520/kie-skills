import sys
from pathlib import Path


def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    for path in sorted(root.glob("*.log")):
        print(path.name)


if __name__ == "__main__":
    main()
