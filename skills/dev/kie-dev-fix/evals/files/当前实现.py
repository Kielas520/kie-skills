import json
import sys


def parse(lines):
    records = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        fields = {}
        for part in line.split():
            key, value = part.split("=")
            fields[key] = value
        records.append(fields)
    return records


def main():
    path = sys.argv[1]
    with open(path, encoding="utf-8") as handle:
        lines = handle.read().splitlines()
    print(json.dumps(parse(lines), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
