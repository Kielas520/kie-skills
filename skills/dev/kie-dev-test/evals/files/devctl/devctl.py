import sys
from pathlib import Path

PORT = Path("/dev/ttyUSB0")


def read_version(port: Path) -> str:
    with port.open("rb+", buffering=0) as handle:
        handle.write(b"VER?\n")
        reply = handle.readline().decode("ascii", errors="replace").strip()
    if not reply.startswith("VER "):
        raise RuntimeError(f"unexpected reply: {reply!r}")
    return reply.removeprefix("VER ")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] != "version":
        print("usage: devctl.py version", file=sys.stderr)
        return 2
    print(read_version(PORT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
